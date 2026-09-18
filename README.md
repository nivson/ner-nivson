# Extração de atributos de produtos a partir do título (NER)

Reconhecimento de entidades nomeadas aplicado a títulos de produtos de
e-commerce, para preenchimento automático do cadastro no momento em que o
vendedor digita o título.

## Autor

Nivson - SEU EMAIL

## Base escolhida

`data/raw/cellphone.ibyte.json` — 1326 produtos capturados, **1032 títulos
únicos** após limpeza e deduplicação.

A base foi escolhida por ser a mais próxima do exemplo do enunciado
(`iphone 14 128gb vermelho`) e por concentrar muitos atributos por título:
armazenamento, memória RAM, cor, tela, rede, câmera e código do fabricante.

## Esquema de entidades

`TIPO`, `MARCA`, `MODELO`, `COMPATIBILIDADE`, `MEMORIA`, `RAM`, `COR`, `TELA`,
`REDE`, `CAMERA`, `BATERIA`, `POTENCIA`, `CODIGO`.

As definições e as regras de desempate estão em
[`docs/guia-anotacao.md`](docs/guia-anotacao.md). A decisão central do esquema é
separar `MODELO` (produto vendido) de `COMPATIBILIDADE` (aparelho a que o
acessório se destina), já que aproximadamente metade da base é de acessórios.

## Estratégia de anotação

1. **Pré-anotação por regras** (`src/preanotacao.py`): dicionário de marcas
   extraído do próprio campo `brand` do microdata, mais expressões regulares
   para os atributos numéricos e um gazetteer de cores e tipos.
2. **Revisão manual no Doccano** sobre o rascunho gerado, em vez de anotação do
   zero.
3. **Amostragem estratificada** por categoria: 400 títulos revisados
   manualmente, preservando a proporção entre produto principal e acessórios.
   O tamanho da amostra é justificado pela curva de aprendizado no notebook de
   avaliação.
4. O restante da base fica como conjunto não anotado, usado para inspeção
   qualitativa das predições.

O mesmo componente de regras é reaproveitado como **baseline** na comparação
experimental.

## Estrutura

```
data/raw/              bases brutas (microdata da ibyte)
data/annotations/      anotações no formato JSONL do Doccano
docs/guia-anotacao.md  definição das tags e regras de decisão
notebooks/             exploração, anotação, treinamento e avaliação
src/                   código compartilhado entre os notebooks
scripts/               subida do Doccano em container
```

## Notebooks

| Notebook | Conteúdo |
|---|---|
| `01_exploracao_dados.ipynb` | leitura do microdata, deduplicação, estatísticas, vocabulário |
| `02_preanotacao_regras.ipynb` | regras, geração do rascunho e amostragem para revisão |

## Execução

```bash
pip install -r requirements.txt
jupyter notebook notebooks/
```

## Doccano

```bash
chmod +x scripts/*.sh
./scripts/0.setup-doccano.sh
./scripts/1.start-doccano.sh
```

Acesse `localhost:8000` (usuário `admin`, senha `password`), crie um projeto do
tipo *Sequence Labeling* e importe o arquivo em **Dataset → Actions → Import
Dataset**, com formato `JSONL` e coluna de rótulo `entities`.
