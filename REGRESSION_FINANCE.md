# Regressão financeira — provas estáticas e limites

Controle imutável: `1995`, SHA-256 `2479ed8e5c9189438d787be1e804abbd95f9e1c06e01042e560251e64ef67fc5`. A base tem 73 inputs declarados e 312 funções. O teste em `tests/test_financial_invariants.py` compara a candidata com esse conteúdo, sem presumir equivalência a partir de comentários de herança.

## Contrato comparado

| Área | Evidência exigida | Alcance |
| --- | --- | --- |
| BE e proteção progressiva | Identidade literal de `BE*`, `Protection*`, `ClassifyProtectionExits`, `ManageBreakEven`, seus structs e journals | Preserva o código; não reproduz um servidor MT5 |
| Financeiro e recuperação | Todas as funções originais fora de uma lista nominal de 59 pontos estratégicos/diagnósticos são comparadas byte a byte: 253 funções protegidas por padrão | Uma edição financeira não listada falha automaticamente |
| Envio | `SendOrder` e `OnTradeTransaction` literalmente iguais | A guarda estratégica nova atua por `EntryDispatchGuard`, antes de preparação/envio; cálculo de stops/margem e protocolo durável continuam os originais |
| EOD | `ProcessEOD` literalmente igual | B3 não participa do encerramento de posição |
| Sizing fixo | Diferença esperada exata: retirar `bool turbo` e usar `Inp_FixedLots` diretamente | Grade, min/max e `Inp_MaxLots` continuam iguais |
| Sizing por risco | Corpo a partir de `double profit=0.0;` idêntico | Preserva cálculo por `OrderCalcProfit`, equity, arredondamento para baixo e mínimo |
| Inputs protegidos | Mesmo nome, tipo e default de todos os inputs não classificados como amputações estratégicas | Inclui Magic, horários, M5/M1, BE, SL/TP, spread, desvio, overshoot, timeout, risco, cota e cooldown |
| Histórico | `ParseScalperComment`, `RJRoute`, `LoadTradeMetadata`, `Identify1995EntryDeal` idênticos e contendo os quatro modos históricos | Novas rotas usam BASE/BASE_CONT como mapeamento; não existe novo significado financeiro STANDARD |
| CSV financeiro | Headers de configuração/trades, linha de trade, índice e lógica de append idênticos | Colunas de configuração amputadas da decisão são conservadas no schema histórico, com valores constantes documentados |
| Persistência | `TradeRecord`, `BreakEvenState`, `PendingExecContext`, `PendingExitIntent`, `UnresolvedOrderContext`, `OpenPositionInfo` e enums de despacho idênticos | Namespaces de conta/símbolo/Magic/PID, checksums, barriers e incerteza de envio preservados |
| Precedência de proteção | `SyncAccountingState` → `UpdateMAEMFE` → `ProcessEOD` → `ManageBreakEven` antes dos dados experimentais | Indisponibilidade do motor novo não deve impedir a chamada às proteções |
| Cadência financeira no timer | Gate explícito de 60 segundos no tester e um segundo ao vivo, inicializado com a mesma duração; chamadas financeiras contidas nesse gate | O coletor pode rodar a cada segundo sem antecipar EOD/recuperação no timer; BE continua despachado pelo tick |
| Overshoot terminal | Harness executa `EntryDispatchGuard` e `ProcessArmedSignal` reais com negócio posterior, overshoot excessivo e spread alto, inclusive dados estratégicos indisponíveis | Cancela a tese antes de esperar spread; não cancela pedido incerto, posição ou recuperação financeira |

A lista nominal de exceções no teste contém exclusivamente a inteligência antiga, integração analítica dos callbacks, diagnóstico, `FAREvaluate`, configuração histórica compartilhada e a exceção do sizing. Ela não concede licença para alterar qualquer função financeira que a chame; `SendOrder`, recuperação, parsers, BE e EOD continuam protegidos.

`ResetPerfStat` e `RecordPerf` foram removidas apenas após a ausência de chamadas no motor analítico novo; eram auxiliares da telemetria de custo antiga. `TickIndex`, exclusivo do POC removido, também não é preservação financeira. `FARHeader` e `FARRow` permanecem literalmente iguais e são reutilizadas no stream diagnóstico novo, com colunas vazias quando o evento atrasado não pertence ao sinal armado atual.

