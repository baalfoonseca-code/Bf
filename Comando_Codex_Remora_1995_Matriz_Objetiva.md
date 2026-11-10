# COMANDO DEFINITIVO AO CODEX — RÊMORA SCALPER 1.995 → MATRIZ OBJETIVA

## 0. MISSÃO, FONTE E LIMITES

Atue como engenheiro sênior MQL5 e auditor independente de estratégias quantitativas para WIN/IND e WDO/DOL na B3. A tarefa é uma CIRURGIA NA INTELIGÊNCIA DE ENTRADA, NÃO UMA REESCRITA DO EA. Trabalhe a partir do arquivo-fonte `.mq5` canônico da versão Scalper 1.995, conferindo-o com o PDF de 195 páginas enviado pelo usuário. O próprio PDF informa que sua compilação nativa está pendente: NÃO alegue que a versão anterior nem a nova compilam sem evidência do MetaEditor. Preserve um arquivo imutável da base, registre SHA-256, crie uma nova versão/branch e entregue diff completo. Se não encontrar o `.mq5` canônico, reporte a ausência; NÃO trate a extração do PDF automaticamente como fonte compilável.

**Princípio:** ONDE (VWAP Bands da sessão) + ESFORÇO (Weis Wave com volume real de negócios) + RESULTADO (trajetória, eficiência, reação) → CONT BUY, CONT SELL, ABS BUY, ABS SELL ou NEUTRO. Isso não é um sistema de votação nem uma declaração de edge comprovado. Observe e refute a própria classificação.

**FRONTEIRA DE MODIFICAÇÃO:** substituir somente (i) coleta/cálculos de VWAP e bandas do dia; (ii) formação e interpretação de ondas e reação do preço; (iii) matriz ABS/CONT, armamento, invalidação e guardas direcionais tardios; (iv) integração mínima com FAR; (v) telemetria analítica correspondente; (vi) validação de inputs exclusivamente relacionados a esses módulos.

**ZONA PROTEGIDA — CONGELADA:** NÃO alterar, nem por refatoração cosmética, lógica e valores de `Inp_Magic_WIN=60001`, `Inp_Magic_WDO=60002`, `CSVFileName`, `BacktestStart`, timeframes M5/M1, horários de entrada/EOD, `Inp_SizingMode`, `Inp_FixedLots`, `Inp_RiskPerTradePct`, `Inp_MaxLots`, SL/TP (WIN 400/2000; WDO 10/25), `Inp_ExitMode=PROGRESSIVE_NO_TP`, `Inp_EnableBreakEven=true`, `Inp_MaxProtectedR=5`, stops diários e sequenciais, cota diária, cool-downs, `Inp_ArmedTimeoutSec=300`, spread, desvio, overshoot (WIN 100; WDO 2,5), EOD, BE e locks de proteção, recuperação econômica, `OnTradeTransaction`, persistência, propriedade/ownership/netting, pendências, journaling de execução, reconciliadores, salvaguardas de envio, SL/TP, gestão de posições e toda condição de fail-closed financeira. Não mudar inputs alheios à seleção de entradas. Se encontrar identificador `BKey`, `BEKey` ou similar no repositório canônico, preservar literalmente nome/semântica; não presumir que exista porque foi citado oralmente. NÃO aumentar lotagem para recuperar perdas.

**EXCEÇÃO ESPECÍFICA JÁ AUTORIZADA:** remover o multiplicador de lotes TURBO somente das NOVAS ENTRADAS. Para lote fixo: usar `Inp_FixedLots` sem multiplicador; para risco percentual: preservar o cálculo anterior. Os rótulos históricos `BASE`, `BASE_CONT`, `TURBO`, `TURBO_CONT` e quaisquer identificadores antigos devem continuar reconhecíveis pelo subsistema financeiro quando necessários à recuperação de posições/ordens/arquivos. Não reescrever retrospectivamente históricos nem renomear Magic, chaves persistentes ou arquivos de journaling financeiro.

## 1. AMPUTAÇÕES EXATAS

Remover da NOVA decisão e de seus caminhos de execução:

1. POC/Volume Profile inteiro: `ENUM_POC_STATE`, `ComputePOCWithTie*`, janelas de 300s, classificação FOLLOWING/DIVERGENT, todos os C1 que consultam POC, caches, `perfPOC`, inputs `Inp_POC_*`, logs/colunas apenas analíticos de POC.
2. Referências de preço D-1: `CalcD1Structure`, `TryCalcD1`, `VWAP_D1`, `H1`, `L1`, `d1Ready`, C2/C3/C4 e inputs vinculados. NÃO retirar histórico financeiro de pregões; ele é outro subsistema. O cálculo antigo `CalcSigmaHistory`, `SigmaLookbackDays` e `Inp_SigmaFloor_*` sai do motor: foi escolhida a modalidade automática da sessão, não um fallback histórico.
3. Votação C1–C5, pontuação 3/3, classificações BASE/TURBO para novas ordens, `Inp_TurboLotsMultiplier`, `Inp_Rule_40_60`, `Inp_VWAP_Inner_Pct`, `Inp_VWAP_Outer_Pct` e antiga lógica de `glass` como veto.
4. `Inp_Region_Candles` como PRÉ-CONDIÇÃO de ARMAR, `REGION_INVALID` derivado de máximas/mínimas anteriores, e gatilho `ComputeTrigger(regHigh,regLow)` nos caminhos novos. Eliminar a escolha ABS legada `ABS_TRIGGER_LEGACY_REGION` para NOVOS SINAIS. Conservar parsers de ordens históricas se necessários.
5. Velhos vetos direcionalmente inconsistentes `LATE_WEIS_BLOCK`, `LATE_DIRECTION_BLOCK`, `LATE_GLASS_BLOCK`, old `Inp_EnableMacroDirectionGate` e `Inp_EnableLateDirectionBlock`, substituindo apenas por checagem contemporânea de validade da nova tese. Remover também das checagens de inicialização/OnTimer/OnTick, para não deixar travas escondidas.
6. Qualquer dado morto: após análise de referências, apagar structs/funções/inputs sem uso operacional, MAS não remover símbolos usados na persistência/recuperação/journals financeiros. Documentar exceções.

Executar busca de referências em toda a árvore antes de excluir qualquer símbolo e apresentar mapa `símbolo antigo → remoção/substituição/legado financeiro preservado`. Nenhuma referência antiga pode permanecer como condição silenciosa de entrada.

## 2. VWAP DA SESSÃO E SIGMA AUTOMÁTICO

Somente **SESSION_WEIGHTED_SIGMA** participa da nova matriz. Utilizar negócios executados válidos com `MqlTick.last`, `MqlTick.volume` ou `volume_real`, de forma consistente e auditável; NÃO utilizar contagem de ticks como se fosse volume de contratos. Uma única definição de fonte, unidades, timestamp, grade e sessão deve alimentar a VWAP, o sigma e a análise de volume. Se fonte de volume real vier ausente/zerada ou misturada, discriminar indisponibilidade; não trocar silenciosamente por contagem de atualizações de cotação. Volume inteiro de negócios (`MqlTick.volume`) pode ser válido mesmo quando `volume_real` não está disponível, desde que consistência seja demonstrada; documentar escolha por ativo/feed.

Fórmula:
- `W = Σv`; `VWAP = Σ(p×v)/W`;
- `sigma = sqrt(Σ[v×(p−VWAP)^2]/W)`;
- `d = k_atual_do_ativo × sigma`;
- `B1± = VWAP ± d`, `B2± = VWAP ± 2d`, `B3± = VWAP ± 3d`.

Preservar como input de escala-base `Inp_BandMultiplier_WIN=0.80` e `Inp_BandMultiplier_WDO=1.50`, SEM alegar que estes são ótimos, e respeitar exatamente os múltiplos uniformes 1/2/3. **Não** criar K1/K2/K3 independentes. Em ambos os ativos `d` é recalculado pela sessão atual, não pelos últimos cinco dias. Nunca interpretar 0,80 ou 1,50 como pontos fixos.

