"""
Leitura das bases brutas (microdata da ibyte) e escrita/leitura do formato JSONL
usado nas anotacoes.

Cada arquivo em data/raw/ e uma lista de registros; cada registro tem uma chave
"microdata" com varios objetos, entre eles um do tipo "Product" (nome, marca,
sku, descricao) e um "BreadcrumbList" (categoria).
"""

import json
import re
import unicodedata
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
DIR_RAW = RAIZ / "data" / "raw"
DIR_ANOT = RAIZ / "data" / "annotations"


def carregar_produtos(nome_base):
    """Extrai os objetos Product de uma base bruta.

    nome_base: "cellphone", "gamer", etc. (sem sufixo .ibyte.json)
    Retorna lista de dicionarios com titulo, marca, sku, categoria.
    """
    caminho = DIR_RAW / f"{nome_base}.ibyte.json"
    registros = json.loads(caminho.read_text(encoding="utf-8"))

    produtos = []
    for registro in registros:
        produto = None
        categoria = None
        for bloco in registro.get("microdata", []):
            tipo = bloco.get("@type")
            if tipo == "Product":
                produto = bloco
            elif tipo == "BreadcrumbList":
                itens = bloco.get("itemListElement", [])
                if itens:
                    categoria = itens[-1].get("name")
        if produto is None:
            continue

        marca = produto.get("brand")
        if isinstance(marca, dict):
            marca = marca.get("name")

        produtos.append({
            "titulo": limpar_titulo(produto.get("name", "")),
            "marca": (marca or "").strip(),
            "sku": (produto.get("sku") or "").strip(),
            "categoria": categoria,
        })
    return produtos


def limpar_titulo(texto):
    """Remove quebras de linha, espacos duplicados e espacos nas pontas."""
    texto = texto.replace("\r", " ").replace("\n", " ")
    texto = re.sub(r"\s+", " ", texto)
    return texto.strip()


def normalizar(texto):
    """Minusculas e sem acentos, para casamento de dicionarios."""
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    return texto.lower()


def titulos_unicos(produtos, tamanho_minimo=10):
    """Deduplica titulos preservando a ordem de aparicao."""
    vistos = set()
    saida = []
    for produto in produtos:
        titulo = produto["titulo"]
        chave = normalizar(titulo)
        if len(titulo) < tamanho_minimo or chave in vistos:
            continue
        vistos.add(chave)
        saida.append(produto)
    return saida


def marcas_do_catalogo(produtos):
    """Dicionario de marcas declaradas no campo brand do catalogo."""
    marcas = set()
    for produto in produtos:
        marca = produto["marca"]
        if marca and len(marca) > 1:
            marcas.add(marca.strip())
    return sorted(marcas)


def salvar_jsonl(registros, caminho):
    caminho = Path(caminho)
    caminho.parent.mkdir(parents=True, exist_ok=True)
    with caminho.open("w", encoding="utf-8") as arquivo:
        for registro in registros:
            arquivo.write(json.dumps(registro, ensure_ascii=False) + "\n")
    return caminho


def carregar_jsonl(caminho):
    with Path(caminho).open(encoding="utf-8") as arquivo:
        return [json.loads(linha) for linha in arquivo if linha.strip()]
