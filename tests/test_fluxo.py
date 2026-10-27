"""Testa o fluxo real por HTTP e simula a API da IA, sem gastar créditos."""
import io
import json
import os
import threading
import unittest
from datetime import datetime, timedelta, timezone
from http.server import ThreadingHTTPServer
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.request import Request, urlopen
from backend import servidor
from backend.ia_service import IAIndisponivel, gerar_orientacoes
from backend.repositorio import Repositorio

DADOS = {"nome": "Anna", "escolhas": ["som", "toque"], "estado": "amarelo",
         "outra_preferencia": "Prefiro aguardar perto da porta.",
         "ajuda_comunicacao": "Consigo responder melhor por escrito."}


class TestFluxo(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.http = ThreadingHTTPServer(("127.0.0.1", 0), servidor.Servidor)
        cls.thread = threading.Thread(target=cls.http.serve_forever, daemon=True)
        cls.thread.start()
        cls.base = f"http://127.0.0.1:{cls.http.server_port}"

    @classmethod
    def tearDownClass(cls):
        cls.http.shutdown()
        cls.http.server_close()
        cls.thread.join()

    def setUp(self):
        servidor.repositorio = Repositorio()

    def chamar(self, caminho, metodo="GET", dados=None):
        req = Request(self.base + caminho, method=metodo,
                      data=json.dumps(dados).encode() if dados is not None else None)
        try:
            with urlopen(req) as resposta:
                return resposta.status, json.load(resposta)
        except HTTPError as erro:
            return erro.code, json.load(erro)

    def test_envio_independente_da_ia_e_campos_livres_preservados(self):
        with patch('backend.servidor.gerar_orientacoes') as ia:
            status, resultado = self.chamar('/api/atendimentos', 'POST', DADOS)
            self.assertEqual(status, 201)
            ia.assert_not_called()
        lista = self.chamar('/api/atendimentos')[1]
        self.assertEqual(lista[0]['nome'], 'Anna')
        self.assertEqual(lista[0]['ajuda_comunicacao'], DADOS['ajuda_comunicacao'])
        self.assertEqual(lista[0]['ia_status'], 'pendente')
        self.assertNotIn('criado_em', lista[0])

    def test_aceita_preferencia_so_por_texto(self):
        self.assertEqual(self.chamar('/api/atendimentos', 'POST', {**DADOS, 'escolhas': []})[0], 201)

    def test_rejeita_entradas_invalidas_sem_derrubar_servidor(self):
        for dados in [[], {**DADOS, 'nome': ''}, {**DADOS, 'escolhas': [[]]},
                      {**DADOS, 'estado': []}, {**DADOS, 'escolhas': ['som', 'som']},
                      {**DADOS, 'outra_preferencia': 'x' * 401},
                      {**DADOS, 'escolhas': [], 'outra_preferencia': ''}]:
            with self.subTest(dados=dados):
                self.assertEqual(self.chamar('/api/atendimentos', 'POST', dados)[0], 400)

    def test_botao_ia_e_reuso_sem_nova_cobranca(self):
        numero = self.chamar('/api/atendimentos', 'POST', DADOS)[1]['numero']
        with patch('backend.servidor.gerar_orientacoes', return_value=['Ofereça comunicação escrita.']) as ia:
            rota = f'/api/atendimentos/{numero}/orientacoes'
            self.assertEqual(self.chamar(rota, 'POST')[1]['ia_status'], 'concluida')
            self.chamar(rota, 'POST')
            ia.assert_called_once()

    def test_falha_ia_preserva_solicitacao_e_permite_tentar_novamente(self):
        numero = self.chamar('/api/atendimentos', 'POST', DADOS)[1]['numero']
        rota = f'/api/atendimentos/{numero}/orientacoes'
        with patch.dict(os.environ, {"OPENAI_API_KEY": ""}):
            self.assertEqual(self.chamar(rota, 'POST')[0], 503)
        self.assertEqual(self.chamar('/api/atendimentos')[1][0]['nome'], 'Anna')
        with patch('backend.servidor.gerar_orientacoes', return_value=['Dê tempo para responder.']):
            self.assertEqual(self.chamar(rota, 'POST')[1]['ia_status'], 'concluida')

    def test_encerrar_remove_registro(self):
        numero = self.chamar('/api/atendimentos', 'POST', DADOS)[1]['numero']
        self.assertEqual(self.chamar(f'/api/atendimentos/{numero}', 'DELETE')[0], 200)
        self.assertEqual(self.chamar('/api/atendimentos')[1], [])

    def test_registro_expirado_nao_pode_ser_acessado(self):
        servidor.repositorio.criar(DADOS)
        servidor.repositorio._registros[1]['criado_em'] = datetime.now(timezone.utc) - timedelta(hours=3)
        self.assertEqual(self.chamar('/api/atendimentos')[1], [])
        self.assertEqual(self.chamar('/api/atendimentos/1/orientacoes', 'POST')[0], 404)


class TestIA(unittest.TestCase):
    def test_resposta_simulada_e_nome_fora_do_payload(self):
        resposta = {"output": [{"type": "message", "content": [{"type": "output_text", "text":
                     json.dumps({"orientacoes": ["Ofereça comunicação escrita."]})}]}]}
        with patch.dict(os.environ, {"OPENAI_API_KEY": "chave-ficticia"}), \
             patch('backend.ia_service.urlopen', return_value=io.BytesIO(json.dumps(resposta).encode())) as abrir:
            self.assertEqual(gerar_orientacoes(DADOS), ['Ofereça comunicação escrita.'])
            enviado = json.loads(abrir.call_args.args[0].data)
            contexto = json.loads(enviado['input'])
            self.assertNotIn('nome', contexto)
            self.assertEqual(contexto['ajuda_comunicacao'], DADOS['ajuda_comunicacao'])
            self.assertFalse(enviado['store'])

    def test_resposta_invalida_nao_vira_orientacao(self):
        with patch.dict(os.environ, {"OPENAI_API_KEY": "chave-ficticia"}), \
             patch('backend.ia_service.urlopen', return_value=io.BytesIO(b'{"output": []}')):
            with self.assertRaises(IAIndisponivel):
                gerar_orientacoes(DADOS)


if __name__ == '__main__':
    unittest.main()
