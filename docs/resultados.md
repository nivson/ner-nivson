# Resultados

Extração de atributos de produto a partir do título, base `cellphone.ibyte`
(1032 títulos únicos, 13 entidades definidas em [`guia-anotacao.md`](guia-anotacao.md)).

## Conjuntos de dados

| Conjunto | Títulos | Entidades | Origem do rótulo |
|---|---|---|---|
| Treino | 983 | 5499 | regras (notebook 02) |
| Teste | 49 | 311 | revisão manual |

A separação é deliberada. Todos os sistemas são avaliados contra o mesmo
conjunto de 49 títulos revisados à mão, que é a única referência confiável do
trabalho. O treino usa rótulo automático, barato e imperfeito, o que permite
medir o efeito da qualidade da anotação sobre o resultado.

A avaliação é estrita em nível de span: início, fim e tag precisam coincidir com
a referência. Marcar `128` onde a referência diz `128GB` conta como erro.

## Quanto as regras erram

Comparação entre a pré-anotação automática e a revisão manual dos mesmos 49
títulos.

| | |
|---|---|
| Títulos alterados na revisão | 21 de 49 (42,9%) |
| Entidades antes da revisão | 287 |
| Entidades depois da revisão | 311 |
| Precisão micro | 0,986 |
| Revocação micro | 0,910 |

O padrão é o esperado de um sistema baseado em dicionário e expressão regular:
**quase nunca marca errado, mas deixa de marcar**. As 24 entidades adicionadas na
revisão são, na maioria, modelos de marcas sem padrão mapeado e cores fora do
dicionário.

Por entidade, a revocação separa dois grupos com clareza:

| Entidade | Revocação | Suporte |
|---|---|---|
| CAMERA, MEMORIA, RAM, REDE, TIPO | 1,000 | 18 a 45 |
| MARCA | 0,961 | 51 |
| TELA | 0,917 | 24 |
| CODIGO | 0,905 | 21 |
| COMPATIBILIDADE | 0,882 | 17 |
| COR | 0,784 | 37 |
| MODELO | 0,686 | 35 |

Entidades de formato fixo são resolvidas integralmente por regra. Entidades de
vocabulário aberto (MODELO, COR) são onde a regra falha.

## Comparação dos sistemas

| Sistema | Títulos de treino | Micro F1 | Macro F1 |
|---|---|---|---|
| Regras | 0 | **0,946** | 0,870 |
| CRF com rótulo automático | 983 | 0,938 | 0,860 |
| CRF com rótulo humano | 39 | 0,818 | 0,747 |

Por entidade:

| Entidade | Suporte | Regras | CRF automático | CRF humano |
|---|---|---|---|---|
| MARCA | 51 | 0,970 | 0,960 | 0,875 |
| TIPO | 45 | 1,000 | 1,000 | 0,857 |
| COR | 37 | 0,866 | 0,866 | 0,677 |
| MODELO | 35 | 0,814 | 0,814 | 0,667 |
| MEMORIA | 31 | 1,000 | 0,967 | 0,951 |
| TELA | 24 | 0,957 | 0,957 | 0,826 |
| CODIGO | 21 | 0,950 | 0,950 | 0,889 |
| CAMERA | 18 | 1,000 | 1,000 | 0,750 |
| COMPATIBILIDADE | 17 | 0,882 | 0,812 | 0,571 |
| RAM | 16 | 1,000 | 1,000 | 0,938 |
| REDE | 15 | 1,000 | 1,000 | 0,968 |
| POTENCIA | 1 | 0,000 | 0,000 | 0,000 |

## Leitura dos resultados

**O CRF treinado com rótulo automático reproduz as regras.** F1 idêntico até a
terceira casa em oito das doze entidades, incluindo MODELO (0,814 nos dois) e
COR (0,866 nos dois). Não é coincidência: o modelo aprendeu com rótulos gerados
pelas regras, e casos que as regras não reconhecem nunca apareceram rotulados no
treino. O desempenho fica limitado pelo do rotulador.

**A curva de aprendizado confirma que o limite não é volume.** O CRF sai de 0,808
com 50 títulos e chega a 0,938 com 983, mas o ganho entre 600 e 983 é de apenas
0,002. Triplicar a base não tiraria o modelo desse patamar, porque adicionaria
mais rótulos com os mesmos erros.

**39 títulos revisados não compensam 983 automáticos.** O CRF treinado com rótulo
humano ficou em 0,818, bem abaixo das outras duas abordagens. A hipótese de que
qualidade superaria volume não se sustentou nessa escala.

**A perda do rótulo humano é desigual, e a desigualdade é informativa.** MEMORIA
(-0,016), REDE (-0,032) e RAM (-0,062) quase não sofrem, porque seu padrão está
na forma do token e é aprendido com poucos exemplos. COR (-0,188) e MODELO
(-0,147) desabam, porque dependem de o modelo ter visto cada valor do
vocabulário, e 39 títulos cobrem uma fração pequena dele.

**CAMERA (-0,250) é escassez absoluta, não dificuldade.** O padrão é rígido
(`13MP`), mas as 18 ocorrências distribuídas em 5 partições deixam cerca de 14
exemplos por treino.

**COMPATIBILIDADE é o caso difícil para os três sistemas** (0,882 / 0,812 /
0,571). Separar o modelo do produto do modelo do aparelho compatível exige saber
que o produto é um acessório, informação que está no início do título e
condiciona um span no meio. Features locais de token não alcançam essa
dependência.

## Conclusão

Nenhuma das três abordagens isoladas resolve o problema por completo, e cada uma
falha por um motivo diferente: a regra não tem vocabulário, o CRF com rótulo
automático herda o teto da regra, e o CRF com rótulo humano não tem dado
suficiente.

A composição mais eficiente observada é **regra para as entidades de formato
fixo** (MEMORIA, RAM, REDE, CAMERA, TIPO, todas entre 0,95 e 1,00) e
**aprendizado para as de vocabulário aberto**, desde que haja volume anotado. O
caminho natural de continuação seria treinar no conjunto automático e ajustar no
revisado, aproveitando cobertura e correção ao mesmo tempo.

## Limitações

- O conjunto de teste tem 49 títulos. Diferenças por entidade se apoiam em
  poucas ocorrências, e POTENCIA, com suporte 1, não sustenta conclusão alguma.
- A validação cruzada mede um regime de dados muito pequeno, e não permite
  extrapolar o desempenho do rótulo humano em escala maior.
- Parte dos títulos da base vem truncada no caractere de polegada, uma limitação
  da captura original que remove atributos do final de alguns títulos.
- A abordagem zero-shot não pôde ser avaliada por restrição de rede do ambiente,
  e fica registrada como continuação possível.

## Reprodução

```bash
pip install -r requirements.txt
jupyter notebook notebooks/
```

| Notebook | Conteúdo |
|---|---|
| `01_exploracao_dados.ipynb` | leitura do microdata, deduplicação, vocabulário |
| `02_preanotacao_regras.ipynb` | regras de pré-anotação e amostragem |
| `03_amostra_teste.ipynb` | separação treino/teste e medição do erro das regras |
| `04_regras_e_crf.ipynb` | baseline, CRF e curva de aprendizado |
| `05_rotulo_humano.ipynb` | validação cruzada com rótulo humano |

A revisão manual foi feita em `tools/anotador.html`, ferramenta de anotação
construída para este trabalho, que lê e escreve o mesmo formato JSONL do
Doccano.