## FAR: mudança mínima autorizada

O veto continua exigindo janela integral posterior ao armamento, classificação conhecida nas duas metades, percentual contrário configurado nas duas metades e no total, deslocamento adverso e rompimento da estrutura congelada. São conservados os modos OFF/OBSERVAR/APLICAR e default de 60%. Quando a referência estrutural exclusiva FAR não puder ser coletada, o estado é INDETERMINADO; falta de dados não se torna prova de pressão favorável/contrária. O ramo observacional FAR_FAVORAVEL passa a consultar o gatilho congelado da entrada, em vez do antigo trigger calculado por região. Essa diferença deve ser mostrada no diff e coberta por teste específico; não é equivalência literal dessa função.

O teste específico exige que o corpo inteiro de `FAREvaluate` seja exatamente o original com apenas a guarda `FAR_STRUCTURE_UNAVAILABLE` e a substituição da expressão do trigger. `FARAuditSchemaCompatible`, que validava o CSV analítico antigo removido, é a única função FAR retirada; as funções de coleta, classificação, percentuais, captura e aplicação do veto continuam protegidas por identidade literal.

## Execução dos checks desta entrega

Na revisão final da candidata foram executados **15 testes, todos aprovados**, em `tests/test_financial_invariants.py` (2,984 segundos na última execução isolada). A suíte inclui os 253 corpos de funções protegidos, os contratos de structs/inputs/CSV, a exceção exata do sizing e a diferença autorizada do FAR. Um teste compila e executa os corpos numéricos reais de proteção em um harness C++ com stubs explícitos de APIs de arredondamento: 21 asserts cobrem +/-1R exato, salto até +5R, entrada fracionária, grade WIN/WDO, arredondamento conservador e dados inválidos. Outro harness executa os corpos reais de guarda e processamento do ARMED com stubs explícitos dos efeitos MT5, cobrindo overshoot terminal com spread alto, teto exato permitido, bloqueio B3, timeout, divergência entre Last atual e processado, e proteção de pedidos/posições/recuperação. Ambos passaram com `g++ -Wall -Wextra -Werror`; não são compilação MetaEditor nem simulação do broker.

A auditoria adversarial encontrou e corrigiu, antes desta execução, uma regressão intermediária em que overshoot seguido de spread alto aguardava retração. O cancelamento terminal voltou a preceder a espera por spread. Também se identificou que timer analítico de um segundo no tester anteciparia chamadas financeiras originalmente a cada 60 segundos; a candidata agora contém gate financeiro separado, validado pela suíte.

O resultado definitivo deve ser lido também no artefato de resultados gerado pela suíte e no relatório final da entrega, após as últimas alterações. Comando reproduzível:

```sh
python3 -m unittest discover -s tests -p 'test_financial_invariants.py' -v
```

## Testes operacionais ainda necessários no MT5

| Cenário | Estado nesta máquina |
| --- | --- |
| Arranque sem posição e sem histórico disponível | NÃO EXECUTADO no terminal |
| Restart com BE pendente/confirmado e proteção progressiva | NÃO EXECUTADO no terminal |
| Pedido possivelmente enviado sem resposta e journal incompleto | NÃO EXECUTADO no terminal |
| Ordem pendente e execução parcial | NÃO EXECUTADO no terminal |
| Netting com posição estrangeira; exchange/hedging | NÃO EXECUTADO no terminal |
| EOD, rollover, queda de conexão e recuperação financeira | NÃO EXECUTADO no terminal |
| Falha de VWAP/volume com posição existente | Precedência estática verificada pela suíte; comportamento operacional NÃO EXECUTADO |
| Compilação MetaEditor e warnings reais | `COMPILACAO_NATIVA_NAO_VERIFICADA` |

Não há evidência de rentabilidade, acurácia ou comportamento operacional homologado. Identidade textual é uma prova de preservação do código protegido, não prova suficiente de equivalência de trajetória: a nova seleção de entradas muda quando existem posições e, portanto, resultados e cronologia subsequente. Situação: **NÃO HOMOLOGADO** enquanto faltarem os portões nativos e o replay financeiro.
