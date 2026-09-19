# Extração de atributos de produtos a partir do título (NER)

Reconhecimento de entidades nomeadas aplicado a títulos de produtos de
e-commerce, para preenchimento automático do cadastro no momento em que o
vendedor digita o título.

## Autor

Nivson Jesus - nsj@cesar.school

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
2. **Revisão manual** sobre o rascunho gerado, em vez de anotação do zero, na
   ferramenta em `tools/anotador.html`.
3. **Amostragem estratificada** por categoria para o conjunto de teste: 49
   títulos revisados manualmente, preservando a proporção entre produto
   principal e acessórios.
4. Os 983 títulos restantes formam o conjunto de treino, com rótulo automático.
   A separação permite medir o efeito da qualidade da anotação sobre o
   resultado.

O mesmo componente de regras é reaproveitado como **baseline** na comparação
experimental.

## Estrutura

```
data/raw/              bases brutas (microdata da ibyte)
data/annotations/      anotações no formato JSONL
docs/guia-anotacao.md  definição das tags e regras de decisão
docs/resultados.md     relatório dos experimentos
notebooks/             exploração, anotação, treinamento e avaliação
src/                   código compartilhado entre os notebooks
tools/anotador.html    ferramenta de revisão das anotações
scripts/               subida do Doccano em container
```

## Resultados

Avaliação em nível de span estrito, contra 49 títulos revisados manualmente.

| Sistema | Títulos de treino | Micro F1 |
|---|---|---|
| Regras | 0 | 0,946 |
| CRF com rótulo automático | 983 | 0,938 |
| CRF com rótulo humano | 39 | 0,818 |

O CRF treinado com rótulo automático reproduz as regras que o rotularam, com F1
idêntico em oito das doze entidades, e a curva de aprendizado satura (0,002 de
ganho entre 600 e 983 títulos). Análise completa em
[`docs/resultados.md`](docs/resultados.md).

## Notebooks

| Notebook | Conteúdo |
|---|---|
| `01_exploracao_dados.ipynb` | leitura do microdata, deduplicação, estatísticas, vocabulário |
| `02_preanotacao_regras.ipynb` | regras, geração do rascunho e amostragem para revisão |
| `03_amostra_teste.ipynb` | separação treino/teste e medição do erro das regras |
| `04_regras_e_crf.ipynb` | baseline, CRF e curva de aprendizado |
| `05_rotulo_humano.ipynb` | validação cruzada com rótulo humano |

## Execução

```bash
pip install -r requirements.txt
jupyter notebook notebooks/
```

## Anotação

A revisão foi feita em `tools/anotador.html`, ferramenta construída para este
trabalho por indisponibilidade de Docker no ambiente. Ela roda no navegador sem
instalação, lê o JSONL pré-anotado e exporta no mesmo formato do Doccano, de
modo que as anotações permanecem compatíveis.

Para usar o Doccano em vez dela, os scripts originais continuam no repositório:

```bash
chmod +x scripts/*.sh
./scripts/0.setup-doccano.sh
./scripts/1.start-doccano.sh
```

Acesse `localhost:8000` (usuário `admin`, senha `password`), crie um projeto do
tipo *Sequence Labeling* e importe o arquivo em **Dataset → Actions → Import
Dataset**, com formato `JSONL` e coluna de rótulo `entities`.
