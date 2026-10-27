// Adaptador de demonstração para GitHub Pages.
// O Pages hospeda apenas arquivos estáticos: não executa o servidor Python.
// Por isso, este arquivo simula as rotas usando localStorage neste navegador.
// Os dados NÃO são compartilhados entre dispositivos e não devem ser reais/sensíveis.

const CHAVE = 'empatize_demo_atendimentos';
const CHAVE_NUMERO = 'empatize_demo_proximo_numero';
const TEMPO_EXPIRACAO = 2 * 60 * 60 * 1000;

function lerAtendimentos() {
  try {
    const agora = Date.now();
    const atendimentos = JSON.parse(localStorage.getItem(CHAVE) || '[]');
    const validos = atendimentos.filter(item => agora - item.criadoEm < TEMPO_EXPIRACAO);
    localStorage.setItem(CHAVE, JSON.stringify(validos));
    return validos;
  } catch {
    return [];
  }
}

function salvarAtendimentos(atendimentos) {
  localStorage.setItem(CHAVE, JSON.stringify(atendimentos));
}

function criarOrientacoes(atendimento) {
  // Sugestões fixas apenas para demonstrar o fluxo. Não são geradas por uma IA.
  const dicas = [];
  if (atendimento.escolhas.includes('som')) dicas.push('Se possível, reduza ruídos e converse em um local mais tranquilo.');
  if (atendimento.escolhas.includes('instrucoes')) dicas.push('Use frases curtas e instruções claras, uma etapa de cada vez.');
  if (atendimento.escolhas.includes('toque')) dicas.push('Avise antes de qualquer contato físico e aguarde a resposta da pessoa.');
  if (atendimento.escolhas.includes('espera')) dicas.push('Explique a previsão de espera e avise se houver mudanças.');
  if (atendimento.estado === 'amarelo') dicas.push('Fale com calma e ofereça tempo ou uma pausa, se possível.');
  if (atendimento.estado === 'vermelho') dicas.push('Faça perguntas simples, permita respostas não verbais e evite pressionar.');
  if (atendimento.outra_preferencia.trim()) dicas.push('Leia e considere a preferência adicional escrita pela pessoa.');
  if (atendimento.ajuda_comunicacao.trim()) dicas.push('Considere a orientação que a pessoa informou sobre o que pode ajudá-la.');
  if (!dicas.length) dicas.push('Pergunte com respeito como a pessoa prefere receber ajuda e siga suas orientações.');
  return dicas.slice(0, 3);
}

export async function requisitar(caminho, { metodo = 'GET', dados } = {}) {
  // Pequena pausa para manter a sensação de uma requisição durante a demonstração.
  await new Promise(resolve => setTimeout(resolve, 120));

  const atendimentos = lerAtendimentos();

  if (caminho === '/api/atendimentos' && metodo === 'GET') {
    return atendimentos.sort((a, b) => b.numero - a.numero);
  }

  if (caminho === '/api/atendimentos' && metodo === 'POST') {
    if (!dados || !dados.nome || !dados.estado) {
      throw new Error('Confira os campos obrigatórios e tente novamente.');
    }
    const numero = Number(localStorage.getItem(CHAVE_NUMERO) || '1');
    const atendimento = {
      ...dados,
      numero,
      criadoEm: Date.now(),
      ia_status: 'pendente',
      orientacoes: [],
      ia_erro: '',
    };
    atendimentos.push(atendimento);
    salvarAtendimentos(atendimentos);
    localStorage.setItem(CHAVE_NUMERO, String(numero + 1));
    return { numero, nome: atendimento.nome };
  }

  const rotaOrientacoes = caminho.match(/^\/api\/atendimentos\/(\d+)\/orientacoes$/);
  if (rotaOrientacoes && metodo === 'POST') {
    const numero = Number(rotaOrientacoes[1]);
    const atendimento = atendimentos.find(item => item.numero === numero);
    if (!atendimento) throw new Error('Esse atendimento expirou ou não foi encontrado.');
    atendimento.ia_status = 'concluida';
    atendimento.orientacoes = criarOrientacoes(atendimento);
    salvarAtendimentos(atendimentos);
    return atendimento;
  }

  const rotaEncerrar = caminho.match(/^\/api\/atendimentos\/(\d+)$/);
  if (rotaEncerrar && metodo === 'DELETE') {
    const numero = Number(rotaEncerrar[1]);
    const restantes = atendimentos.filter(item => item.numero !== numero);
    if (restantes.length === atendimentos.length) throw new Error('Atendimento não encontrado.');
    salvarAtendimentos(restantes);
    return { mensagem: 'Atendimento encerrado e removido.' };
  }

  throw new Error('Ação não disponível nesta demonstração.');
}
