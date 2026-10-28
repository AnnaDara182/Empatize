# Empatize

**Você comunica. A gente acolhe.**

## Sobre o projeto

O Empatize é um sistema criado para ajudar pessoas que têm dificuldades de comunicação a informar suas preferências antes de um atendimento.

A pessoa pode indicar o que facilita sua comunicação, como receber instruções claras, ter menos barulho no ambiente ou ser avisada antes de um contato físico.

Essas informações ficam disponíveis no painel da recepção, permitindo que a equipe conheça as necessidades de cada pessoa e ofereça um atendimento mais acolhedor.

O sistema também conta com uma integração com inteligência artificial (IA), que gera sugestões de acolhimento com base nas informações fornecidas.

## Objetivo

O objetivo do Empatize é facilitar a comunicação entre as pessoas atendidas e os profissionais responsáveis pelo atendimento, respeitando as necessidades e preferências de cada pessoa.

## Funcionalidades

O sistema possui as seguintes funcionalidades:

- Cadastro das preferências de atendimento.
- Escolha do estado de comunicação no momento.
- Campo para informar necessidades específicas.
- Envio das informações para o painel da recepção.
- Visualização das solicitações recebidas.
- Geração de sugestões de acolhimento com inteligência artificial.
- Encerramento dos atendimentos após a conclusão.

## Tecnologias utilizadas

O projeto foi desenvolvido utilizando:

- **HTML:** estrutura das páginas.
- **CSS:** aparência e organização das telas.
- **JavaScript:** interações das páginas e comunicação com o servidor.
- **Python:** funcionamento do servidor e processamento das solicitações.
- **Inteligência artificial:** geração de sugestões de acolhimento.
- **GitHub Pages:** publicação das páginas do sistema.

O backend utiliza recursos nativos do Python para executar o servidor e armazenar temporariamente os atendimentos. Nesta versão, os dados ficam em memória e não são mantidos após o encerramento do servidor.

## Organização dos arquivos

Os principais arquivos e pastas do projeto são:

- `index.html`: página em que a pessoa informa suas preferências.
- `recepcao.html`: página utilizada pela equipe da recepção.
- `assets/css/`: arquivos responsáveis pela aparência das páginas.
- `assets/js/`: arquivos JavaScript responsáveis pelas interações e pela comunicação com o servidor.
- `assets/img/`: imagens utilizadas no sistema.
- `app.py`: arquivo que inicia o servidor.
- `backend/`: arquivos responsáveis pelo funcionamento do servidor, pela validação das informações, pelo armazenamento dos atendimentos e pela integração com a inteligência artificial.
- `static/`: arquivos utilizados pelo servidor Python para apresentar as páginas e seus recursos.
- `tests/`: arquivos com testes automatizados do projeto.

## Como executar o projeto

Para executar o sistema no computador, é necessário ter o Python 3.10 ou superior instalado.

1. Abra a pasta do projeto no Visual Studio Code.
2. Abra o terminal integrado.
3. Execute o comando abaixo:

   ```bash
   py app.py