Implementação de precisão: acumulação incremental com variância ponderada numericamente estável (Welford ponderado: após `w>0`, `delta=p−mean`, `W'=W+w`, `mean'=mean+(w/W')×delta`, `M2'=M2+w×delta×(p−mean')`; `sigma=sqrt(max(M2'/W',0))`). Impedir overflow, entradas inválidas e variação negativa numericamente indevida; comparar a cada verificação independente com recálculo em lote no mesmo conjunto de negócios. NÃO recalcular toda a sessão a cada tick.

**Sessão:** ancorar na abertura regular do contrato do dia, não 00:00 do servidor. Consultar `SymbolInfoSessionTrade` e conferir sessão/relógio da corretora; prever input específico para sessão regular quando houver ambiguidade, sem modificar `Inp_StartHHMM` (início das ORDENS). Definir explicitamente inclusão/exclusão de leilão, intervalos e troca de contrato. Não assumir que o primeiro evento da plataforma coincide com a abertura regular. `TimeTradeServer`, tempo de tick e horário da série devem ser reconciliados.

**Maturidade:** `BANDS_NOT_READY` até pelo menos 300 segundos após abertura regular (input de pesquisa, não verdade empírica), volume positivo, dispersão não nula, preços em níveis distintos e dados contínuos. Todos os requisitos e falhas devem ter logs. 300s é hipótese inicial alterável, sem impor esperas adicionais depois de READY. Sem backfill falso nem mudança silenciosa para sigma D-1. Se não houver cobertura completa desde a abertura, reconstruir em chunks pela história real; até concluir, sem entradas novas, mas gestão de posições funciona normalmente.

**Integridade de negócios:** `CopyTicksRange` usa limites INCLUSIVOS em milissegundos; tratar fronteira de mesmo `time_msc` que contenha múltiplos negócios SEM duplicar ou descartar. Caso o banco revise a última fronteira, detectar divergência, reconstruir trecho ou marcar indisponível. `OnTick` não garante processamento de todos os ticks; efetuar catch-up incremental em lotes limitados, com controle de carga e cursor causal. Não fazer grandes buscas síncronas em cada `OnTick`. Em reconnect, mudança de dia e restart, recomputar sessão de modo verificável, sem disparar sinais passados retroativamente. Não incluir preços futuros em snapshot M1 fechado. Congelar `VWAP`, `sigma`, B1/B2/B3 e horário da banda no início OBSERVÁVEL da tentativa da onda e no fechamento do sinal; atualizar o mapa vivo em paralelo. O congelamento da banda NÃO congela a gestão de posições.

## 3. WEIS WAVE APRIMORADO — UM MOTOR DE ESFORÇO/RESULTADO

Substituir `RebuildWeisCache`/`ComputeLiveWaveO1` e respectivas dependências por um motor causal incremental de ondas construídas a partir de negócios executados, sem repintura de decisões anteriores. O objetivo é analisar ESFORÇO e RESPOSTA, não equiparar aumento de volume a certeza de continuação.

**Segmentação:** mudança de direção somente após reversão observada suficiente, referenciada a pivô registrado em tempo real; não virar onda por qualquer diferença de fechamento M1. Introduzir `Inp_WaveReversalPts_WIN` (hipótese inicial 60 pts) e `Inp_WaveReversalPts_WDO` (hipótese inicial 2,0 pts) como valores EXPERIMENTAIS escolhidos com base na escala dos limiares atuais de deslocamento ABS, não como parâmetros otimizados. Arredondar e validar na grade de tick do ativo. Separar momento do extremo e momento do reconhecimento; não retrodatá-lo nem usar pivot futuro para simular entrada anterior. Registrar tentativas que ainda não atingiram o limiar.

**Métricas observadas:** volume acumulado `V`, volume por segundo válido, direção da tentativa, preço inicial, maior excursão favorável e contrária, soma do percurso absoluto entre negócios (`grossPath`), deslocamento líquido direcional (`netProgress`), idade, volume relativo às últimas até 10 ondas FECHADAS ANTES do instante do sinal, `pathEfficiency = netProgress/grossPath` quando `grossPath>0`; caso contrário estado INDETERMINADO, nunca eficiência zero inventada. Sem misturar uma onda ativa ao denominador de sua própria referência. Dados anteriores à sessão podem servir só como BASELINE HISTÓRICA DE VOLUME se explicitamente causal, não como VWAP/POC/região D-1; documentar isso. Exigir quantidade suficiente de ondas de referência, senão registrar `WAVE_BASELINE_NOT_READY` e não inventar força relativa.

