"""Valida os dados também no servidor: a validação do navegador pode ser contornada."""
from .config import ESTADOS, LIMITE_NOME, LIMITE_TEXTO, PREFERENCIAS


class DadosInvalidos(ValueError):
    """Erro que pode ser mostrado à pessoa sem expor detalhes internos."""


def ler_texto(dados, campo, limite):
    valor = dados.get(campo, "")
    if not isinstance(valor, str):
        raise DadosInvalidos("Os campos de texto precisam conter texto.")
    valor = valor.strip()
    if len(valor) > limite:
        raise DadosInvalidos(f"O campo {campo} excede o limite de {limite} caracteres.")
    return valor


def validar_atendimento(dados):
    if not isinstance(dados, dict):
        raise DadosInvalidos("Envie uma solicitação válida.")
    nome = ler_texto(dados, "nome", LIMITE_NOME)
    outra_preferencia = ler_texto(dados, "outra_preferencia", LIMITE_TEXTO)
    ajuda_comunicacao = ler_texto(dados, "ajuda_comunicacao", LIMITE_TEXTO)
    if not nome:
        raise DadosInvalidos("Informe como podemos chamar você.")
    escolhas = dados.get("escolhas")
    # Verificamos os tipos antes de usar set(), para evitar erros com entradas inválidas.
    if (not isinstance(escolhas, list) or len(escolhas) > len(PREFERENCIAS)
            or any(not isinstance(x, str) or x not in PREFERENCIAS for x in escolhas)
            or len(set(escolhas)) != len(escolhas)):
        raise DadosInvalidos("As preferências selecionadas são inválidas.")
    # A pessoa pode ter só uma necessidade diferente: não forçamos uma opção pronta.
    if not escolhas and not outra_preferencia:
        raise DadosInvalidos("Escolha uma preferência ou escreva o que você precisa.")
    estado = dados.get("estado")
    if not isinstance(estado, str) or estado not in ESTADOS:
        raise DadosInvalidos("Escolha como está sua comunicação agora.")
    return {"nome": nome, "escolhas": escolhas, "estado": estado,
            "outra_preferencia": outra_preferencia, "ajuda_comunicacao": ajuda_comunicacao}
