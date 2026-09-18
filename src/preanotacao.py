"""
Pre-anotacao das entidades por regras (dicionarios + expressoes regulares).

Serve para dois propositos:
  1. gerar um rascunho de anotacao que e revisado manualmente no Doccano,
     reduzindo o esforco de anotacao do zero;
  2. funcionar como baseline na comparacao com os modelos aprendidos.

As entidades produzidas seguem o formato [inicio, fim, TAG], com offsets de
caractere sobre o titulo original.
"""

import re

from .dados import normalizar

# ---------------------------------------------------------------------------
# Dicionarios
# ---------------------------------------------------------------------------

TIPOS = [
    "smartphone", "celular simples", "celular", "telefone sem fio", "telefone",
    "capa com magsafe", "capa protetora", "capa carteira", "capa flip", "capa",
    "case", "bumper", "capinha",
    "pelicula de vidro", "pelicula de hydrogel", "pelicula protetora",
    "pelicula 3d", "pelicula", "protetor de tela",
    "carregador sem fio", "carregador de parede", "carregador veicular",
    "carregador portatil", "carregador", "base carregadora",
    "fone de ouvido", "fone", "headset", "earbuds",
    "cabo usb-c", "cabo lightning", "cabo micro usb", "cabo",
    "adaptador", "power bank", "bateria externa", "bateria",
    "suporte veicular", "suporte", "apoio", "apoio para smartphone",
    "caixa de som", "smartwatch", "relogio inteligente", "pulseira",
    "cartao de memoria", "kit", "selfie stick", "bastao de selfie",
    "anel suporte", "pop socket", "caneta touch", "estabilizador",
]

CORES = [
    "preto fosco", "preto espacial", "preto-espacial", "preto",
    "branco", "azul pacifico", "azul-pacifico", "azul marinho", "azul escuro",
    "azul claro", "azul", "vermelho", "verde escuro", "verde claro", "verde",
    "amarelo", "rosa claro", "rosa", "roxo profundo", "roxo-profundo", "roxo",
    "cinza espacial", "cinza", "prata", "prateado", "dourado", "rose gold",
    "grafite", "coral", "lilas", "bege", "marrom", "transparente", "incolor",
    "titanio", "meia-noite", "meia noite", "estelar", "creme", "laranja",
    "turquesa", "violeta", "champagne", "chumbo", "fume", "nude", "vinho",
]

# Familias de modelo mais frequentes nas bases de celular.
PADROES_MODELO = [
    r"iphone\s+(?:se|xr|xs\s+max|xs|x)\b(?:\s+(?:plus|pro\s+max|pro|mini))?",
    r"iphone\s+\d{1,2}(?:\s+(?:pro\s+max|pro|plus|mini))?",
    r"galaxy\s+(?:z\s+)?(?:flip|fold)\s*\d*",
    r"galaxy\s+(?:note\s*)?[a-z]{1,2}\d{1,3}[a-z]*(?:\s+(?:plus|ultra|\+))?",
    r"moto\s+[a-z]\d{1,3}[a-z]*(?:\s+(?:plus|power|play|neo|5g))?",
    r"moto\s+(?:edge|razr)\s*\d*(?:\s+(?:pro|plus))?",
    r"redmi\s+(?:note\s+)?\d{1,2}[a-z]*(?:\s+(?:pro|plus))?",
    r"poco\s+[a-z]\d{1,2}(?:\s+pro)?",
    r"\bxt\d{4}\b",
    # modelo citado logo apos a marca, sem o nome da familia
    r"(?<=motorola\s)(?:moto\s)?[a-z]{1,4}\d{1,3}[a-z]*(?:\s(?:plus|power|play|neo))?",
    r"(?<=nokia\s)[a-z]{1,2}\d{2,3}(?:\s(?:plus|pro))?",
    r"(?<=philco\s)hit\s[a-z]?\d{1,3}",
    r"(?<=positivo\s)[a-z]{1,2}\d{3,4}",
]

# ---------------------------------------------------------------------------
# Construcao das expressoes regulares
# ---------------------------------------------------------------------------


def _alternativa(termos):
    """Regex de alternancia com os termos mais longos primeiro."""
    ordenados = sorted(termos, key=len, reverse=True)
    return "|".join(re.escape(t).replace(r"\ ", r"\s+") for t in ordenados)