Preservar inputs existentes `Inp_ABS_Effort=1.50`, `Inp_CONT_Effort=1.50` e, se ainda fizerem sentido na tese nova, `Inp_ABS_BreakoutEffort=1.50`, `Inp_CONT_BreakoutEffort=1.50`; documentar a semântica exata. Não reinterpretar silenciosamente 1,50 como garantia de qualidade. Expor medidas de ritmo e trajetória sem criar votos independentes redundantes.

**Hipóteses quantitativas novas para pesquisa, NÃO otimizadas:** `Inp_CONT_MinPathEfficiency=0.60`, `Inp_ABS_MaxPathEfficiency=0.30`, `Inp_ABS_MinRejectionFraction=0.35`, com validações de faixa e logs. Se o desenho da onda tornar algum teste circular, conflitante ou irrealizável em tempo causal, NÃO simular cumprimento: interromper a implementação dessa regra e apresentar uma proposta de correção com caso reprodutível. Rejeitar `NaN`, ausência de volume, divisão por zero, amostra incompleta ou comparação em unidades heterogêneas.

**CONT BUY/SELL:** evidência de esforço na direção, progresso líquido positivo e suficiente, eficiência de percurso acima do input, manutenção observável do progresso e nenhuma rejeição/invalidação objetiva. Como início experimental para magnitude de progresso usar os inputs CONT atuais WIN 50 pts/WDO 1,5 pt, indicando expressamente que muda a origem da medição (antes vinha de janela POC). Não exigir cor específica de vela como confirmação redundante; sinal só fica ARMADO após fechamento causal da M1 que reconheceu a hipótese. Manter registro do que o fluxo detectou ainda dentro da M1, sem gerar sinal retroativo.

**ABS BUY/SELL:** tentativa contrária à direção da reversão, esforço elevado na tentativa, resposta ineficiente relativamente ao volume, excursão observável, rejeição posterior **positiva e confirmada** pela trajetória e fechamento da M1 do sinal. Rejeição não deve depender apenas de banda ou de um candle isolado. Avaliar separadamente máximo progresso anterior, reversion/drawdown do extremo, tempo e volume; quantidade mínima de rejeição proporcional à excursão (`Inp_ABS_MinRejectionFraction`) e pelo menos um tick válido. Um preço imóvel com percurso zero não se torna ABS executável; classificar apenas candidato/inconclusivo. Se a onda de esforço estiver sendo encerrada, conservar evidências congeladas da onda original, mas registrar a hora real da confirmação da reversão.

**Exclusividade:** estado `CONT_BUY`, `CONT_SELL`, `ABS_BUY`, `ABS_SELL`, `NEUTRO`, mais estados diagnósticos de CANDIDATO/INDETERMINADO. Se houver disputa entre teses, não atribuir prioridade arbitrária a uma; registrar conflito e deixar NEUTRO até uma hipótese ganhar critérios mensuráveis. Não permitir troca oposta a cada minuto sem registrar qual evidência nova justificou a troca.

## 4. LOCALIZAÇÃO ≠ DIREÇÃO; POLÍTICA GEOGRÁFICA AUDITÁVEL

O motor de ondas classifica o **mercado** mesmo que determinada rota não esteja autorizada geograficamente. Em etapa separada, o mapa decide ELEGIBILIDADE OPERACIONAL. Registrar sempre `DETECTED_DIRECTION`, `BAND_POSITION`, `LOCATION_ELIGIBLE` e `BLOCK_REASON`.

