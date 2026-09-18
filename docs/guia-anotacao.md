# Guia de anotação — base `cellphone.ibyte`

Documento de referência para a revisão das entidades no Doccano. O objetivo é
que dois anotadores diferentes produzam a mesma anotação para o mesmo título.

## Tags

| Tag | O que marcar | Exemplos |
|---|---|---|
| `TIPO` | categoria funcional do produto | `Smartphone`, `Capa`, `Película de Vidro`, `Carregador Veicular` |
| `MARCA` | fabricante do produto | `Samsung`, `Apple`, `Multilaser` |
| `MODELO` | linha/modelo **do produto sendo vendido** | `iPhone 14 Pro Max`, `Galaxy A53`, `Moto E32` |
| `COMPATIBILIDADE` | modelo de aparelho a que um **acessório** se destina | `Capa para **iPhone 13 Pro**` |
| `MEMORIA` | armazenamento interno | `128GB`, `64 GB` |
| `RAM` | memória de trabalho | `4GB RAM`, `8GB de RAM` |
| `COR` | cor declarada | `Preto`, `Azul Pacífico`, `Rose Gold` |
| `TELA` | tamanho da tela | `Tela 6,5`, `6.5 Pol` |
| `REDE` | geração de rede móvel | `4G`, `5G` |
| `CAMERA` | resolução da câmera | `13MP`, `5.0MP` |
| `BATERIA` | capacidade da bateria | `5000mAh` |
| `POTENCIA` | potência ou voltagem | `20W`, `Bivolt` |
| `CODIGO` | código do fabricante/SKU | `MM2Y3ZE/A`, `NK041`, `P9076` |

## Regras de decisão

**1. Produto principal vs. acessório.**
Esta é a regra mais importante da base, porque metade dos títulos é de acessório.
O modelo citado depois de `para`, `compatível com` ou `p/` é `COMPATIBILIDADE`,
nunca `MODELO`.

- `Capa para iPhone 8 Plus / 7 Plus Apple` → `Capa`=TIPO, `iPhone 8 Plus`=COMPATIBILIDADE, `Apple`=MARCA
- `iPhone 11 Apple Branco, 64GB` → `iPhone 11`=MODELO, `Apple`=MARCA

Quando o acessório lista vários aparelhos compatíveis (`iPhone 8 Plus / 7 Plus`),
marcar **cada um** como um span separado de `COMPATIBILIDADE`.

**2. Um `TIPO` por título.**
O tipo é o do produto vendido, normalmente no início. Em
`Cinta Esportiva Resist Água 2 Bolsos Smartphone de Até 5.5 Pol`, o tipo é
`Cinta Esportiva`; a palavra `Smartphone` ali indica compatibilidade e **não**
deve ser marcada como TIPO.

**3. Extensão do span de `TIPO`.**
Incluir o qualificador quando ele muda a categoria do produto:
`Película de Vidro` (inteiro), `Carregador Veicular` (inteiro),
`Capa com MagSafe` (inteiro). Não incluir adjetivos comerciais:
em `Capa Protetora Premium`, marcar apenas `Capa Protetora`.

**4. `MEMORIA` vs. `RAM`.**
Quando o título traz os dois números (`128GB 8GB de RAM`), o primeiro é
armazenamento e o segundo é RAM. O span de RAM inclui a palavra `RAM`.

**5. Unidades.**
A unidade faz parte do span: marcar `128GB` e não `128`. O mesmo para
`13MP`, `5000mAh`, `20W`.

**6. `TELA`.**
Incluir a palavra `Tela` quando ela estiver presente (`Tela 6,5`). Quando não
estiver, marcar o número com a unidade (`6.5 Pol`). Muitos títulos da base vêm
truncados no caractere de polegada; anotar o que estiver visível.

**7. `MODELO` vs. `CODIGO`.**
O código do fabricante costuma vir no fim do título, depois de um hífen, e não é
pronunciável (`MHDC3BR/A`, `NK041`). Se a sequência alfanumérica é o nome pelo
qual o produto é vendido (`Twist 2 Pro S532`), ela faz parte do `MODELO`.

**8. Pontuação e espaços.**
O span não inclui vírgulas, hífens nem espaços nas bordas.

**9. Na dúvida, não marcar.**
Termos de marketing (`Desbloqueado`, `Original`, `Lacrado`, `Dual Chip`) ficam
sem tag nesta versão do esquema.

## Fluxo de revisão

1. Importar `data/annotations/cellphone.ibyte.revisar.jsonl` no Doccano
   (amostra de 400 títulos estratificada por categoria).
2. Revisar em duas passadas: na primeira, corrigir o que estiver errado; na
   segunda, reler os títulos anotados no início, já com o guia consolidado.
   Anotador único tende a mudar de critério ao longo do trabalho, e a segunda
   passada é o que controla isso.
3. Toda decisão nova tomada durante a revisão entra no histórico abaixo.
4. Exportar como `data/annotations/cellphone.ibyte.jsonl`.

## Histórico de decisões

| Data | Decisão | Motivo |
|---|---|---|
| | Criada a tag `COMPATIBILIDADE` | metade da base é acessório e marcar o aparelho alvo como `MODELO` confundiria o cadastro |
| | `RAM` separada de `MEMORIA` | são campos distintos no cadastro do produto |
