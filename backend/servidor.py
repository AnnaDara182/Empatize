"""Rotas HTTP: recebem pedidos das telas e chamam os serviços correspondentes."""
import json
import re
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlsplit
from .config import STATIC_DIR
from .ia_service import IAIndisponivel, gerar_orientacoes
from .repositorio import Repositorio
from .validacao import DadosInvalidos, validar_atendimento

repositorio = Repositorio()
# Lista explícita: o navegador só pode baixar arquivos públicos, nunca código ou chaves.
ARQUIVOS = {
    "/": ("index.html", "text/html; charset=utf-8"),
    "/recepcao": ("recepcao.html", "text/html; charset=utf-8"),
    "/static/css/base.css": ("css/base.css", "text/css; charset=utf-8"),
    "/static/css/pessoa.css": ("css/pessoa.css", "text/css; charset=utf-8"),
    "/static/css/recepcao.css": ("css/recepcao.css", "text/css; charset=utf-8"),
    "/static/js/api.js": ("js/api.js", "text/javascript; charset=utf-8"),
    "/static/js/pessoa.js": ("js/pessoa.js", "text/javascript; charset=utf-8"),
    "/static/js/recepcao.js": ("js/recepcao.js", "text/javascript; charset=utf-8"),
    "/static/img/acolhimento.svg": ("img/acolhimento.svg", "image/svg+xml"),
}


class Servidor(BaseHTTPRequestHandler):
    def log_message(self, formato, *args):
        # Apenas método e caminho; não registramos nomes nem campos livres no terminal.
        print(f"{self.command} {urlsplit(self.path).path}")

    def responder(self, corpo, tipo, status=200):
        self.send_response(status)
        self.send_header("Content-Type", tipo)
        self.send_header("Content-Length", str(len(corpo)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(corpo)

    def json(self, dados, status=200):
        self.responder(json.dumps(dados, ensure_ascii=False).encode("utf-8"),
                       "application/json; charset=utf-8", status)

    def ler_json(self):
        try:
            tamanho = int(self.headers.get("Content-Length", "0"))
            if not 0 < tamanho <= 8192:
                raise ValueError()
            return json.loads(self.rfile.read(tamanho).decode("utf-8"))
        except (ValueError, UnicodeError):
            raise DadosInvalidos("Não foi possível ler a solicitação enviada.") from None

    def do_GET(self):
        caminho = urlsplit(self.path).path
        if caminho == "/api/atendimentos":
            return self.json(repositorio.listar())
        if caminho not in ARQUIVOS:
            return self.json({"erro": "Página não encontrada."}, 404)
        arquivo, tipo = ARQUIVOS[caminho]
        self.responder((STATIC_DIR / arquivo).read_bytes(), tipo)

    def do_POST(self):
        caminho = urlsplit(self.path).path
        if caminho == "/api/atendimentos":
            try:
                dados = validar_atendimento(self.ler_json())
            except DadosInvalidos as erro:
                return self.json({"erro": str(erro)}, 400)
            # Envio imediato: não espera a IA e não chama uma API paga automaticamente.
            registro = repositorio.criar(dados)
            return self.json({"numero": registro["numero"], "nome": registro["nome"]}, 201)
        rota_ia = re.fullmatch(r"/api/atendimentos/(\d+)/orientacoes", caminho)
        if rota_ia:
            numero = int(rota_ia.group(1))
            try:
                registro, precisa_gerar = repositorio.iniciar_ia(numero)
            except KeyError:
                return self.json({"erro": "Esse atendimento já foi encerrado ou expirou."}, 404)
            if not precisa_gerar:
                return self.json(registro, 202 if registro["ia_status"] == "gerando" else 200)
            try:
                dicas = gerar_orientacoes(registro)
                registro = repositorio.terminar_ia(numero, orientacoes=dicas)
            except IAIndisponivel as erro:
                registro = repositorio.terminar_ia(numero, erro=str(erro))
                if registro is None:
                    return self.json({"erro": "Atendimento encerrado ou expirado."}, 404)
                return self.json({"erro": str(erro)}, 503)
            if registro is None:
                return self.json({"erro": "Atendimento encerrado ou expirado."}, 404)
            return self.json(registro)
        self.json({"erro": "Endereço não encontrado."}, 404)

    def do_DELETE(self):
        rota = re.fullmatch(r"/api/atendimentos/(\d+)", urlsplit(self.path).path)
        if not rota or not repositorio.excluir(int(rota.group(1))):
            return self.json({"erro": "Atendimento não encontrado."}, 404)
        self.json({"mensagem": "Atendimento encerrado e removido."})
