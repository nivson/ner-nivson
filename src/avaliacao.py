"""
Conversao entre o formato de offsets (Doccano) e o formato BIO por token, e
metricas de avaliacao em nivel de span.

A avaliacao e estrita: um acerto exige que inicio, fim e tag coincidam com a
referencia. Marcar "128" quando a referencia diz "128GB" conta como erro, e nao
como acerto parcial.
"""

import re
from collections import defaultdict

PADRAO_TOKEN = re.compile(r"\w+|[^\w\s]", re.UNICODE)


def tokenizar(texto):
    """Divide o texto em tokens preservando o offset de cada um."""
    return [(m.group(), m.start(), m.end()) for m in PADRAO_TOKEN.finditer(texto)]


def para_bio(registro):
    """Converte {'text', 'entities'} em (tokens, rotulos BIO)."""
    tokens = tokenizar(registro["text"])
    rotulos = ["O"] * len(tokens)

    for inicio, fim, tag in registro["entities"]:
        primeiro = True
        for indice, (_, ini_tok, fim_tok) in enumerate(tokens):
            if ini_tok >= inicio and fim_tok <= fim:
                rotulos[indice] = ("B-" if primeiro else "I-") + tag
                primeiro = False

    return [t[0] for t in tokens], rotulos


def de_bio(texto, rotulos):
    """Reconstroi a lista de entidades [inicio, fim, TAG] a partir do BIO."""
    tokens = tokenizar(texto)
    entidades = []
    atual = None

    for (_, ini_tok, fim_tok), rotulo in zip(tokens, rotulos):
        if rotulo.startswith("B-"):
            if atual:
                entidades.append(atual)
            atual = [ini_tok, fim_tok, rotulo[2:]]
        elif rotulo.startswith("I-") and atual and atual[2] == rotulo[2:]:
            atual[1] = fim_tok
        else:
            if atual:
                entidades.append(atual)
            atual = None

    if atual:
        entidades.append(atual)
    return entidades


def _conjunto(registros):
    """Spans de todos os registros, identificados pelo indice do titulo."""
    saida = set()
    for indice, registro in enumerate(registros):
        for inicio, fim, tag in registro["entities"]:
            saida.add((indice, inicio, fim, tag))
    return saida


def avaliar(referencia, predicao):
    """Precisao, revocacao e F1 por tag e no agregado.

    referencia e predicao sao listas de {'text', 'entities'} na mesma ordem.
    """
    if len(referencia) != len(predicao):
        raise ValueError("as listas precisam ter o mesmo tamanho e a mesma ordem")

    esperados = _conjunto(referencia)
    obtidos = _conjunto(predicao)

    por_tag = defaultdict(lambda: {"vp": 0, "fp": 0, "fn": 0})
    for span in esperados & obtidos:
        por_tag[span[3]]["vp"] += 1
    for span in obtidos - esperados:
        por_tag[span[3]]["fp"] += 1
    for span in esperados - obtidos:
        por_tag[span[3]]["fn"] += 1

    linhas = []
    for tag in sorted(por_tag):
        c = por_tag[tag]
        linhas.append({"tag": tag, **_metricas(c["vp"], c["fp"], c["fn"]),
                       "suporte": c["vp"] + c["fn"]})

    total_vp = sum(c["vp"] for c in por_tag.values())
    total_fp = sum(c["fp"] for c in por_tag.values())
    total_fn = sum(c["fn"] for c in por_tag.values())
    linhas.append({"tag": "micro", **_metricas(total_vp, total_fp, total_fn),
                   "suporte": total_vp + total_fn})

    tags = [l for l in linhas if l["tag"] != "micro"]
    if tags:
        linhas.append({
            "tag": "macro",
            "precisao": sum(l["precisao"] for l in tags) / len(tags),
            "revocacao": sum(l["revocacao"] for l in tags) / len(tags),
            "f1": sum(l["f1"] for l in tags) / len(tags),
            "suporte": total_vp + total_fn,
        })
    return linhas


def _metricas(vp, fp, fn):
    precisao = vp / (vp + fp) if vp + fp else 0.0
    revocacao = vp / (vp + fn) if vp + fn else 0.0
    f1 = 2 * precisao * revocacao / (precisao + revocacao) if precisao + revocacao else 0.0
    return {"precisao": precisao, "revocacao": revocacao, "f1": f1}


def erros(referencia, predicao, limite=30):
    """Lista os spans divergentes, para inspecao qualitativa."""
    esperados = _conjunto(referencia)
    obtidos = _conjunto(predicao)
    saida = []

    for indice, inicio, fim, tag in sorted(esperados - obtidos)[:limite]:
        texto = referencia[indice]["text"]
        saida.append({"titulo": texto, "trecho": texto[inicio:fim],
                      "esperado": tag, "obtido": "-", "tipo": "nao encontrado"})

    for indice, inicio, fim, tag in sorted(obtidos - esperados)[:limite]:
        texto = referencia[indice]["text"]
        saida.append({"titulo": texto, "trecho": texto[inicio:fim],
                      "esperado": "-", "obtido": tag, "tipo": "marcado a mais"})

    return saida
