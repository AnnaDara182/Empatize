# Empatize

**Você comunica. A gente acolhe.**

O Empatize é um protótipo para ajudar pessoas com algum tipo de dificuldade de comunicação a informar suas preferências antes do atendimento.

## Publicar no GitHub Pages

Esta cópia está organizada para o GitHub Pages abrir a interface do projeto automaticamente: o arquivo **`index.html` está na raiz** do repositório. O `README.md` pode continuar na raiz; quando o Pages estiver configurado corretamente, ele abre `index.html`, não o README.

1. Extraia o arquivo ZIP.
2. Entre na pasta `empatize_pages` (a pasta que contém `index.html` e `README.md`).
3. Envie **o conteúdo dessa pasta** para a raiz do seu repositório GitHub. Não envie a pasta externa como uma pasta dentro do repositório e não envie a pasta `.git` de outro repositório.
4. No GitHub, abra **Settings → Pages**.
5. Em **Build and deployment**, escolha **Deploy from a branch**.
6. Selecione a branch `main` e a pasta `/(root)`; clique em **Save**.
7. Aguarde a publicação e abra o endereço mostrado na seção Pages.

A tela principal será `index.html`. O painel de recepção fica em `recepcao.html`, acessível acrescentando `recepcao.html` ao endereço publicado.

## O que funciona nesta versão do Pages

- Formulário da pessoa em duas etapas.
- Validação dos campos e tela de confirmação com número.
- Painel da recepção.
- Sugestões fixas para demonstrar o fluxo do painel.
- Salvamento de demonstração no `localStorage` do navegador.

### Limitações importantes do GitHub Pages

O GitHub Pages hospeda apenas arquivos estáticos. Ele **não executa o servidor Python (`app.py`) nem conecta a IA real**.

Nesta versão, os registros ficam somente no armazenamento local do navegador em que foram preenchidos. Isso significa que a recepção em outro computador ou celular **não verá os mesmos atendimentos**. As orientações do botão são exemplos fixos, não respostas de uma IA real. Use somente dados fictícios na demonstração.

Para usar o sistema com a recepção compartilhando os atendimentos e com a IA real, será necessário hospedar o backend Python em um serviço compatível e configurar o endereço da API. **Nunca coloque a chave da API de IA no HTML ou no JavaScript.**

## Executar a versão Python localmente

O ZIP também mantém o backend original do protótipo.

1. Instale Python 3.10 ou superior.
2. Abra o terminal na pasta do projeto.
3. Execute no Windows: `py app.py` (ou `python app.py`). No macOS/Linux: `python3 app.py`.
4. Acesse `http://localhost:8000/` para a tela da pessoa e `http://localhost:8000/recepcao` para o painel.
5. Mantenha o terminal aberto enquanto estiver usando o sistema.

A versão local usa os arquivos dentro da pasta `static/`; a versão de demonstração do GitHub Pages usa os arquivos na raiz e em `assets/`.

## Estrutura principal

- `index.html` — página inicial publicada pelo GitHub Pages.
- `recepcao.html` — painel da recepção na versão Pages.
- `assets/css/` — estilos da interface publicada.
- `assets/js/` — comportamento das telas e adaptador de demonstração.
- `assets/img/` — ilustração da interface.
- `app.py` e `backend/` — servidor Python da versão local.
- `static/` — interface usada pelo servidor Python.
- `tests/` — testes do backend.

