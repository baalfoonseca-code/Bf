# Auditoria dos 65 inputs — base b6961c4

Autoridade: `Comando_Codex_Remora_1995_Matriz_Objetiva_REVISADO.md` e `Comando_Codex_Remora_1996_Integracao_Entrega.md`, subordinados ao pedido atual de correção CONT. Conferência automática das declarações em `1995`, principal e módulo; leitura de `INPUTS_DIFF.md`.

Resultado: **65 entradas efetivas = 48 herdadas + 17 hipóteses experimentais previstas**, com todos os nomes em INPUTS_DIFF. Nenhuma alteração de tipo/default nas 48 herdadas. A base tem 73 inputs: 25 removidos + 48 mantidos. Dentre os 17 novos, seis têm nome/default explicitamente prescritos como hipótese no comando; os outros onze atendem requisitos de engenharia/pesquisa expostos e já documentados. Não se qualifica nenhum número como otimizado ou comprovado.

Classes: H = herdado; HP-E = hipótese experimental prevista, default expressamente autorizado no comando; HP-D = hipótese prevista/documentada para atender requisito autorizado, sem prescrição original do número. Mudanças semânticas autorizadas são indicadas em H. Nenhum input adicional foi necessário para a correção solicitada.

| # | Input | Tipo / default | Classe | Confronto com comando e INPUTS_DIFF |
| --- | --- | --- | --- | --- |
| 1 | `Inp_Magic_WIN` | `int = 60001` | H | Nome, tipo e default idênticos a 1.995; preservação exigida no §0/§5/§6. |
| 2 | `Inp_Magic_WDO` | `int = 60002` | H | Nome, tipo e default idênticos a 1.995; preservação exigida no §0/§5/§6. |
| 3 | `CSVFileName` | `string = "Scalper1995"` | H | Nome, tipo e default idênticos a 1.995; preservação exigida no §0/§5/§6. |
| 4 | `BacktestStart` | `datetime = D'2025.01.01'` | H | Nome, tipo e default idênticos a 1.995; preservação exigida no §0/§5/§6. |
| 5 | `Inp_ContextTF` | `ENUM_TIMEFRAMES = PERIOD_M5` | H | Nome, tipo e default idênticos a 1.995; preservação exigida no §0/§5/§6. |
| 6 | `Inp_SignalTF` | `ENUM_TIMEFRAMES = PERIOD_M1` | H | Nome, tipo e default idênticos a 1.995; preservação exigida no §0/§5/§6. |
| 7 | `Inp_StartHHMM` | `int = 900` | H | Nome, tipo e default idênticos a 1.995; preservação exigida no §0/§5/§6. |
| 8 | `Inp_StopEntryHHMM` | `int = 1530` | H | Nome, tipo e default idênticos a 1.995; preservação exigida no §0/§5/§6. |
| 9 | `Inp_EOD_CloseHHMM` | `int = 1750` | H | Nome, tipo e default idênticos a 1.995; preservação exigida no §0/§5/§6. |
| 10 | `Inp_SizingMode` | `SIZING_MODE = SIZING_FIXED` | H | Nome, tipo e default idênticos a 1.995; preservação exigida no §0/§5/§6. |
| 11 | `Inp_FixedLots` | `double = 1.0` | H | Nome, tipo e default idênticos a 1.995; preservação exigida no §0/§5/§6. |
| 12 | `Inp_RiskPerTradePct` | `double = 0.15` | H | Nome, tipo e default idênticos a 1.995; preservação exigida no §0/§5/§6. |
| 13 | `Inp_MaxLots` | `double = 2.0` | H | Nome, tipo e default idênticos a 1.995; preservação exigida no §0/§5/§6. |
| 14 | `Inp_SL_Pts_WIN` | `double = 400.0` | H | Nome, tipo e default idênticos a 1.995; preservação exigida no §0/§5/§6. |
| 15 | `Inp_TP_Pts_WIN` | `double = 2000.0` | H | Nome, tipo e default idênticos a 1.995; preservação exigida no §0/§5/§6. |
| 16 | `Inp_SL_Pts_WDO` | `double = 10.0` | H | Nome, tipo e default idênticos a 1.995; preservação exigida no §0/§5/§6. |
| 17 | `Inp_TP_Pts_WDO` | `double = 25.0` | H | Nome, tipo e default idênticos a 1.995; preservação exigida no §0/§5/§6. |
| 18 | `Inp_SpreadMaxPts_WIN` | `double = 30.0` | H | Nome, tipo e default idênticos a 1.995; preservação exigida no §0/§5/§6. |
| 19 | `Inp_SpreadMaxPts_WDO` | `double = 2.0` | H | Nome, tipo e default idênticos a 1.995; preservação exigida no §0/§5/§6. |
| 20 | `Inp_EnableBreakEven` | `bool = true` | H | Nome, tipo e default idênticos a 1.995; preservação exigida no §0/§5/§6. |
| 21 | `Inp_EnableDailyRiskStop` | `bool = true` | H | Nome, tipo e default idênticos a 1.995; preservação exigida no §0/§5/§6. |
| 22 | `Inp_MaxDailyLossR` | `double = 3.0` | H | Nome, tipo e default idênticos a 1.995; preservação exigida no §0/§5/§6. |
| 23 | `Inp_EnableConsecutiveLossStop` | `bool = true` | H | Nome, tipo e default idênticos a 1.995; preservação exigida no §0/§5/§6. |
| 24 | `Inp_MaxConsecutiveLosses` | `int = 3` | H | Nome, tipo e default idênticos a 1.995; preservação exigida no §0/§5/§6. |
| 25 | `Inp_MaxTradesDay` | `int = 10` | H | Nome, tipo e default idênticos a 1.995; preservação exigida no §0/§5/§6. |
| 26 | `Inp_CooldownSec` | `int = 0` | H | Nome, tipo e default idênticos a 1.995; preservação exigida no §0/§5/§6. |
| 27 | `Inp_LossCooldownSec` | `int = 0` | H | Nome, tipo e default idênticos a 1.995; preservação exigida no §0/§5/§6. |
| 28 | `Inp_ArmedTimeoutSec` | `int = 300` | H | Nome, tipo e default idênticos a 1.995; preservação exigida no §0/§5/§6. |
| 29 | `Inp_BreakoutMargin_WIN` | `double = 175.0` | H | Nome, tipo e default idênticos a 1.995; preservação exigida no §0/§5/§6. |
| 30 | `Inp_BreakoutMargin_WDO` | `double = 3.5` | H | Nome, tipo e default idênticos a 1.995; preservação exigida no §0/§5/§6. |
| 31 | `Inp_MaxOvershoot_WIN` | `double = 100.0` | H | Nome, tipo e default idênticos a 1.995; preservação exigida no §0/§5/§6. |
| 32 | `Inp_MaxOvershoot_WDO` | `double = 2.5` | H | Nome, tipo e default idênticos a 1.995; preservação exigida no §0/§5/§6. |
| 33 | `Inp_ABS_Effort` | `double = 1.50` | H | Herdado; §3 autoriza esforço da tentativa original versus ondas encerradas. |
| 34 | `Inp_CONT_Effort` | `double = 1.50` | H | Herdado; §3 autoriza esforço da onda direcional versus ondas encerradas. |
| 35 | `Inp_ABS_MinPriceMovePts_WIN` | `double = 60.0` | H | Herdado; origem de medição passa à excursão da tentativa conforme §3. |
| 36 | `Inp_ABS_MinPriceMovePts_WDO` | `double = 2.0` | H | Herdado; origem de medição passa à excursão da tentativa conforme §3. |
| 37 | `Inp_CONT_MinPriceMovePts_WIN` | `double = 50.0` | H | Herdado; §3 autoriza explicitamente progresso líquido em lugar da janela POC. |
| 38 | `Inp_CONT_MinPriceMovePts_WDO` | `double = 1.5` | H | Herdado; §3 autoriza explicitamente progresso líquido em lugar da janela POC. |
| 39 | `Inp_BandMultiplier_WIN` | `double = 0.80` | H | Herdado; §2 fixa 0,8σ/1,6σ/2,4σ da sessão. |
| 40 | `Inp_BandMultiplier_WDO` | `double = 1.50` | H | Herdado; §2 fixa 1,5σ/3σ/4,5σ da sessão. |
| 41 | `Inp_MaxDeviationPts_WIN` | `int = 100` | H | Nome, tipo e default idênticos a 1.995; preservação exigida no §0/§5/§6. |
| 42 | `Inp_MaxDeviationPts_WDO` | `int = 2` | H | Nome, tipo e default idênticos a 1.995; preservação exigida no §0/§5/§6. |
| 43 | `Inp_EnableAbsorption` | `bool = true` | H | Nome, tipo e default idênticos a 1.995; preservação exigida no §0/§5/§6. |
| 44 | `Inp_EnableContinuation` | `bool = true` | H | Nome, tipo e default idênticos a 1.995; preservação exigida no §0/§5/§6. |
| 45 | `Inp_ExitMode` | `EXIT_MODE = PROGRESSIVE_NO_TP` | H | Nome, tipo e default idênticos a 1.995; preservação exigida no §0/§5/§6. |
| 46 | `Inp_MaxProtectedR` | `int = 5` | H | Nome, tipo e default idênticos a 1.995; preservação exigida no §0/§5/§6. |
| 47 | `Inp_AggressionFilterMode` | `FAR_MODE = FAR_APLICAR` | H | Nome, tipo e default idênticos a 1.995; preservação exigida no §0/§5/§6. |
| 48 | `Inp_AggressionThresholdPct` | `double = 60.0` | H | Nome, tipo e default idênticos a 1.995; preservação exigida no §0/§5/§6. |
| 49 | `Inp_BandsWarmupSec` | `int = 300` | HP-E | §2: 300s expressos; hipótese de maturidade, não estabilidade provada. |
| 50 | `Inp_BandsMinTrades` | `int = 2` | HP-D | §2 exige negócios suficientes e preços distintos; 2 é hipótese algébrica documentada, não suficiência estatística. |
| 51 | `Inp_BandsMinSigmaTicks` | `double = 1.0` | HP-D | §2 autoriza parâmetro de dispersão distinguível da grade; 1,0 é hipótese documentada. |
| 52 | `Inp_RegularSessionStartHHMM` | `int = -1` | HP-D | §2 prevê override de sessão regular em caso de ambiguidade; -1 exige sessão publicada única. |
| 53 | `Inp_RegularSessionEndHHMM` | `int = -1` | HP-D | §2 prevê delimitação de sessão; -1 acompanha início, sem sessão inventada. |
| 54 | `Inp_FeedMaxGapSec` | `int = 30` | HP-D | §2/§7 exigem cobertura verificável; 30s é diagnóstico experimental documentado, não prova de corrupção. |
| 55 | `Inp_WaveBaselineMin` | `int = 3` | HP-D | §3 exige quantidade suficiente até 10 ondas encerradas; 3 é hipótese documentada. |
| 56 | `Inp_WaveReversalPts_WIN` | `double = 60.0` | HP-E | §3: 60 pontos expressos; reversão estrutural causal experimental. |
| 57 | `Inp_WaveReversalPts_WDO` | `double = 2.0` | HP-E | §3: 2,0 pontos expressos; reversão estrutural causal experimental. |
| 58 | `Inp_PathEventTicks` | `int = 2` | HP-D | §3 prevê amostragem causal se grossPath for refutado; 2 ticks documentados e pedido atual autoriza uso exclusivamente de medição. |
| 59 | `Inp_CONT_MinPathEfficiency` | `double = 0.60` | HP-E | §3: 0,60 expresso; trajetória amostrada, não valor otimizado. |
| 60 | `Inp_ABS_MaxPathEfficiency` | `double = 0.30` | HP-E | §3: 0,30 expresso; tentativa anterior, sem exigir ineficiência da reação. |
| 61 | `Inp_ABS_MinRejectionFraction` | `double = 0.35` | HP-E | §3: 0,35 expresso; além de ao menos um tick de rejeição. |
| 62 | `Inp_DataChunkMsc` | `int = 10000` | HP-D | §7 requer chunks limitados; 10000ms é orçamento de engenharia documentado. |
| 63 | `Inp_DataMaxChunkTrades` | `int = 50000` | HP-D | §7 requer controle de carga e sem descarte silencioso; 50000 é orçamento documentado. |
| 64 | `Inp_DataChunksPerTimer` | `int = 4` | HP-D | §7 requer orçamento por callback; 4 é hipótese de engenharia documentada. |
| 65 | `Inp_SigmaCheckToleranceTicks` | `double = 0.000001` | HP-D | §2/§9 requerem comparação independente em ticks; 0,000001 é tolerância numérica documentada, não filtro estratégico. |