- Acima da VWAP: política inicial permite `CONT_BUY` (até +B2) e `ABS_SELL` (com rejeição); abaixo da VWAP, `CONT_SELL` (até -B2) e `ABS_BUY` (com rejeição).
- De 0 a ±B2, permitir CONT com esforço/resultado válidos. Entre B2/B3 e além, CONT ainda é DETECTADA e auditada, mas nova ordem dessa CONT não é elegível pela política inicial. Reversão na terceira banda NUNCA é automática.
- Uma CONT SELL comprovada por volume mas ainda acima da VWAP deve ser DETECTADA e logada como `LOCATION_INELIGIBLE`, não apagada da inteligência. Idem ao caso simétrico.
- Não reintroduzir faixa morta artificial 0,40–0,60 próxima ao centro. Em preço exatamente sobre VWAP, localização ambígua → logar sem inventar lado. Evitar histerese artificial que não tenha sido autorizada.
- Usar fotografia das bandas no instante causal de reconhecimento/armamento para avaliar elegibilidade; a expansão do sigma posterior não pode retroativamente reclassificar a tese. Mapas vivos servem ao monitoramento e à identificação de evidência NOVA; não vetar silenciosamente um sinal por simples migração matemática da banda.

Preservar M5 como contexto temporal; NÃO transformar o M5 em novo veto direcional de votação. M1 fechado continua referência do sinal. Ticks/negócios acompanham a evolução e invalidação enquanto armado.

## 5. ARMAMENTO, GATILHO E EXECUÇÃO — BLOCO PROTEGIDO

Para TODA ABS/CONT nova: preço de referência = **fechamento da M1 do sinal** (`shift 1`) congelado; BUY trigger = `RoundUpTick(close + margem)` e SELL trigger = `RoundDownTick(close − margem)`. PRESERVAR `Inp_BreakoutMargin_WIN=175.0`, `Inp_BreakoutMargin_WDO=3.5` e todas as verificações reais de preço negociado após a tese, grade, sequência temporal, bid/ask executável, spread, overshoot, cota, risco, BE e controle de ordens. Sem pullback obrigatório, sem recálculo do gatilho por máxima/mínima anterior, sem deslocar o gatilho na vida do sinal. `Inp_ArmedTimeoutSec=300` permanece e não se renova por sinal novo descartado.

Tirar os velhos vetos (`LATE_WEIS`, `LATE_DIRECTION`, `LATE_GLASS`) e substituí-los por uma **função única de revalidação** da tese aprovada, baseada nos mesmos estados de onda/resultado que geraram o sinal, mais o FAR preservado. Reavaliação deve ser causal e não alterar referência/trigger; `INDETERMINADO` na evidência crítica cancela ou deixa em espera conforme semântica explícita, nunca aprova silenciosamente. As proteções financeiras e operacionais continuam aplicadas em TODAS as etapas, inclusive `SendOrder`.

**Sinais concorrentes:** enquanto ARMADO, continuar monitorando a tese atual e classificar novas hipóteses em modo OBSERVAÇÃO. Nova tese não envia segunda ordem nem renova timeout. Substituição/cancelamento apenas por invalidação mensurável posterior; não intervir depois de solicitação de ordem potencialmente despachada, posição aberta ou recuperação pendente. Preservar idempotência e bloqueio de execução ambígua.

**FAR:** manter os três modos `FAR_OFF`, `FAR_OBSERVAR`, `FAR_APLICAR`, default `FAR_APLICAR`, e `Inp_AggressionThresholdPct=60`. Preservar flags/negócios e sua verificação das duas metades, identidade, sequência temporal, agressão contrária sustentada e falha de dados não interpretada como prova. Para a referência estrutural atualmente dependente de `armed.regionHigh/regionLow`, permitir coleta de extremos congelados EXCLUSIVAMENTE PARA A PROTEÇÃO FAR (não como condição de armar nem como gatilho), ou substituir por referência equivalente demonstrada em testes. NÃO enfraquecer silenciosamente a proteção. O `ComputeTrigger()` antigo usado no rótulo `FAR_FAVORAVEL` deve passar a consultar `armed.entry.trigger`, sem modificar o gatilho de mercado. Registrar diff comportamental de FAR. Se não houver referencial verificável, `FAR_INDETERMINADO`, sem inventar evidência favorável/contrária, preservando sua política de falha já vigente.

