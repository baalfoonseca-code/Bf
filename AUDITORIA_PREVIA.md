# Auditoria prévia — Rêmora 1.995 / matriz objetiva

Base: `baalfoonseca-code/Bf`, `main`, commit `dabaa1a57b54350b72a91ee821c965a7bbb6b455`. O fonte `1995` é o artefato canônico, sem necessidade de extensão `.mq5` para leitura. Foi lido integralmente: 9.065 linhas, 378.497 bytes, versão declarada `1.995`, 312 funções identificadas. SHA-256: `2479ed8e5c9189438d787be1e804abbd95f9e1c06e01042e560251e64ef67fc5`.

Autoridade: `Comando_Codex_Remora_1995_Matriz_Objetiva_REVISADO.md`, lido integralmente. Esta reforma é uma alteração experimental da geração/validação de entradas. Não é equivalência estratégica com a base, nem simples instrumentação. A base permanecerá inalterada e a candidata será entregue separadamente.

## Dependências e fronteira

| Caminho existente | Dependência / destino da reforma | Proteção |
| --- | --- | --- |
| `CopyTradeTicksStrict` → VWAP incremental | Negócios da sessão; substituir cursor e acumuladores analíticos por cálculo causal ponderado | O coletor FAR continua distinguindo volume real/integral e indisponibilidade |
| `CalcD1Structure`, `CalcSigmaHistory`, `TryCalcD1` → `ComputeMacroContext`/`ComputeMatrixSnapshot` | Remover preço D-1 e sigma histórico exclusivamente da inteligência | Histórico contábil continua intacto |
| `ComputePOCWithTie*`, `POCResult`, `ENUM_POC_STATE`, `perfPOC` | Remover da candidata operacional | Referências na base preservada documentam herança |
| `RebuildWeisCache`, `ComputeLiveWaveO1` | Substituir direção de fechamentos M1 por ondas causais de negócios | Não chamar tick volume de volume negociado |
| `ComputeMatrixSnapshot`, `SnapshotForSignal`, `EvaluateMatrix` | Substituir votação C1–C5, região, `glass` e classificação TURBO por ABS/CONT/NEUTRO | M1 fechada continua referência; M5 não cria voto direcional |
| `ProcessArmedSignal`, `EntryDispatchGuard` | Revalidar tese congelada; limites geográficos B2 inclusiva e entrada CONT estritamente antes de B3 | Preservar negócio posterior, spread, overshoot, timeout, preço executável e guardas financeiras |
| `FARCaptureArm`, `FAREvaluate` | Extremos exclusivos FAR; referência do rompimento usa `armed.entry.trigger` | Mesmos modos/threshold, flags, duas metades, pressão posterior e estrutura |
| `SendOrder` | Chama guarda estratégica antes de cálculo/envio e em releituras de quote | Preservar preparação, barreira durável, API de envio, tratamento de resultado e sizing normal |
| `OnTick`, `OnTimer`, `DailyReset`, `BootstrapCachesNoTrade`, `OnInit` | Trocar apenas dependências analíticas e inicialização do motor | A execução financeira precede o trabalho novo; reconstrução não gera entradas passadas |

## Identidade e persistência financeira

`EvaluateMatrix` escreve `armed.route/mode`; `SendOrder` usa esses campos no comentário `S1995|<route>|<mode>`. `PreparePendingExec` copia referência, volume, SL/TP e intenção. `MarkRequestDispatchPossible` persiste a transição `PREPARED → MAY_HAVE_DISPATCHED` antes de `PositionOpen`; `CompletePendingExec` retém resultado, pedido e IDs. Não é permitido inferir ausência de envio a partir de timeout, erro de transporte, posição ausente ou ordem desaparecida.

`ParseScalperComment`, `RJRoute`, `LoadTradeMetadata` e `Identify1995EntryDeal` aceitam as identidades `BASE`, `TURBO`, `BASE_CONT`, `TURBO_CONT`. `STANDARD` não é aceito pela base. A candidata deve mapear as novas entradas para `BASE`/`BASE_CONT`, sem classificação TURBO, conservando esses parsers literalmente. Apenas o multiplicador de lote fixo será retirado; o cálculo por risco e os limites da grade continuarão iguais.