## Regras confrontadas

| Regra | Autoridade / resultado da auditoria |
| --- | --- |
| Sinal apenas após M1 fechada; M5 sem novo voto | §3/§4/§5: autorizado. |
| VWAP/sigma ponderado por volume real da sessão; bandas uniformes e congeladas | §2/§4: autorizado. |
| Weis causal, reversão 60 WIN/2 WDO; baseline apenas de ondas encerradas | §3: autorizado; mínimo 3 permanece hipótese explícita. |
| CONT: onda/direção, esforço 1,50, progresso 50 WIN/1,5 WDO e eficiência 0,60 | §3: autorizado; sem cor de candle ou pullback obrigatório. |
| ABS: esforço/ineficiência da tentativa e rejeição posterior 0,35 e ≥1 tick | §3: autorizado. |
| CONT somente até B2 inclusiva ao armar; trigger/execução estritamente antes de B3 congelada | §4: expressamente autorizado; B3 não altera saídas. |
| Spread, margem, overshoot, timeout, FAR e financeiro | §0/§5/§6: preservação obrigatória. |
| `drawdown < c.eventStep` em `OMClassify` e `drawdown >= cfg.eventStep` em `OMRevalidate` | **Sem autorização na base b6961c4.** Transforma amostragem em tolerância estratégica de cancelamento; o pedido atual autoriza retirar essa associação, sem novo limiar substituto. |
| `reversal >= Inp_PathEventTicks*gTickSize` na validação | Restrição de coerência entre escala amostrada e segmentação, já documentada; não é tolerância de recuo nem nova regra adicionada pela correção. |
| OM_LIVE_MAX_RECORDS=256 / OM_LIVE_MAX_LAG_MSC=1000 | Orçamentos internos explicitamente documentados na integração; não inputs estratégicos nem evidência de latência real. |

