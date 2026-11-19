# Citizen Assist AI

Assistente de terminal, em Python, que orienta **moradores de áreas de risco de enchentes e pessoas que querem ajudar** com base em informações verificadas, mostrando a fonte, a data de verificação e avisos de limitação, sem coletar dados pessoais.

> ⚠️ Este assistente **não é um canal oficial**. Ele só repete o que está na base de conhecimento. Confirme sempre no site do órgão responsável.

## Integrantes

| Nome | RM |
|------|----|
| Mariana Carminato | 573258 |
| Angela Takezawa | 570797 |

## Público e problema

**Público:** moradores de áreas de risco de enchentes e alagamentos e pessoas que querem ajudar quem foi atingido.

**Problema:** na hora da enchente, e nos dias seguintes, as pessoas não sabem a quem ligar, como receber os alertas da Defesa Civil, o que fazer durante e depois da água, como tornar a água segura, quais doenças evitar, como recuperar documentos, quais auxílios existem e como ajudar sem cair em golpes. A informação existe, mas está espalhada e, em situação de emergência, circulam boatos e pedidos de Pix falsos.

## ODS relacionados

- **ODS 3** – Saúde e bem-estar
- **ODS 11** – Cidades e comunidades sustentáveis
- **ODS 13** – Ação contra a mudança global do clima

## Como executar

Requisitos: Python 3.8 ou superior. Não usa bibliotecas externas.

```bash
python main.py
```

Menu: `1` perguntar em texto livre, `2` navegar por categorias, `3` ver indicadores, `4` exportar CSV, `0` sair (pede uma nota de 1 a 5). Em todas as telas, `0` volta.

## Estrutura

```
citizen-assist-ai/
├── README.md
├── main.py                  # ponto de entrada
├── orientacao.py            # classe Orientacao
├── base_conhecimento.py     # classe BaseConhecimento + normalizar()
├── assistente.py            # classe Assistente
└── data/
    ├── base_conhecimento.json   # 15 orientações, 5 categorias
    ├── historico.json           # atendimentos registrados
    ├── notas.json               # notas de facilidade (1 a 5)
    └── atendimentos.csv         # exportação dos atendimentos
```

Composição: `Assistente` → `BaseConhecimento` → lista de `Orientacao`.

## Regra de pontuação

A pergunta, as palavras-chave e o título são normalizados (minúsculas, sem acentos, sem pontuação).

| Regra | Pontos |
|-------|--------|
| Palavra-chave da orientação aparece na pergunta | +3 |
| Palavra da pergunta (4 letras ou mais) aparece no título | +1 |

| Melhor orientação | Resultado |
|-------------------|-----------|
| 6 pontos ou mais | Confiança **ALTA** |
| 3 a 5 pontos | Confiança **MÉDIA** |
| menos de 3 pontos | "Não encontrei": sugere outras palavras e as categorias |

`buscar()` devolve uma lista de tuplas `(pontos, orientacao)`, da maior para a menor pontuação. O assistente mostra a melhor orientação e até duas alternativas com 3 pontos ou mais.

Exemplo: "Como deixo a água potável para beber?" → palavra-chave `agua potavel` (+3); as palavras "agua", "para" e "beber" estão no título "Tornar a água segura para beber depois da enchente" (+1 cada, +3) = **6 pontos, confiança ALTA** (orientação 8).

Ajustes em relação ao enunciado: na normalização também trocamos `-`, `/`, aspas e apóstrofo por espaço (para que "e-título" case com a palavra-chave "e titulo"). A palavra-chave só pontua se aparecer como palavra inteira (a pergunta é comparada com espaços nas pontas), então "sus" não casa dentro de outra palavra.

## Regras de atendimento

- **Dados pessoais:** perguntas com 8 ou mais dígitos ou com `@` são recusadas e **não** são registradas.
- **Entradas inválidas:** opção fora da faixa, letras, resposta vazia e s/n inválido nunca encerram o programa.
- **Transparência:** toda resposta mostra fonte, data de verificação e o aviso de que não é canal oficial.
- **Arquivos:** JSON ausente ou corrompido não trava o programa (o histórico corrompido é renomeado para `.corrompido`).

## Histórico, indicadores e CSV

Cada atendimento é salvo em `data/historico.json` com: data, origem (pergunta ou categoria), pergunta, id da orientação, se encontrou, se ajudou, tentativas e tempo em segundos. Um atendimento começa na primeira pergunta e termina quando a pessoa diz que a dúvida foi resolvida ou volta com `0`.

Indicadores exibidos: resposta encontrada (%), taxa de acerto (ajudou %), tempo médio para encontrar, tentativas por atendimento, facilidade de uso (1 a 5) e lista de dúvidas sem solução. A exportação usa `csv.DictWriter` (`data/atendimentos.csv`).

## Integrações com outras disciplinas

Nenhuma (opcional no enunciado).

## Fontes consultadas

Cada orientação traz a própria fonte no JSON. Sites usados: gov.br/mdr (Defesa Civil), gov.br/cemaden, gov.br/saude (orientações sobre enchentes), caixa.gov.br (FGTS), gov.br/mds (assistência social) e gov.br/governodigital (documentos).

## Resultado do teste com usuários

> **Preencher após testar com pelo menos 3 pessoas de fora da equipe (10 atendimentos ou mais). Não registre nomes nem dados dessas pessoas.**

| Indicador | Resultado |
|-----------|-----------|
| Pessoas testadas | _preencher_ |
| Atendimentos | _preencher_ |
| Resposta encontrada (%) | _preencher_ |
| Taxa de acerto: ajudou (%) | _preencher_ |
| Tempo médio para encontrar | _preencher_ |
| Tentativas por atendimento | _preencher_ |
| Facilidade de uso (1 a 5) | _preencher_ |

**Dúvidas sem solução:** _preencher_

**Melhoria feita a partir do teste:** _preencher (ex.: nova palavra-chave no JSON)_

## Limitações

- Responde apenas o que está na base (15 orientações); não interpreta sentido, só compara palavras.
- Erros de digitação não são corrigidos (a busca é por palavra exata).
- A base precisa ser revisada manualmente: regras, prazos e sites mudam, e a data `verificado_em` indica quando a equipe conferiu cada fonte.
- Valores, prazos e procedimentos de RG e outros serviços variam por estado ou município.

## Vídeo técnico

Link: _colar aqui o link do YouTube (não listado)_
