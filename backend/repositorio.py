"""Armazenamento temporário em memória. Não cria banco nem arquivos com dados pessoais."""
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from threading import Lock
from .config import TEMPO_EXPIRACAO_HORAS


class Repositorio:
    def __init__(self):
        self._registros = {}
        self._proximo_numero = 1
        # O servidor atende em várias threads. A trava protege alterações simultâneas.
        self._trava = Lock()

    def _limpar_expirados(self):
        limite = datetime.now(timezone.utc) - timedelta(hours=TEMPO_EXPIRACAO_HORAS)
        self._registros = {n: a for n, a in self._registros.items() if a["criado_em"] > limite}

    @staticmethod
    def _publico(registro):
        # Uma cópia evita que outra parte do código altere o registro por acidente.
        return deepcopy({k: v for k, v in registro.items() if k != "criado_em"})

    def criar(self, dados):
        with self._trava:
            self._limpar_expirados()
            numero = self._proximo_numero
            self._proximo_numero += 1
            self._registros[numero] = {
                **dados, "numero": numero, "criado_em": datetime.now(timezone.utc),
                "ia_status": "pendente", "orientacoes": [], "ia_erro": "",
            }
            return self._publico(self._registros[numero])

    def listar(self):
        with self._trava:
            self._limpar_expirados()
            return [self._publico(a) for a in reversed(list(self._registros.values()))]

    def iniciar_ia(self, numero):
        with self._trava:
            self._limpar_expirados()
            registro = self._registros.get(numero)
            if registro is None:
                raise KeyError(numero)
            # Não repetimos chamadas pagas por cliques simultâneos ou por atualização.
            if registro["ia_status"] in ("gerando", "concluida"):
                return self._publico(registro), False
            registro["ia_status"] = "gerando"
            registro["ia_erro"] = ""
            return self._publico(registro), True

    def terminar_ia(self, numero, orientacoes=None, erro=""):
        with self._trava:
            # O atendimento pode ter sido encerrado enquanto a IA respondia.
            self._limpar_expirados()
            registro = self._registros.get(numero)
            if registro is None:
                return None
            registro["ia_status"] = "erro" if erro else "concluida"
            registro["orientacoes"] = orientacoes or []
            registro["ia_erro"] = erro
            return self._publico(registro)

    def excluir(self, numero):
        with self._trava:
            self._limpar_expirados()
            return self._registros.pop(numero, None) is not None