Não foi identificada outra condição estratégica quantitativa nova sem autorização nos caminhos CONT/ABS/geografia examinados. Isso não é prova universal de ausência de defeitos nem validação operacional. Defaults de engenharia documentados não recebem validação estatística por esta auditoria.

A combinação `Inp_ABS_MaxPathEfficiency < Inp_CONT_MinPathEfficiency` é validação da separação experimental, já existente, sem valor novo. A documentação anterior chama as 17 novas entradas de hipóteses, e esta classificação preserva essa qualificação.

## Limites e divergências documentais

- A integração anterior deixou a tolerância CONT como ambiguidade; o pedido atual resolve a decisão, autorizando retirar o vínculo. Atualizar os trechos que ainda a tratam como pendente e registrar a alteração como correção autorizada.
- A referência histórica da skill BOOK (70 inputs/1.125) não se aplica como preset a esta tarefa. A fonte de autoridade aqui é 1.996 e os 65 inputs efetivos, conforme comando atual.
- Preservar `1995` SHA-256 `2479ed8e5c9189438d787be1e804abbd95f9e1c06e01042e560251e64ef67fc5`.
- Compilação MetaEditor, Strategy Tester e dados de mercado não são provados por esta auditoria estática.

## Correção executada e limite da conclusão

Branch: `codex/remora-1996-cont-surgical`, derivada exatamente de
`b6961c4cdff4a9e3f99b64f06fac4d0551ef817e`.