**Mensagem de log:** `DISPARO` é pré-envio; NÃO tratar como negócio. Registrar separadamente `SIGNAL_DETECTED`, `ARMED`, `THESIS_INVALIDATED`, `TRIGGER_CONFIRMED`, `DISPATCH_GUARD`, `SEND_ATTEMPT`, `REQUEST_ACCEPTED/REJECTED`, `DEAL_CONFIRMED`, `ORDER_FAILED`, com preço, milissegundos, motivo, ID correlacionado e `MqlTradeResult.retcode` quando existente. Não afirmar que ordem foi executada sem negócio confirmado.

## 6. PERSISTÊNCIA E REGRESSÃO FINANCEIRA — INVIOLÁVEL

Antes de codificar, mapear todas as leituras/escritas que incluem `mode`, `route`, `signalID`, Magic, comentário `S1995|...`, tickets, requests, `POSITION_ID`, BE, snapshots e CSV. NOVAS entradas podem usar `mode=STANDARD` sem TURBO, mas as funções de recuperação **devem continuar aceitando modos antigos**. Se `STANDARD` quebrar parser ou persistência, criar mapeamento retrocompatível e provar o funcionamento. Não modificar estrutura de históricos já escritos. Preferir novo arquivo versionado para diagnósticos da matriz, preservando intacto CSV financeiro existente e prefixos persistentes. Qualquer necessidade real de mudança nos parsers financeiros exige prova reproduzível e diff mínimo; nunca remodelar conta de resultado.

Validar arranque/restart em: sem posição; posição própria com BE pendente; pedido enviado mas resposta incerta; ordem pendente; posição estrangeira no mesmo símbolo netting; execução parcial; EOD; rollover diário; histórico/journal indisponível. Confirmar que novo módulo não impede o BE, EOD ou a reconciliação mesmo em falha de VWAP/volume.

## 7. ENGENHARIA DE PERFORMANCE

Não consultar janelas de ticks sobrepostas integralmente por evento. Processar fluxos em chunks limitados com cursor exato, caches, snapshots imutáveis para M1 e M5, sem `FileFlush` por tick nem `Print` por negócio. Os eventos `OnTick` do MT5 podem coalescer enquanto outro está rodando; recuperar os negócios pela série, não assumir 1 callback por negócio. Medir custo dos módulos em microssegundos, inclusive p95, p99 e máximo; medir atrasos entre último negócio, reconhecimento de sinal, gatilho, envio e preenchimento. Caso tick read sincronize lentamente, não bloquear proteção financeira. Erro de dados → nenhuma nova ordem baseada em evidência incompleta; gestão existente permanece ativa.

## 8. PROTOCOLO DE REFUTAÇÃO E TESTES OBRIGATÓRIOS

Antes de indicar conclusão, tentar FALSIFICAR o desenho com casos determinísticos:

A. **Sigma:** pares com mesmo volume (100,110) → VWAP 105/sigma 5; adicionar 98 volumes em 110 → preço permanece 110 enquanto posição padronizada cai acentuadamente; uma ABS não pode surgir/desaparecer só por reposicionamento das bandas.
B. **Ondas:** sequência 100→104→100 vs 100→100→100, com mesmo volume, não podem ser interpretadas como a mesma reação. Seq. 100→104→108 sem retorno deve favorecer hipótese CONT, não ABS. Esforço elevado sem rejeição não valida ABS.
C. **Causalidade:** nenhum sinal pode usar pivô ainda não confirmado, vela M1 viva como fechamento ou bandas recalculadas após o sinal. Replay tick-a-tick deve reproduzir mesmo sinal e trigger (quando dados equivalentes).
D. **Fonte:** CopyRealVolume com quantidade correta mas todos zeros; volume inteiro de negócios válido; eventos com mesmo milissegundo; reconexão com intervalo ausente; reinício às 10h; leilão; sessão irregular; mudança de contrato. Sem duplicar volume nem inventar baseline.
E. **Localização:** CONT SELL detectada acima da VWAP mas não elegível; CONT BUY só até B2; sigma expande após sinal sem cancelamento retroativo; posição exatamente VWAP não herda lado oculto; banda terceira não manda reverter automaticamente.
F. **Execução:** BUY close+175 WIN; SELL close−175; BUY close+3,5 WDO; SELL close−3,5. Overshoot original, spread, timeout, stops, lote máximo, BE, EOD e bloqueios financeiros mantidos. `DISPARO` não equivale a fill.
G. **FAR:** preservar veto de agressão contrária após armamento e as duas metades, não enfraquecer em falta de dados, não usar sinal antigo para provar CONT favorável.
H. **Compatibilidade:** recuperação de negócios `BASE`, `TURBO`, `BASE_CONT`, `TURBO_CONT` anteriores; BE progressivo; pending request; partial fill; exchange/netting/hedging; sem alteração dos registros originais.
I. **Arquitetura:** verificar `rg/grep` por `POC`, `VWAP_D1`, `d1Ready`, `c23`, `turbo`, `REGION_INVALID`, `LATE_GLASS`, `LATE_DIRECTION`, etc.; cada remanescente precisa justificativa como compatibilidade histórica ou ser removido. Nenhuma condição de entrada usa dados amputados.
J. **Matriz:** contar razões de neutralidade, detecção versus elegibilidade, oportunidades não armadas por tese anterior, gatilho não acionado, rejeição, execution failure; não inferir edge pela beleza dos movimentos.

