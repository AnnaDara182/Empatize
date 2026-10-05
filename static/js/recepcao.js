import { requisitar } from './api.js';

const lista = document.querySelector('#lista');
const aviso = document.querySelector('#aviso');
const preferenciaRotulos = {
  som: 'Menos barulho', instrucoes: 'Instruções claras',
  toque: 'Avisar antes de tocar', espera: 'Previsão de espera',
};
const estadoRotulos = {
  verde: 'Consigo me comunicar', amarelo: 'Estou ficando sobrecarregado(a)',
  vermelho: 'Estou com dificuldade para me comunicar',
};
let ultimaLista = '';
let carregando = false;
const ocupados = new Set();

// Pequeno utilitário para montar elementos com texto seguro (sem innerHTML).
function elemento(tag, texto = '', classe = '') {
  const item = document.createElement(tag);
  item.textContent = texto;
  if (classe) item.className = classe;
  return item;
}

function adicionarTextoLivre(cartao, titulo, texto) {
  if (!texto) return;
  cartao.append(elemento('h3', titulo), elemento('p', texto, 'free-text'));
}

function criarCartao(atendimento) {
  const cartao = elemento('article', '', 'attendance');
  cartao.dataset.numero = atendimento.numero;
  cartao.append(elemento('p', `Atendimento #${atendimento.numero}`, 'number'),
    elemento('h2', atendimento.nome), elemento('p', estadoRotulos[atendimento.estado], 'state'));
  cartao.append(elemento('h3', 'Preferências informadas'));
  if (atendimento.escolhas.length) {
    const preferencias = elemento('ul');
    for (const chave of atendimento.escolhas) preferencias.append(elemento('li', preferenciaRotulos[chave]));
    cartao.append(preferencias);
  }
  adicionarTextoLivre(cartao, 'Outra preferência', atendimento.outra_preferencia);
  adicionarTextoLivre(cartao, 'O que ajuda na comunicação', atendimento.ajuda_comunicacao);

  const bloco = elemento('div', '', 'ai-block');
  bloco.append(elemento('p', 'Assistente de acolhimento', 'ai-label'));
  bloco.append(elemento('p', 'A IA sugere. A equipe avalia o que é possível oferecer.', 'ai-disclaimer'));
  if (atendimento.ia_status === 'concluida') {
    const dicas = elemento('ul');
    for (const dica of atendimento.orientacoes) dicas.append(elemento('li', dica));
    bloco.append(dicas);
  } else {
    if (atendimento.ia_erro) bloco.append(elemento('p', atendimento.ia_erro, 'ai-error'));
    const botao = elemento('button', atendimento.ia_status === 'gerando' ? 'Gerando orientação…' : 'Gerar orientação de acolhimento', 'button primary');
    botao.type = 'button';
    botao.disabled = atendimento.ia_status === 'gerando';
    botao.addEventListener('click', async () => {
      ocupados.add(atendimento.numero);
      botao.disabled = true;
      botao.textContent = 'Gerando orientação…';
      aviso.textContent = '';
      try {
        await requisitar(`/api/atendimentos/${atendimento.numero}/orientacoes`, { metodo: 'POST' });
      } catch (erro) {
        aviso.textContent = erro.message;
      } finally {
        ocupados.delete(atendimento.numero);
        await atualizar(true);
      }
    });
    bloco.append(botao);
  }
  cartao.append(bloco);
  const encerrar = elemento('button', 'Encerrar e remover atendimento', 'button text-button end-button');
  encerrar.type = 'button';
  encerrar.addEventListener('click', async () => {
    if (!window.confirm(`Encerrar o atendimento #${atendimento.numero} e remover os dados?`)) return;
    encerrar.disabled = true;
    try {
      await requisitar(`/api/atendimentos/${atendimento.numero}`, { metodo: 'DELETE' });
      await atualizar(true);
      aviso.textContent = `Atendimento #${atendimento.numero} encerrado.`;
    } catch (erro) {
      aviso.textContent = erro.message;
      encerrar.disabled = false;
    }
  });
  cartao.append(encerrar);
  return cartao;
}

async function atualizar(forcar = false) {
  // Evita consultas sobrepostas e troca de cartões durante uma chamada de IA.
  if (carregando || ocupados.size) return;
  carregando = true;
  try {
    const atendimentos = await requisitar('/api/atendimentos');
    const assinatura = JSON.stringify(atendimentos);
    document.querySelector('#total').textContent = atendimentos.length;
    if (assinatura !== ultimaLista || forcar) {
      // Preserva o foco de teclado caso a lista mude enquanto a pessoa navega nela.
      const foco = document.activeElement;
      const numero = foco?.closest('.attendance')?.dataset.numero;
      const classeBotao = foco?.classList.contains('end-button') ? '.end-button' : '.primary';
      lista.replaceChildren(...atendimentos.map(criarCartao));
      if (!atendimentos.length) lista.append(elemento('p', 'Nenhuma solicitação por enquanto. Quando alguém enviar, ela aparece aqui.', 'empty'));
      ultimaLista = assinatura;
      if (numero) lista.querySelector(`[data-numero="${numero}"] ${classeBotao}`)?.focus();
    }
  } catch (erro) {
    aviso.textContent = erro.message;
  } finally {
    carregando = false;
  }
}
document.querySelector('#atualizar').addEventListener('click', () => { aviso.textContent = ''; atualizar(true); });
atualizar();
setInterval(() => atualizar(), 5000);