REGEX_ESTATICAS = [
    # (tag, padrao, prioridade) - prioridade maior vence em caso de empate
    ("MEMORIA", r"\b\d{1,4}\s?(?:gb|tb|mb)\b(?!\s*(?:de\s+)?ram)", 5),
    ("RAM", r"\b\d{1,3}\s?gb\s*(?:de\s+)?ram\b", 6),
    ("RAM", r"\bram\s*\d{1,3}\s?gb\b", 6),
    ("REDE", r"\b[2345]g\b", 5),
    ("TELA", r"\btela\s*(?:de\s*)?\d{1,2}(?:[.,]\d{1,2})?\s*(?:pol\.?|polegadas|\"|”)?", 4),
    ("TELA", r"\b\d{1,2}(?:[.,]\d{1,2})?\s*(?:pol\.?|polegadas|\"|”)", 4),
    ("CAMERA", r"\b\d{1,3}(?:[.,]\d)?\s?mp\b", 5),
    ("BATERIA", r"\b\d{3,5}\s?mah\b", 5),
    ("POTENCIA", r"\b\d{1,4}\s?w\b", 5),
    ("POTENCIA", r"\bbivolt\b|\b(?:110|220)\s?v\b", 5),
    ("CODIGO", r"\b[A-Z]{1,3}-?\d{3,5}\b", 3),
    ("CODIGO", r"\b[A-Z0-9]{5,}/[A-Z]\b", 5),
    ("COR", rf"\b(?:{_alternativa(CORES)})\b", 2),
    ("TIPO", rf"\b(?:{_alternativa(TIPOS)})\b", 1),
    ("MODELO", "|".join(PADROES_MODELO), 4),
]


def _regex_marcas(marcas):
    if not marcas:
        return None
    return re.compile(rf"\b(?:{_alternativa([normalizar(m) for m in marcas])})\b")


# ---------------------------------------------------------------------------
# Anotacao
# ---------------------------------------------------------------------------


def _candidatos(titulo, marcas_regex):
    """Lista de (inicio, fim, tag, prioridade) sobre o titulo."""
    texto = normalizar(titulo)
    achados = []

    for tag, padrao, prioridade in REGEX_ESTATICAS:
        for encontro in re.finditer(padrao, texto, flags=re.IGNORECASE):
            achados.append((encontro.start(), encontro.end(), tag, prioridade))

    if marcas_regex is not None:
        for encontro in marcas_regex.finditer(texto):
            achados.append((encontro.start(), encontro.end(), "MARCA", 7))

    return _filtrar_tipo(achados)


def _filtrar_tipo(achados):
    """O tipo do produto aparece uma vez, quase sempre no inicio do titulo.

    Mantem apenas o candidato mais a esquerda (o mais longo, em caso de empate)
    e descarta ocorrencias posteriores, que costumam ser atributo e nao tipo
    (por exemplo "Dual Chip", "Suporte" dentro de descricao de acessorio).
    """
    tipos = [c for c in achados if c[2] == "TIPO"]
    outros = [c for c in achados if c[2] != "TIPO"]
    if not tipos:
        return outros
    melhor = min(tipos, key=lambda c: (c[0], -(c[1] - c[0])))
    return outros + [melhor]


def _resolver_sobreposicao(candidatos):
    """Mantem o maior span; empate resolvido pela prioridade da regra."""
    ordenados = sorted(
        candidatos,
        key=lambda c: (c[1] - c[0], c[3]),
        reverse=True,
    )
    aceitos = []
    for inicio, fim, tag, _ in ordenados:
        conflito = any(inicio < f and i < fim for i, f, _ in aceitos)
        if not conflito:
            aceitos.append((inicio, fim, tag))
    return sorted(aceitos)


def _ajustar_bordas(titulo, inicio, fim):
    """Remove espacos e pontuacao nas pontas do span."""
    while inicio < fim and not titulo[inicio].isalnum():
        inicio += 1
    while fim > inicio and not titulo[fim - 1].isalnum():
        fim -= 1
    return inicio, fim


def anotar_titulo(titulo, marcas_regex=None, marcar_compatibilidade=True):
    """Retorna a lista de entidades [inicio, fim, TAG] para um titulo."""
    entidades = []
    for inicio, fim, tag in _resolver_sobreposicao(_candidatos(titulo, marcas_regex)):
        inicio, fim = _ajustar_bordas(titulo, inicio, fim)
        if fim <= inicio:
            continue
        # Em acessorios, o modelo citado apos "para" e compatibilidade,
        # nao o produto em si (ver guia de anotacao).
        if marcar_compatibilidade and tag == "MODELO":
            anterior = normalizar(titulo[max(0, inicio - 25):inicio])
            if re.search(r"\b(para|compativel\s+com|compativeis\s+com)\b[\s\w]{0,12}$", anterior):
                tag = "COMPATIBILIDADE"
        entidades.append([inicio, fim, tag])
    return entidades


def anotar_base(produtos, marcas, marcar_compatibilidade=True):
    """Aplica a pre-anotacao em toda a base, no formato do Doccano."""
    marcas_regex = _regex_marcas(marcas)
    saida = []
    for produto in produtos:
        titulo = produto["titulo"]
        saida.append({
            "text": titulo,
            "entities": anotar_titulo(titulo, marcas_regex, marcar_compatibilidade),
        })
    return saida
