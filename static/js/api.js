// Centraliza as chamadas HTTP. As telas cuidam da interface, este módulo cuida da rede.
export async function requisitar(caminho, { metodo = 'GET', dados, timeout = 26000 } = {}) {
  const controlador = new AbortController();
  const temporizador = setTimeout(() => controlador.abort(), timeout);
  try {
    const resposta = await fetch(caminho, {
      method: metodo,
      headers: dados === undefined ? {} : { 'Content-Type': 'application/json' },
      body: dados === undefined ? undefined : JSON.stringify(dados),
      signal: controlador.signal,
      cache: 'no-store',
    });
    const resultado = await resposta.json();
    if (!resposta.ok) throw new Error(resultado.erro || 'Não foi possível concluir a solicitação.');
    return resultado;
  } catch (erro) {
    if (erro.name === 'AbortError') throw new Error('A resposta demorou demais. Tente novamente.');
    if (erro instanceof TypeError) throw new Error('Não foi possível conectar ao servidor. Verifique se ele está aberto.');
    throw erro;
  } finally {
    clearTimeout(temporizador);
  }
}
