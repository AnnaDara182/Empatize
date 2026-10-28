import { requisitar } from './api.js';

// Referências ficam reunidas aqui para facilitar a leitura e evitar buscas repetidas.
const formulario = document.querySelector('#formulario');
const nome = document.querySelector('#nome');
const outraPreferencia = document.querySelector('#outra-preferencia');
const ajudaComunicacao = document.querySelector('#ajuda-comunicacao');
const mensagem = document.querySelector('#mensagem');
const enviar = document.querySelector('#enviar');
let enviando = false;

function mostrarErro(texto) {
  mensagem.textContent = texto;
  mensagem.hidden = !texto;
}

function mudarEtapa(numero) {
  document.querySelector('#etapa-1').hidden = numero !== 1;
  document.querySelector('#etapa-2').hidden = numero !== 2;
  document.querySelector('#etapa-texto').textContent = `${numero} de 2`;
  document.querySelector('#etapa-barra').style.width = `${numero * 50}%`;
  document.querySelector('#progresso').setAttribute('aria-label', `Etapa ${numero} de 2`);
  mostrarErro('');
  // O foco avisa usuários de teclado e leitores de tela que a etapa mudou.
  document.querySelector(`#titulo-${numero}`).focus();
  window.scrollTo({ top: 0, behavior: 'auto' });
}

function lerEscolhas() {
  return [...formulario.querySelectorAll('input[name="escolha"]:checked')].map(campo => campo.value);
}

function validarPrimeiraEtapa() {
  if (!nome.value.trim()) {
    mostrarErro('Informe como podemos chamar você.');
    nome.focus();
    return false;
  }
  if (!lerEscolhas().length && !outraPreferencia.value.trim()) {
    mostrarErro('Escolha uma opção ou escreva a sua preferência.');
    outraPreferencia.focus();
    return false;
  }
  return true;
}

document.querySelector('#continuar').addEventListener('click', () => {
  if (validarPrimeiraEtapa()) mudarEtapa(2);
});
document.querySelector('#voltar').addEventListener('click', () => mudarEtapa(1));

// Os contadores ajudam a pessoa a perceber o limite sem encher a tela de instruções.
for (const [campo, contador] of [[outraPreferencia, '#contador-preferencia'], [ajudaComunicacao, '#contador-comunicacao']]) {
  campo.addEventListener('input', () => {
    document.querySelector(contador).textContent = `${campo.value.length} / 400`;
  });
}

formulario.addEventListener('submit', async evento => {
  evento.preventDefault();
  // Enter na primeira etapa deve avançar, em vez de tentar enviar cedo demais.
  if (!document.querySelector('#etapa-1').hidden) {
    if (validarPrimeiraEtapa()) mudarEtapa(2);
    return;
  }
  if (enviando) return;
  const estado = formulario.querySelector('input[name="estado"]:checked')?.value;
  if (!estado) {
    mostrarErro('Escolha como está sua comunicação agora.');
    formulario.querySelector('input[name="estado"]').focus();
    return;
  }
  enviando = true;
  enviar.disabled = true;
  document.querySelector('#voltar').disabled = true;
  enviar.textContent = 'Enviando…';
  mostrarErro('');
  try {
    const resultado = await requisitar('/api/atendimentos', {
      metodo: 'POST', dados: {
        nome: nome.value.trim(), escolhas: lerEscolhas(), estado,
        outra_preferencia: outraPreferencia.value.trim(),
        ajuda_comunicacao: ajudaComunicacao.value.trim(),
      },
    });
    formulario.hidden = true;
    document.querySelector('#progresso').hidden = true;
    document.querySelector('#confirmacao').hidden = false;
    // textContent mantém qualquer texto digitado como texto, sem executar HTML.
    document.querySelector('#confirmacao-nome').textContent = `${resultado.nome}, suas informações foram enviadas à recepção.`;
    document.querySelector('#numero-atendimento').textContent = `#${resultado.numero}`;
    document.querySelector('#titulo-confirmacao').focus();
    window.scrollTo({ top: 0, behavior: 'auto' });
  } catch (erro) {
    // Conserva os campos para não obrigar a pessoa a preencher novamente.
    mostrarErro(erro.message);
  } finally {
    enviando = false;
    enviar.disabled = false;
    document.querySelector('#voltar').disabled = false;
    enviar.textContent = 'Enviar para a recepção';
  }
});

document.querySelector('#novo').addEventListener('click', () => {
  formulario.reset();
  document.querySelector('#contador-preferencia').textContent = '0 / 400';
  document.querySelector('#contador-comunicacao').textContent = '0 / 400';
  formulario.hidden = false;
  document.querySelector('#progresso').hidden = false;
  document.querySelector('#confirmacao').hidden = true;
  mudarEtapa(1);
});
