# Empatize

**Você comunica. A gente acolhe.**

Protótipo para conclusão de curso: duas etapas para comunicar preferências e um painel de recepção. Visual lilás, opções em lista e campos livres nas duas etapas. Python, HTML, CSS e JavaScript, sem bibliotecas extras.

## 1. Abrir o projeto

Use **Python 3.10 ou superior** e um navegador atualizado.

1. Extraia o ZIP e abra a pasta `empatize` no VS Code.
2. Abra **Terminal → Novo Terminal**.
3. Execute `py app.py` no Windows. Alternativa: `python app.py`; no macOS/Linux: `python3 app.py`.
4. Abra **http://localhost:8000/** para a pessoa e **http://localhost:8000/recepcao** em outra aba.
5. Mantenha o terminal aberto. Para encerrar: **Ctrl+C**.

Não abra o HTML diretamente nem use Live Server: as chamadas precisam chegar ao servidor Python.

## 2. Fluxo

- Etapa 1: nome de chamada, quatro opções e campo livre. É permitido escrever apenas uma preferência diferente, sem marcar opções prontas.
- Etapa 2: estado de comunicação e campo livre. Voltar preserva os dados.
- Confirmação: nome e número do atendimento.
- Recepção: informações originais e botão **Gerar orientação de acolhimento**. Atualiza a cada 5 segundos. **Encerrar e remover atendimento** apaga o registro.

O envio não espera a IA. Uma falha da API não impede o atendimento.

## 3. Ativar a IA real

A chave fica no terminal do servidor, nunca no JavaScript. O programa **não lê arquivos .env** automaticamente.

PowerShell:

```powershell
$env:OPENAI_API_KEY="sua-chave-da-api"
py app.py
```

Prompt de Comando do Windows:

```bat
set OPENAI_API_KEY=sua-chave-da-api
py app.py
```

macOS/Linux:

```bash
export OPENAI_API_KEY="sua-chave-da-api"
python3 app.py
```

Obtenha a chave na [plataforma OpenAI](https://platform.openai.com/api-keys), com acesso ao modelo e saldo. A API pode ter custo separado da assinatura ChatGPT. Não compartilhe a chave nem envie ao Git. O modelo padrão é `gpt-4.1-mini`; mude usando `OPENAI_MODEL` no mesmo terminal.

Sem chave, o painel informa que a IA não está configurada. Em caso de falha, mostra uma mensagem e permite tentar novamente. Não apresenta respostas simuladas como se fossem IA real. Após o sucesso, reutiliza as orientações durante aquele atendimento, evitando chamadas pagas repetidas.

A IA recebe preferências, estado e os dois textos livres. O campo do nome e o número não são enviados. Se a pessoa incluir dados pessoais nos textos livres, esse conteúdo será enviado também: use dados fictícios na apresentação. `store: false` desabilita o armazenamento do objeto de resposta; não equivale a uma promessa de retenção zero pelo provedor.

O prompt está em `backend/ia_service.py`: até três sugestões práticas, sem inferir diagnóstico, recomendar tratamento ou prometer recursos. A equipe avalia as sugestões. Os relatos originais continuam visíveis.

**Terminologia:** este é um assistente de IA com uma tarefa definida, sem ações externas autônomas. Se o professor exigir um agente com ferramentas/autonomia, será necessária uma extensão específica.

Referências: [Responses API](https://developers.openai.com/api/reference/resources/responses) e [Structured Outputs](https://developers.openai.com/api/docs/guides/structured-outputs).

## 4. Organização e ajustes

| Arquivo | Responsabilidade / ajuste |
|---|---|
| `app.py` | Inicia e encerra o servidor. |
| `backend/config.py` | Textos, opções e limites. |
| `backend/validacao.py` | Valida os dados recebidos no servidor. |
| `backend/repositorio.py` | Guarda, lista, expira e remove registros em memória. |
| `backend/ia_service.py` | Prompt, pedido à API e interpretação da resposta. |
| `backend/servidor.py` | Rotas HTTP e arquivos públicos. |
| `static/index.html` | Conteúdo das duas etapas e confirmação. |
| `static/recepcao.html` | Estrutura do painel. |
| `static/css/base.css` | Cores, fontes, botões compartilhados. |
| `static/css/pessoa.css` | Layout do cliente para celular. |
| `static/css/recepcao.css` | Layout da recepção. |
| `static/js/api.js` | Comunicação com servidor e tratamento de erros de rede. |
| `static/js/pessoa.js` | Validação, etapas, contadores e envio. |
| `static/js/recepcao.js` | Cartões, atualização, IA e encerramento. |
| `static/img/acolhimento.svg` | Ilustração local. |
| `tests/test_fluxo.py` | Testes sem custos de API. |

Para mudar as cores, edite as variáveis no início de `base.css`. Para adicionar uma opção, inclua um checkbox no HTML, a chave em `config.py` e o rótulo em `recepcao.js`. Para mudar limites, mantenha `config.py`, atributos `maxlength` e contadores do JavaScript iguais.

## 5. Testar no celular / usar QR

No PowerShell, antes de iniciar:

```powershell
$env:HOST="0.0.0.0"
py app.py
```

Celular e computador precisam estar na mesma rede Wi-Fi. Use `ipconfig` para descobrir o IPv4 do computador e abra `http://SEU-IP:8000/` no celular, por exemplo `http://192.168.0.10:8000/`. O firewall pode exigir liberação para rede privada. Gere um QR para esse endereço, não para localhost (que apontaria para o celular). O QR apenas abre a página. O computador e servidor precisam continuar ligados.

## 6. Limites da demonstração

Sem autenticação: quem conseguir acessar o painel pode ler as solicitações. Use dados fictícios e não publique o servidor na internet. Os registros ficam apenas na memória por até duas horas, desaparecem ao encerrar o atendimento ou desligar o servidor. A numeração reinicia ao reiniciar o programa. As telas não usam localStorage; recarregar a página do cliente perde o rascunho.

Uso real exigiria autenticação e autorização da recepção, HTTPS e um projeto de proteção de dados.

## 7. Verificação

Dentro de `empatize`:

```bash
python -m unittest discover -s tests -v
```

Os testes cobrem envio, campos livres, entradas inválidas, botão da IA, falhas, reuso, expiração e remoção. A API é simulada: os testes não gastam créditos nem comprovam uma conexão com uma conta real.

## 8. Roteiro da apresentação

1. Abra pessoa e recepção em abas separadas.
2. Informe nome fictício, preferências e uma solicitação diferente.
3. Continue, escolha a comunicação e escreva o que ajuda.
4. Envie e mostre a confirmação com número.
5. Na recepção, mostre os relatos originais e gere uma orientação (chave configurada).
6. Explique que a IA sugere e a equipe avalia.
7. Encerre e mostre os dados removidos.
