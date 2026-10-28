"""Recebe as solicitações e disponibiliza os atendimentos."""

import json
import os
import re
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlsplit

from .config import ROOT, ASSETS_DIR
from .ia_service import IAIndisponivel, gerar_orientacoes
from .repositorio import Repositorio
from .validacao import DadosInvalidos, validar_atendimento


# Acesso aos dados dos atendimentos.
repositorio = Repositorio()


# Arquivos que o navegador pode acessar.
ARQUIVOS = {
    # Páginas principais, localizadas na raiz do projeto.
    "/": (ROOT / "index.html", "text/html; charset=utf-8"),
    "/recepcao": (ROOT / "recepcao.html", "text/html; charset=utf-8"),

    # Arquivos CSS.
    "/assets/css/base.css": (
        ASSETS_DIR / "css" / "base.css",
        "text/css; charset=utf-8",
    ),
    "/assets/css/pessoa.css": (
        ASSETS_DIR / "css" / "pessoa.css",
        "text/css; charset=utf-8",
    ),
    "/assets/css/recepcao.css": (
        ASSETS_DIR / "css" / "recepcao.css",
        "text/css; charset=utf-8",
    ),

    # Arquivos JavaScript.
    "/assets/js/api.js": (
        ASSETS_DIR / "js" / "api.js",
        "text/javascript; charset=utf-8",
    ),
    "/assets/js/config.js": (
        ASSETS_DIR / "js" / "config.js",
        "text/javascript; charset=utf-8",
    ),
    "/assets/js/pessoa.js": (
        ASSETS_DIR / "js" / "pessoa.js",
        "text/javascript; charset=utf-8",
    ),
    "/assets/js/recepcao.js": (
        ASSETS_DIR / "js" / "recepcao.js",
        "text/javascript; charset=utf-8",
    ),

    # Imagens.
    "/assets/img/acolhimento.png": (
        ASSETS_DIR / "img" / "acolhimento.png",
        "image/png",
    ),
    "/assets/img/acolhimento.svg": (
        ASSETS_DIR / "img" / "acolhimento.svg",
        "image/svg+xml",
    ),
    "/assets/img/acolhimento2.png": (
        ASSETS_DIR / "img" / "acolhimento2.png",
        "image/png",
    ),
}


