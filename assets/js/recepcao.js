// Controla o painel da recepção.

import { requisitar } from './api.js';

// Elementos do painel.
const lista = document.querySelector('#lista');
const aviso = document.querySelector('#aviso');

// Nomes das preferências.
const preferenciaRotulos = {
    som: 'Menos barulho',
    instrucoes: 'Instruções claras',
    toque: 'Avisar antes de tocar',
    espera: 'Previsão de espera'
};

// Descrição dos estados de comunicação.
const estadoRotulos = {
    verde: 'Consigo me comunicar',
    amarelo: 'Estou ficando sobrecarregado(a)',
    vermelho: 'Estou com dificuldade para me comunicar'
};

let ultimaLista = '';
let carregando = false;

const ocupados = new Set();


// Cria elementos com texto seguro.
function elemento(tag, texto = '', classe = '') {
    const item = document.createElement(tag);

    item.textContent = texto;

    if (classe) {
        item.className = classe;
    }

    return item;
}


// Adiciona textos opcionais ao cartão.
function adicionarTextoLivre(cartao, titulo, texto) {
    if (!texto) {
        return;
    }

    cartao.append(
        elemento('h3', titulo),
        elemento('p', texto, 'free-text')
    );
}


// Cria o cartão de atendimento.
function criarCartao(atendimento) {
    const cartao = elemento('article', '', 'attendance');

    cartao.dataset.numero = atendimento.numero;

    cartao.append(
        elemento('p', `Atendimento #${atendimento.numero}`, 'number'),
        elemento('h2', atendimento.nome),
        elemento(
            'p',
            estadoRotulos[atendimento.estado] || 'Estado não informado',
            'state'
        )
    );

    // Exibe as preferências selecionadas.
    cartao.append(elemento('h3', 'Preferências informadas'));

    if (atendimento.escolhas.length) {
        const preferencias = elemento('ul');

        for (const chave of atendimento.escolhas) {
            preferencias.append(
                elemento('li', preferenciaRotulos[chave] || chave)
            );
        }

        cartao.append(preferencias);
    }

    // Exibe as informações adicionais.
    adicionarTextoLivre(
        cartao,
        'Outra preferência',
        atendimento.outra_preferencia
    );

    adicionarTextoLivre(
        cartao,
        'O que ajuda na comunicação',
        atendimento.ajuda_comunicacao
    );

    // Área de orientações de acolhimento.
    const bloco = elemento('div', '', 'ai-block');

    bloco.append(
        elemento('p', 'Assistente de acolhimento', 'ai-label'),
        elemento(
            'p',
            'As orientações apoiam a equipe. Confirme o que é possível oferecer e respeite as escolhas da pessoa.',
            'ai-disclaimer'
        )
    );

    if (atendimento.ia_status === 'concluida') {
        const dicas = elemento('ul');

        for (const dica of atendimento.orientacoes || []) {
            dicas.append(elemento('li', dica));
        }

        bloco.append(dicas);

    } else {
        if (atendimento.ia_erro) {
            bloco.append(
                elemento('p', atendimento.ia_erro, 'ai-error')
            );
        }

        const botao = elemento(
            'button',
            atendimento.ia_status === 'gerando'
                ? 'Gerando orientação…'
                : 'Gerar orientação de acolhimento',
            'button primary'
        );

        botao.type = 'button';
        botao.disabled = atendimento.ia_status === 'gerando';

        // Solicita orientações ao servidor.
        botao.addEventListener('click', async () => {
            ocupados.add(atendimento.numero);

            botao.disabled = true;
            botao.textContent = 'Gerando orientação…';
            aviso.textContent = '';

            try {
                await requisitar(
                    `/api/atendimentos/${atendimento.numero}/orientacoes`,
                    { metodo: 'POST' }
                );

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

    // Botão para encerrar o atendimento.
    const encerrar = elemento(
        'button',
        'Encerrar e remover atendimento',
        'button text-button end-button'
    );

    encerrar.type = 'button';

    encerrar.addEventListener('click', async () => {
        const confirmar = window.confirm(
            `Encerrar o atendimento #${atendimento.numero} e remover os dados?`
        );

        if (!confirmar) {
            return;
        }

        encerrar.disabled = true;

        try {
            await requisitar(
                `/api/atendimentos/${atendimento.numero}`,
                { metodo: 'DELETE' }
            );

            await atualizar(true);

            aviso.textContent =
                `Atendimento #${atendimento.numero} encerrado.`;

        } catch (erro) {
            aviso.textContent = erro.message;
            encerrar.disabled = false;
        }
    });

    cartao.append(encerrar);

    return cartao;
}


// Atualiza a lista de atendimentos.
async function atualizar(forcar = false) {
    // Evita consultas simultâneas.
    if (carregando || ocupados.size) {
        return;
    }

    carregando = true;

    try {
        const atendimentos = await requisitar('/api/atendimentos');
        const assinatura = JSON.stringify(atendimentos);

        document.querySelector('#total').textContent =
            atendimentos.length;

        if (assinatura !== ultimaLista || forcar) {
            // Guarda o foco atual.
            const foco = document.activeElement;
            const numero = foco?.closest('.attendance')?.dataset.numero;

            const classeBotao = foco?.classList.contains('end-button')
                ? '.end-button'
                : '.primary';

            // Atualiza os cartões.
            lista.replaceChildren(...atendimentos.map(criarCartao));

            if (!atendimentos.length) {
                lista.append(
                    elemento(
                        'p',
                        'Nenhuma solicitação por enquanto. Quando alguém enviar, ela aparece aqui.',
                        'empty'
                    )
                );
            }

            ultimaLista = assinatura;

            // Mantém o foco no atendimento anterior.
            if (numero) {
                lista
                    .querySelector(
                        `[data-numero="${numero}"] ${classeBotao}`
                    )
                    ?.focus();
            }
        }

    } catch (erro) {
        aviso.textContent = erro.message;

    } finally {
        carregando = false;
    }
}


// Atualiza a lista ao clicar no botão.
document.querySelector('#atualizar').addEventListener('click', () => {
    aviso.textContent = '';
    atualizar(true);
});


// Carrega os atendimentos ao abrir o painel.
atualizar();

// Atualiza a lista a cada cinco segundos.
setInterval(() => atualizar(), 5000);