Removidos exclusivamente o cálculo local de drawdown e sua comparação direta
com eventStep em `OMClassify()` e `OMRevalidate()`. Não há limiar substituto.
A escala segue alimentando eventPrice/eventPath e, portanto, a eficiência já
prevista; não é prometida invariância da classificação a mudanças de amostragem.
O limite estrutural continua sendo o input vigente de reversão da onda, não um
novo veto. Permanecem os conflitos e os demais predicados da classificação;
a revalidação não recebeu novo veto por reclassificação global.

| Regra vigente | Mudança | Invariantes | Efeito e contrapartida | Evidência |
| --- | --- | --- | --- | --- |
| CONT: recuo limitado artificialmente por eventStep | Retirado o veto direto nos dois métodos | Direção/identidade, esforço, progresso, eficiência, reversão estrutural | Permite manter/identificar CONT em recuos ainda sustentados; muda o universo de oportunidades, sem prova de melhor resultado | Harness da implementação entregue, BUY/SELL WIN/WDO |
| Amostragem da trajetória | Nenhuma | Mesmo input, unidades e acumuladores | Eficiência continua sensível à trajetória observada | Inputs e funções de medição intactos |
| M1/B2/B3/margens/timeout/spread/overshoot | Nenhuma | Fonte principal byte a byte igual à base | Nenhuma nova permissão de despacho | Suítes de entrada e integração |
| FAR/BE/SL/TP/sizing/journals/recuperação/EOD | Nenhuma | Fonte principal e 1.995 intactos | Alteração da seleção CONT pode mudar posições e resultados posteriores | Comparação estática e testes portáteis, sem prova de broker |

