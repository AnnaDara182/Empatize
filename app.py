"""Ponto de entrada do Empatize.
No terminal, execute: python app.py (ou py app.py no Windows).
"""

import os
from pathlib import Path
from http.server import ThreadingHTTPServer


def carregar_variaveis_ambiente():
    """Carrega as configurações do arquivo .env."""

    # Localiza o arquivo .env na pasta principal do projeto.
    caminho_env = Path(__file__).resolve().parent / ".env"

    # Se o arquivo não existir, a função não altera nada.
    if not caminho_env.exists():
        return

    # Lê o arquivo como texto, tratando também um possível BOM.
    linhas = caminho_env.read_text(encoding="utf-8-sig").splitlines()

    for linha in linhas:
        linha = linha.strip()

        # Ignora linhas vazias, comentários e linhas sem sinal de igual.
        if not linha or linha.startswith("#") or "=" not in linha:
            continue

        # Separa o nome da variável do seu valor.
        nome, valor = linha.split("=", 1)

        nome = nome.strip()
        valor = valor.strip().strip('"').strip("'")

        # Não substitui variáveis que já foram configuradas no sistema.
        if nome and nome not in os.environ:
            os.environ[nome] = valor


# Carrega o .env antes de importar o servidor.
# Assim, os outros arquivos já conseguem acessar as variáveis.
carregar_variaveis_ambiente()

from backend.servidor import Servidor


def main():
    """Inicia o servidor web do Empatize."""

    # Define a porta do servidor, usando 8000 como padrão.
    porta = int(os.getenv("PORT", "8000"))

    # O padrão permite acessar o sistema somente pelo computador.
    host = os.getenv("HOST", "127.0.0.1")

    servidor = ThreadingHTTPServer((host, porta), Servidor)

    print(f"Empatize: http://localhost:{porta}/")
    print(f"Recepção: http://localhost:{porta}/recepcao")
    print("Pressione Ctrl+C para encerrar.")

    try:
        servidor.serve_forever()

    except KeyboardInterrupt:
        print("\nEmpatize encerrado.")

    finally:
        servidor.server_close()


if __name__ == "__main__":
    main()