Fazer comparação sobre o mesmo feed observacional, com a versão 1.995 congelada e nova versão separada; não executar duas versões independentes enviando ordens para a mesma conta netting. Em execução real controlada, manter exposição e proteções vigentes; não prometer taxa de acerto. Trabalhar também com séries M1 apenas para testes unitários não dependentes de tick; nunca usar ticks sintéticos como prova de microestrutura real.

## 9. ENTREGÁVEIS E PORTÕES DE ACEITE

1. `AUDITORIA_PREVIA.md`: mapa de funções/inputs e dependências, áreas financeiras congeladas, riscos de semântica, fontes de feed, decisões e hipóteses; SHA-256 da base.
2. Fonte `.mq5` novo, original intocado, diff exato por arquivo/funcionalidade.
3. `INPUTS_DIFF.md`: para cada input atual, classificar **INALTERADO**, **REMOVIDO porque exclusivo da matriz antiga** ou **NOVO hipótese de pesquisa**. Nunca alterar default/semântica dos controles financeiros existentes.
4. `REGRESSION_FINANCE.md`: provas de que BE, SL/TP, stops, Magic, sizing, cooldown, EOD, reconciliadores, journal e recuperação não mudaram, salvo o multiplicador TURBO autorizado.
5. `TEST_CASES.md` + resultados automáticos para os casos da seção 8, inclusive casos que REFUTARAM a implementação e como foram corrigidos.
6. Compilação NATIVA no MetaEditor com **0 erros**; relatar warnings reais e corrigi-los sem mexer indevidamente em finanças. Se não houver ambiente de compilação, declarar claramente `COMPILACAO_NATIVA_NAO_VERIFICADA`, sem alegar sucesso ou pronto para produção.
7. Teste de desempenho, controle de cursor, sigma, precificação e logs com timestamps. Se não houver ticks reais suficientes, relatar `DADOS_INSUFICIENTES`, não inventar resultado.
8. `CHANGELOG_CIRURGICO.md` com alterações aprovadas, riscos remanescentes e decisão explícita de **NÃO HOMOLOGADO** caso qualquer teste crítico esteja faltando.

**Regras de decisão:** não usar pseudo-código como entrega; não modificar gestão financeira para satisfazer testes; não copiar trecho do PDF com quebra de linha e declarar compilado; não “corrigir” falha financeira fora de escopo sem autorização; não escolher parâmetros como se fossem estatisticamente ótimos; não usar nenhuma informação futura. Caso uma instrução de entrada entre em conflito com segurança financeira, prevalece a SEGURANÇA, documentando o conflito. Se houver lacuna matemática que impeça implementação causal, apresentar a questão e o menor conjunto de alternativas com seus trade-offs — não inventar regra oculta.

**Resultado exigido:** uma Rêmora que decide por localização + esforço + resultado, com sigma automático, três bandas uniformes, Weis Wave causal, absorção/continuação mutuamente exclusivas, gatilhos e proteções antigos preservados, desempenho auditável e nenhuma dependência operacional morta de POC ou D-1.
