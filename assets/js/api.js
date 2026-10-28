// Centraliza a comunicação com o servidor.

const API_BASE_URL = (window.EMPATIZE_API_URL || '')
    .trim()
    .replace(/\/+$/, '');

export async function requisitar(
    caminho,
    { metodo = 'GET', dados, timeout = 26000 } = {}
) {
    const controlador = new AbortController();

    const temporizador = setTimeout(
        () => controlador.abort(),
        timeout
    );

    try {
        const resposta = await fetch(`${API_BASE_URL}${caminho}`, {
            method: metodo,

            headers: dados === undefined
                ? {}
                : { 'Content-Type': 'application/json' },

            body: dados === undefined
                ? undefined
                : JSON.stringify(dados),

            signal: controlador.signal,
            cache: 'no-store'
        });

        // Lê a resposta do servidor.
        const tipo = resposta.headers.get('content-type') || '';

        const resultado = tipo.includes('application/json')
            ? await resposta.json()
            : {};

        // Trata erros retornados pela API.
        if (!resposta.ok) {
            throw new Error(
                resultado.erro || 'Não foi possível concluir a solicitação.'
            );
        }

        return resultado;

    } catch (erro) {
        // Trata o tempo limite da solicitação.
        if (erro.name === 'AbortError') {
            throw new Error('A resposta demorou demais. Tente novamente.');
        }

        // Trata falhas de conexão.
        if (erro instanceof TypeError) {
            if (
                !API_BASE_URL &&
                location.hostname.endsWith('github.io')
            ) {
                throw new Error(
                    'Configure o endereço do backend em assets/js/config.js para conectar o Empatize ao servidor.'
                );
            }

            throw new Error(
                'Não foi possível conectar ao servidor. Verifique o endereço e se a API está disponível.'
            );
        }

        throw erro;

    } finally {
        // Cancela o temporizador ao finalizar a solicitação.
        clearTimeout(temporizador);
    }
}