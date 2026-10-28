"""Gerencia os atendimentos salvos no banco de dados SQLite."""

import json
import sqlite3

from datetime import datetime, timedelta, timezone
from pathlib import Path
from threading import Lock

from .config import BANCO_DADOS, PASTA_DADOS, TEMPO_EXPIRACAO_HORAS


class Repositorio:
    """Realiza as operações de criação, consulta e exclusão de atendimentos."""

    def __init__(self):
        # Evita conflitos quando duas operações acontecem ao mesmo tempo.
        self._trava = Lock()

        # Cria a pasta do banco de dados, caso ela ainda não exista.
        PASTA_DADOS.mkdir(parents=True, exist_ok=True)

        # Cria a tabela na primeira execução.
        self._criar_tabela()

    def _conectar(self):
        """Abre uma conexão com o banco de dados."""

        conexao = sqlite3.connect(BANCO_DADOS)

        # Permite acessar as colunas pelo nome, além de pela posição.
        conexao.row_factory = sqlite3.Row

        return conexao

    def _criar_tabela(self):
        """Cria a tabela de atendimentos se ela ainda não existir."""

        with self._conectar() as conexao:
            conexao.execute("""
                CREATE TABLE IF NOT EXISTS atendimentos (
                    numero INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT NOT NULL,
                    escolhas TEXT NOT NULL,
                    estado TEXT NOT NULL,
                    outra_preferencia TEXT NOT NULL DEFAULT '',
                    ajuda_comunicacao TEXT NOT NULL DEFAULT '',
                    criado_em TEXT NOT NULL,
                    ia_status TEXT NOT NULL DEFAULT 'pendente',
                    orientacoes TEXT NOT NULL DEFAULT '[]',
                    ia_erro TEXT NOT NULL DEFAULT ''
                )
            """)

    def _limpar_expirados(self, conexao):
        """Remove atendimentos que ultrapassaram o tempo permitido."""

        limite = datetime.now(timezone.utc) - timedelta(
            hours=TEMPO_EXPIRACAO_HORAS
        )

        conexao.execute(
            "DELETE FROM atendimentos WHERE criado_em <= ?",
            (limite.isoformat(),)
        )

    @staticmethod
    def _publico(registro):
        """Converte um registro do banco para um dicionário utilizável."""

        if registro is None:
            return None

        atendimento = dict(registro)

        # Converte os campos JSON para listas ou outros dados Python.
        atendimento["escolhas"] = json.loads(atendimento["escolhas"])
        atendimento["orientacoes"] = json.loads(
            atendimento["orientacoes"]
        )

        # A data de criação continua no banco, mas não é enviada ao frontend.
        atendimento.pop("criado_em", None)

        return atendimento

    def criar(self, dados):
        """Salva um novo atendimento e devolve os dados registrados."""

        agora = datetime.now(timezone.utc).isoformat()

        with self._trava:
            with self._conectar() as conexao:
                self._limpar_expirados(conexao)

                cursor = conexao.execute("""
                    INSERT INTO atendimentos (
                        nome,
                        escolhas,
                        estado,
                        outra_preferencia,
                        ajuda_comunicacao,
                        criado_em,
                        ia_status,
                        orientacoes,
                        ia_erro
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    dados["nome"],
                    json.dumps(dados["escolhas"], ensure_ascii=False),
                    dados["estado"],
                    dados.get("outra_preferencia", ""),
                    dados.get("ajuda_comunicacao", ""),
                    agora,
                    "pendente",
                    "[]",
                    ""
                ))

                numero = cursor.lastrowid

                registro = conexao.execute(
                    "SELECT * FROM atendimentos WHERE numero = ?",
                    (numero,)
                ).fetchone()

                return self._publico(registro)

    def listar(self):
        """Retorna os atendimentos do mais recente para o mais antigo."""

        with self._trava:
            with self._conectar() as conexao:
                self._limpar_expirados(conexao)

                registros = conexao.execute("""
                    SELECT *
                    FROM atendimentos
                    ORDER BY numero DESC
                """).fetchall()

                return [
                    self._publico(registro)
                    for registro in registros
                ]

    def iniciar_ia(self, numero):
        """Marca um atendimento para iniciar a geração das orientações."""

        with self._trava:
            with self._conectar() as conexao:
                self._limpar_expirados(conexao)

                registro = conexao.execute(
                    "SELECT * FROM atendimentos WHERE numero = ?",
                    (numero,)
                ).fetchone()

                if registro is None:
                    raise KeyError(numero)

                atendimento = self._publico(registro)

                # Evita iniciar novamente uma geração já em andamento
                # ou que já tenha sido concluída.
                if atendimento["ia_status"] in ("gerando", "concluida"):
                    return atendimento, False

                conexao.execute("""
                    UPDATE atendimentos
                    SET ia_status = ?, ia_erro = ?
                    WHERE numero = ?
                """, ("gerando", "", numero))

                registro = conexao.execute(
                    "SELECT * FROM atendimentos WHERE numero = ?",
                    (numero,)
                ).fetchone()

                return self._publico(registro), True

    def terminar_ia(self, numero, orientacoes=None, erro=""):
        """Salva as orientações geradas pela IA ou registra um erro."""

        status = "erro" if erro else "concluida"

        with self._trava:
            with self._conectar() as conexao:
                self._limpar_expirados(conexao)

                conexao.execute("""
                    UPDATE atendimentos
                    SET ia_status = ?,
                        orientacoes = ?,
                        ia_erro = ?
                    WHERE numero = ?
                """, (
                    status,
                    json.dumps(
                        orientacoes or [],
                        ensure_ascii=False
                    ),
                    erro,
                    numero
                ))

                registro = conexao.execute(
                    "SELECT * FROM atendimentos WHERE numero = ?",
                    (numero,)
                ).fetchone()

                return self._publico(registro)

    def excluir(self, numero):
        """Exclui um atendimento pelo número."""

        with self._trava:
            with self._conectar() as conexao:
                self._limpar_expirados(conexao)

                cursor = conexao.execute(
                    "DELETE FROM atendimentos WHERE numero = ?",
                    (numero,)
                )

                return cursor.rowcount > 0