"""Constantes do projeto. Ajuste os limites aqui, sem procurar em vários arquivos."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STATIC_DIR = ROOT / "static"
TEMPO_EXPIRACAO_HORAS = 2
LIMITE_NOME = 60
LIMITE_TEXTO = 400
# As chaves são usadas no HTML; os rótulos são exibidos na recepção.
PREFERENCIAS = {
    "som": "Menos barulho",
    "instrucoes": "Instruções claras",
    "toque": "Avisar antes de tocar",
    "espera": "Previsão de espera",
}
ESTADOS = {
    "verde": "Consigo me comunicar",
    "amarelo": "Estou ficando sobrecarregado(a)",
    "vermelho": "Estou com dificuldade para me comunicar",
}