class Servidor(BaseHTTPRequestHandler):

    # Registra o método e o caminho acessado.
    def log_message(self, formato, *args):
        caminho = urlsplit(self.path).path
        print(f"{self.command} {caminho}")

    # Configura o acesso do frontend à API.
    def configurar_cors(self):
        origem = self.headers.get("Origin")
        origem_permitida = os.getenv("CORS_ORIGIN", "").strip()

        if origem and origem_permitida and origem == origem_permitida:
            self.send_header("Access-Control-Allow-Origin", origem)
            self.send_header("Vary", "Origin")
            self.send_header(
                "Access-Control-Allow-Methods",
                "GET, POST, DELETE, OPTIONS",
            )
            self.send_header(
                "Access-Control-Allow-Headers",
                "Content-Type",
            )

    # Envia uma resposta HTTP.
    def responder(self, corpo, tipo, status=200):
        self.send_response(status)
        self.send_header("Content-Type", tipo)
        self.send_header("Content-Length", str(len(corpo)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")

        self.configurar_cors()

        self.end_headers()
        self.wfile.write(corpo)

    # Envia uma resposta em JSON.
    def responder_json(self, dados, status=200):
        corpo = json.dumps(
            dados,
            ensure_ascii=False,
        ).encode("utf-8")

        self.responder(
            corpo,
            "application/json; charset=utf-8",
            status,
        )

    # Lê os dados enviados pelo frontend.
    def ler_json(self):
        try:
            tamanho = int(self.headers.get("Content-Length", "0"))

            # Impede requisições vazias ou excessivamente grandes.
            if not 0 < tamanho <= 8192:
                raise ValueError()

            return json.loads(
                self.rfile.read(tamanho).decode("utf-8")
            )

        except (ValueError, UnicodeError):
            raise DadosInvalidos(
                "Não foi possível ler a solicitação enviada."
            ) from None

    # Responde às verificações de acesso da API.
    def do_OPTIONS(self):
        self.send_response(204)
        self.configurar_cors()
        self.send_header("Content-Length", "0")
        self.end_headers()

    # Consulta os atendimentos e disponibiliza os arquivos.
    def do_GET(self):
        caminho = urlsplit(self.path).path

        # Retorna os atendimentos registrados.
        if caminho == "/api/atendimentos":
            return self.responder_json(repositorio.listar())

        # Verifica se o arquivo solicitado está cadastrado.
        if caminho not in ARQUIVOS:
            return self.responder_json(
                {"erro": "Página não encontrada."},
                404,
            )

        arquivo, tipo = ARQUIVOS[caminho]

        try:
            conteudo = arquivo.read_bytes()

        except OSError:
            return self.responder_json(
                {"erro": "Não foi possível carregar o arquivo."},
                404,
            )

        self.responder(conteudo, tipo)

    # Cria atendimentos e gera orientações com a IA.
    def do_POST(self):
        caminho = urlsplit(self.path).path

        # Cria um novo atendimento.
        if caminho == "/api/atendimentos":
            try:
                dados = validar_atendimento(self.ler_json())

            except DadosInvalidos as erro:
                return self.responder_json(
                    {"erro": str(erro)},
                    400,
                )

            registro = repositorio.criar(dados)

            return self.responder_json(
                {
                    "numero": registro["numero"],
                    "nome": registro["nome"],
                },
                201,
            )

        # Identifica a solicitação de orientações para um atendimento.
        # Exemplo: /api/atendimentos/12/orientacoes
        rota_ia = re.fullmatch(
            r"/api/atendimentos/(\d+)/orientacoes",
            caminho,
        )

        if rota_ia:
            numero = int(rota_ia.group(1))

            try:
                registro, precisa_gerar = repositorio.iniciar_ia(numero)

            except KeyError:
                return self.responder_json(
                    {
                        "erro": (
                            "Esse atendimento já foi encerrado "
                            "ou expirou."
                        )
                    },
                    404,
                )

            # Evita gerar orientações novamente se já houver uma solicitação.
            if not precisa_gerar:
                status = (
                    202
                    if registro["ia_status"] == "gerando"
                    else 200
                )

                return self.responder_json(registro, status)

            try:
                # Solicita as orientações ao Gemini.
                orientacoes = gerar_orientacoes(registro)

                # Salva o resultado no atendimento.
                registro = repositorio.terminar_ia(
                    numero,
                    orientacoes=orientacoes,
                )

            except IAIndisponivel as erro:
                # Registra o erro para informar o painel.
                registro = repositorio.terminar_ia(
                    numero,
                    erro=str(erro),
                )

                if registro is None:
                    return self.responder_json(
                        {"erro": "Atendimento encerrado ou expirado."},
                        404,
                    )

                return self.responder_json(
                    {"erro": str(erro)},
                    503,
                )

            if registro is None:
                return self.responder_json(
                    {"erro": "Atendimento encerrado ou expirado."},
                    404,
                )

            return self.responder_json(registro)

        # Endereço não reconhecido.
        return self.responder_json(
            {"erro": "Endereço não encontrado."},
            404,
        )

    # Encerra e remove um atendimento.
    def do_DELETE(self):
        caminho = urlsplit(self.path).path

        # Aceita somente números de atendimento.
        # Exemplo: /api/atendimentos/12
        rota = re.fullmatch(
            r"/api/atendimentos/(\d+)",
            caminho,
        )

        if not rota:
            return self.responder_json(
                {"erro": "Atendimento não encontrado."},
                404,
            )

        numero = int(rota.group(1))

        if not repositorio.excluir(numero):
            return self.responder_json(
                {"erro": "Atendimento não encontrado."},
                404,
            )

        self.responder_json(
            {"mensagem": "Atendimento encerrado e removido."}
        )

    # Evita um traceback quando o navegador encerra a conexão.
    def handle_one_request(self):
        try:
            super().handle_one_request()

        except (ConnectionAbortedError, ConnectionResetError, BrokenPipeError):
            # A conexão foi interrompida antes de a resposta ser enviada.
            # Não é necessário encerrar o programa por causa disso.
            pass