# Empatize

**Você comunica. A gente acolhe.**

O Empatize ajuda pessoas com algum tipo de dificuldade de comunicação a informar preferências antes do atendimento. A recepção consulta essas informações e pode solicitar orientações de acolhimento geradas por IA.

## Estrutura do projeto

- `index.html` e `recepcao.html` — interface publicada no GitHub Pages.
- `assets/css/` — estilos das telas.
- `assets/js/` — comportamento das telas e comunicação com a API.
- `assets/js/config.js` — endereço do backend usado pela interface publicada.
- `assets/img/acolhimento.png` — ilustração da tela inicial.
- `app.py` e `backend/` — servidor HTTP, validação, armazenamento e integração com IA.
- `static/` — interface servida pelo backend Python.
- `tests/` — testes automatizados do backend.

## Executar localmente

1. Instale Python 3.10 ou superior.
2. Abra o terminal nesta pasta.
3. Execute `py app.py` no Windows ou `python3 app.py` no macOS/Linux.
4. Acesse `http://localhost:8000/` para o formulário e `http://localhost:8000/recepcao` para o painel.
5. Mantenha o terminal aberto enquanto estiver usando o sistema.

O servidor local compartilha os atendimentos entre as duas telas. Os registros são mantidos em memória, expiram após duas horas e são perdidos quando o servidor é encerrado.

## Publicar a interface no GitHub Pages

O GitHub Pages hospeda HTML, CSS, JavaScript e imagens, mas não executa o servidor Python. Para que o formulário e o painel funcionem no site publicado, hospede `app.py` e `backend/` em um serviço que execute Python e mantenha o servidor disponível.

Depois de hospedar a API:

1. Configure no serviço do backend a variável `CORS_ORIGIN` com a origem do site, por exemplo `https://annadara182.github.io` (sem a barra final).
2. Configure `OPENAI_API_KEY` no ambiente do backend para habilitar as orientações de IA. Opcionalmente, defina `OPENAI_MODEL`. Não coloque a chave em HTML, CSS ou JavaScript.
3. Abra `assets/js/config.js` e defina `window.EMPATIZE_API_URL` com a URL pública do backend, sem barra no final.
4. Envie os arquivos atualizados para a branch `main`.
5. No GitHub, em **Settings → Pages**, selecione **Deploy from a branch**, branch `main` e pasta `/(root)`.

## Como funciona a integração com IA

A IA é acionada pela equipe no painel, não automaticamente ao enviar um atendimento. O nome e o número do atendimento não são enviados à API de IA, mas as preferências e os campos livres são enviados para gerar orientações. Informe isso às pessoas antes do uso e evite coletar dados pessoais desnecessários. As orientações são sugestões de apoio, não diagnósticos nem substitutos do julgamento da equipe.

## Antes de usar com atendimentos reais

O armazenamento atual do backend é em memória e o painel ainda não tem autenticação. Portanto, esta versão é adequada para desenvolvimento e validação técnica, mas ainda não deve ser usada para guardar informações sensíveis de pessoas em um ambiente público. Antes de uso operacional, implemente autenticação e autorização para a recepção, armazenamento persistente com controle de acesso, HTTPS, política de retenção e exclusão, além de aviso de privacidade e processo de consentimento apropriados.

## Testes

Execute `py -m unittest discover -s tests` no Windows ou `python3 -m unittest discover -s tests` no macOS/Linux. Os testes isolam a chamada externa de IA para não depender de uma chave ou gerar cobranças.
