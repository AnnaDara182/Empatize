"""Configurações gerais do projeto Empatize."""

from pathlib import Path

# Caminho da pasta principal do projeto.
ROOT = Path(__file__).resolve().parent.parent

# Pasta que contém os arquivos do frontend.
ASSETS_DIR = ROOT / "assets"

# Pasta onde o banco de dados será armazenado.
PASTA_DADOS = ROOT / "dados"

# Caminho completo do banco de dados SQLite.
BANCO_DADOS = PASTA_DADOS / "empatize.db"

# Tempo máximo de permanência de um atendimento.
TEMPO_EXPIRACAO_HORAS = 2

# Limites de caracteres dos campos.
LIMITE_NOME = 60
LIMITE_TEXTO = 400

# Preferências disponíveis na tela de atendimento.
PREFERENCIAS = {
    "som": "Menos barulho",
    "instrucoes": "Instruções claras",
    "toque": "Avisar antes de tocar",
    "espera": "Previsão de espera",
}

# Estados de comunicação disponíveis.
ESTADOS = {
    "verde": "Consigo me comunicar",
    "amarelo": "Estou ficando sobrecarregado(a)",
    "vermelho": "Estou com dificuldade para me comunicar",
}