A revisão independente conferiu que apenas duas dentre 38 funções do módulo
mudaram e que nenhum predicado foi acrescentado. O principal, o builder, `1995`
e o consolidado histórico permanecem byte a byte iguais à base. Os artefatos
históricos permanecem históricos; resultados atuais estão somente em
`artifacts/correcao_cont_1996/`.

A suíte original de 96 testes passou antes da alteração. Quatro expectativas
antigas de cancelamento por dois ticks foram atualizadas explicitamente ao
contrato autorizado. As demais expectativas foram preservadas; os novos testes
exercitam a implementação compartilhada, sem substituir o algoritmo por réplica.
Consultar `test-results.txt` e `validation.json` no diretório de artefatos para a
contagem final e `functions.patch` para o diff das funções modificadas.

Entrega de uso: somente `RemoraScalper_1996_Completo.mq5`, com o módulo integral
incorporado e sem includes próprios externos. Dependências restantes são as
bibliotecas padrão Trade do MT5. Não é necessário copiar o módulo separado.

**COMPILACAO_NATIVA_NAO_VERIFICADA.** MetaEditor/MT5 não estão disponíveis nesta
máquina; nenhum número de erros ou warnings nativos é alegado. Strategy Tester,
replay com dados reais, reinícios financeiros e validação operacional continuam
não executados. Candidata **NÃO HOMOLOGADA** para conta real. A mudança é uma
correção de defeito demonstrado, não uma comprovação de vantagem preditiva.

## Resultado final executado

`python3 -m unittest discover -s tests -v`: **146/146 passaram**, 20,563s,
zero falhas, erros ou skips. São 96 casos preexistentes (4 oráculos do defeito
explicitamente atualizados) + 44 novos de sustentação + 6 de segurança dos callbacks.
Contra o módulo intacto b6961c4, os 44 novos de sustentação reproduziram 24 falhas
esperadas; ver `base-new-tests-red.txt`. Na versão corrigida todos passam.
Revisão independente repetiu os 50 novos testes: todos passaram.

Os casos de recuo maior usam 20 pontos WIN e 1,5 WDO ainda sustentados; a
fronteira estrutural segue 60 WIN/2 WDO, com cenários um tick antes, na igualdade
e depois. Recuo de dois ticks é 10 WIN/1 WDO. A perda de eficiência é produzida
por oscilação na mesma onda; esforço e progresso insuficientes são fixtures
numéricas declaradas, sem afirmar que o volume acumulado cai naturalmente.

Os seis novos testes integrados verificam fechamento M1 após recuo, chamada e
respeito ao veto booleano FAR, precedência de accounting/EOD/BE, reconstrução
sem entrada retroativa, espera por nova M1, despacho único em callbacks repetidos
e preservação de obrigações pendentes. FAR, serviços financeiros e broker são
stubs explícitos nesse harness: não se alega prova nova do algoritmo FAR,
persistência real, proteção no servidor ou fills. A preservação dos corpos FAR
e financeiros também é verificada estaticamente pela suíte original.

SHA-256 da entrega única:
`381673d13bdda0ab175bd11d5d603f65f4df9f56dc67f6b884d18eb553b87cc5`.