`TradeMetaPath`, `AccountingKey`, `EconomicMarkerPrefix`, `BEJournalPath` e `RequestJournalPath` definem namespaces persistentes que não podem ser renomeados. `TradeRecord`, `BreakEvenState`, `PendingExecContext`, `PendingExitIntent`, `UnresolvedOrderContext` e `OpenPositionInfo` preservam formato e semântica. `NewEntrySignalID`/diagnóstico experimental não substituem identidade financeira de conta/símbolo/Magic/ordem/deal/POSITION_ID.

Os CSVs financeiros dependem de `CsvConfigHeader/Row`, `CsvTradeHeader/Row`, `InitializeTradeCsvIndex` e `WriteTradeRow`. Retirar uma coluna analítica compartilhada invalidaria o arquivo já gravado. Campos históricos de configuração podem sobreviver no schema financeiro como constantes documentadas, sem voltar a decidir entradas; o novo diagnóstico deve ter arquivo próprio.

## Núcleo congelado

Estão protegidos: `ProcessEOD`; gestão de BE e todas as funções `BE*`/`Protection*`; confirmação contábil de negócios; ownership/netting; limites diários e sequenciais; cota; cooldown; reconciliação de execução parcial ou incerta; recuperação de ordens; journals e marcadores econômicos. O bloco de `ResetTradeRecord` ao final do arquivo contém esses subsistemas e será comparado função por função, incluindo `OnTradeTransaction`.

No `OnTick` original, `SyncAccountingState`, `UpdateMAEMFE`, `ProcessEOD` e `ManageBreakEven` precedem dados e decisão. O novo motor não pode fazer essas rotinas dependerem de VWAP, volume ou prontidão. No timer, recuperação e prova de BE também precedem trabalho analítico. Funções de entrada não podem limpar intenção financeira para satisfazer uma tese nova.

## Riscos identificados antes da implementação

1. **Eficiência dependente do feed:** fragmentação a preço igual preserva caminho, mas alternâncias por bid-ask bounce aumentam `grossPath`. É necessário refutar com trajetórias equivalentes e testar qualquer amostragem causal; 0,60/0,30 são hipóteses, não parâmetros otimizados.
2. **Circularidade ABS:** exigir baixa eficiência da reação que deve progredir invalida a própria reversão. Esforço/ineficiência pertencem à tentativa original; rejeição posterior deve ter evidência e relógio próprios.
3. **Fronteira inclusiva:** `CopyTicksRange` inclui ambos os limites e pode devolver vários negócios idênticos no mesmo milissegundo. Deduplicação por timestamp/preço elimina multiplicidade legítima. Revisão do prefixo já observado deve tornar dados indisponíveis ou reconstruir causalmente.
4. **Cobertura:** cinco minutos não provam histórico íntegro nem sigma estável. READY exige também qualidade/suficiência configuradas. Sessões, leilão, feed silencioso e reconexão precisam política explícita; nenhum fallback D-1.
5. **B2/B3:** sinal fechado exatamente em B2 pode ter gatilho fora de B3. A margem não muda; trigger e execução CONT precisam estar estritamente antes da B3 congelada. Esse bloqueio não altera saída de posição aberta.
6. **Snapshot causal:** reconstrução iniciada às 10h não pode usar bandas das 10h em um sinal das 9h nem gerar ordem retroativa. Fotografia de início da tentativa e de fechamento de M1 não podem receber dados futuros.
7. **Bloqueio/lentidão de dados:** chamadas síncronas de histórico podem atrasar proteção. Trabalho deve ser limitado, medido, e ocorrer depois de BE/EOD; nenhum limite em código torna uma chamada MT5 preemptível.
8. **Compatibilidade histórica:** renomear BASE/TURBO ou schema de CSV/journals pode impedir recuperação. O mapeamento das novas rotas e a retirada exclusiva do multiplicador evitam essa ampliação de escopo.

## Provas e limites

A comparação estática deve comprovar identidade do núcleo protegido e inputs, e inspecionar explicitamente os pontos de integração. Testes numéricos e adversariais devem executar os cálculos novos, não meras réplicas que sempre passam. Compilação C++ de um kernel, quando usada, não é compilação MQL5. Replay/Strategy Tester, reinícios operacionais, performance com feed real e resultados financeiros exigem o terminal e dados adequados.

O ambiente Linux inspecionado não possui MetaEditor/MetaTrader 5. PDF e referências históricas citadas não estão no checkout e são secundários. Situação inicial: `COMPILACAO_NATIVA_NAO_VERIFICADA`, `DADOS_INSUFICIENTES` para microestrutura real e candidata **NÃO HOMOLOGADA** até os portões obrigatórios serem executados.
