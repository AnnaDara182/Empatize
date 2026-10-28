// Controla o formulário da pessoa atendida.

import { requisitar } from './api.js';

// Elementos do formulário.
const formulario = document.querySelector('#formulario');
const nome = document.querySelector('#nome');
const outraPreferencia = document.querySelector('#outra-preferencia');
const ajudaComunicacao = document.querySelector('#ajuda-comunicacao');
const mensagem = document.querySelector('#mensagem');
const enviar = document.querySelector('#enviar');

let enviando = false;


// Exibe mensagens de erro.
function mostrarErro(texto) {
    mensagem.textContent = texto;
    mensagem.hidden = !texto;
}


// Alterna entre as etapas do formulário.
function mudarEtapa(numero) {
    document.querySelector('#etapa-1').hidden = numero !== 1;
    document.querySelector('#etapa-2').hidden = numero !== 2;

    document.querySelector('#etapa-texto').textContent = `${numero} de 2`;
    document.querySelector('#etapa-barra').style.width = `${numero * 50}%`;

    document
        .querySelector('#progresso')
        .setAttribute('aria-label', `Etapa ${numero} de 2`);

    mostrarErro('');

    document.querySelector(`#titulo-${numero}`).focus();

    window.scrollTo({ top: 0, behavior: 'auto' });
}


// Retorna as opções selecionadas.
function lerEscolhas() {
    return [
        ...formulario.querySelectorAll('input[name="escolha"]:checked')
    ].map(campo => campo.value);
}


// Valida os campos da primeira etapa.
function validarPrimeiraEtapa() {
    if (!nome.value.trim()) {
        mostrarErro('Informe como podemos chamar você.');
        nome.focus();
        return false;
    }

    if (!lerEscolhas().length && !outraPreferencia.value.trim()) {
        mostrarErro('Escolha uma opção ou escreva sua preferência.');
        outraPreferencia.focus();
        return false;
    }

    return true;
}


// Avança para a segunda etapa.
document.querySelector('#continuar').addEventListener('click', () => {
    if (validarPrimeiraEtapa()) {
        mudarEtapa(2);
    }
});


// Volta para a primeira etapa.
document.querySelector('#voltar').addEventListener('click', () => {
    mudarEtapa(1);
});


// Atualiza os contadores de caracteres.
for (const [campo, contador] of [
    [outraPreferencia, '#contador-preferencia'],
    [ajudaComunicacao, '#contador-comunicacao']
]) {
    campo.addEventListener('input', () => {
        document.querySelector(contador).textContent =
            `${campo.value.length} / 400`;
    });
}


// Envia os dados do formulário.
formulario.addEventListener('submit', async evento => {
    evento.preventDefault();

    // Avança de etapa se o formulário ainda estiver na primeira.
    if (!document.querySelector('#etapa-1').hidden) {
        if (validarPrimeiraEtapa()) {
            mudarEtapa(2);
        }

        return;
    }

    // Evita envios duplicados.
    if (enviando) {
        return;
    }

    const estado = formulario.querySelector(
        'input[name="estado"]:checked'
    )?.value;

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
        // Envia os dados para o servidor.
        const resultado = await requisitar('/api/atendimentos', {
            metodo: 'POST',
            dados: {
                nome: nome.value.trim(),
                escolhas: lerEscolhas(),
                estado,
                outra_preferencia: outraPreferencia.value.trim(),
                ajuda_comunicacao: ajudaComunicacao.value.trim()
            }
        });

        // Exibe a confirmação do atendimento.
        formulario.hidden = true;
        document.querySelector('#progresso').hidden = true;
        document.querySelector('#confirmacao').hidden = false;

        document.querySelector('#confirmacao-nome').textContent =
            `${resultado.nome}, suas informações foram enviadas à recepção.`;

        document.querySelector('#numero-atendimento').textContent =
            `#${resultado.numero}`;

        document.querySelector('#titulo-confirmacao').focus();

        window.scrollTo({ top: 0, behavior: 'auto' });

    } catch (erro) {
        // Exibe o erro sem apagar os dados preenchidos.
        mostrarErro(erro.message);

    } finally {
        // Libera os botões novamente.
        enviando = false;
        enviar.disabled = false;

        document.querySelector('#voltar').disabled = false;

        enviar.textContent = 'Enviar para a recepção';
    }
});


// Reinicia o formulário para um novo atendimento.
document.querySelector('#novo').addEventListener('click', () => {
    formulario.reset();

    document.querySelector('#contador-preferencia').textContent = '0 / 400';
    document.querySelector('#contador-comunicacao').textContent = '0 / 400';

    formulario.hidden = false;
    document.querySelector('#progresso').hidden = false;
    document.querySelector('#confirmacao').hidden = true;

    mudarEtapa(1);
});