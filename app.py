"""Ponto de entrada. No terminal, execute: python app.py (ou py app.py no Windows)."""
import os
from http.server import ThreadingHTTPServer
from backend.servidor import Servidor


def main():
    porta = int(os.getenv("PORT", "8000"))
    # Localhost é suficiente para a apresentação em duas abas. Para testar no celular,
    # defina HOST=0.0.0.0 e use o IP do computador na mesma rede (instruções no README).
    host = os.getenv("HOST", "127.0.0.1")
    servidor = ThreadingHTTPServer((host, porta), Servidor)
    print(f"Empatize: http://localhost:{porta}/")
    print(f"Recepção: http://localhost:{porta}/recepcao")
    print("Pressione Ctrl+C para encerrar.")
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        print("\nEmpatize encerrado. Os registros temporários foram descartados.")
    finally:
        servidor.server_close()


if __name__ == "__main__":
    main()
