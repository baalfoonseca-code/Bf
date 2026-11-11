# Casos adversariais e limites da validação

Esta entrega exige separar execução numérica, comparação estática e validação no
terminal. Um teste de funções MQL5 extraídas e compiladas como C++ não é
compilação nativa MetaEditor nem prova do comportamento do Strategy Tester.
Negócios sintéticos servem para refutar fórmulas e máquinas de estado; não provam
microestrutura, latência, continuidade do feed, acurácia ou resultado financeiro.

## Resultados locais executados

Comando para repetir a validação completa: `python3 -m unittest discover -s tests -v`.
As últimas execuções por suíte tiveram os seguintes resultados:

| Suíte | Testes | Resultado / alcance |
| --- | ---: | --- |
| `test_entry_contract.py` | 11 | Passaram; funções reais do núcleo de gatilho e despacho extraídas do EA |
| `test_financial_invariants.py` | 15 | Passaram; comparação financeira/inputs, kernel BE/proteção e guardas reais com serviços simulados |
| `test_objective_engine.py` | 15 | Passaram; kernel numérico real, ondas/classificação e compilação do módulo inteiro com APIs simuladas |
| `test_runtime_contract.py` | 20 | Passaram; módulo inteiro, histórico simulado e contrato de integração M1 fechada |

São 61 testes locais por suíte, sem skips nessas execuções. Os detalhes de cada
assertion constam nos arquivos executáveis. Não são 61 testes no MetaTrader nem
uma contagem de cenários de mercado independentes.

Durante a implementação/revisão foram encontrados e corrigidos:

1. **Desencontro de relógio M1:** integração passava o início da barra viva a
   uma API que exigia o início da barra fechada. Corrigido para `shift 1`, com
   verificação `closed + PeriodSeconds == current`; o teste de integração cobre
   esse contrato e o runtime confirma que negócios do minuto seguinte não
   alteram a fotografia fechada.
2. **Fronteira same-ms:** a versão inicial rejeitava acréscimos legítimos de
   negócios no último milissegundo. O coletor agora exige prefixo idêntico e
   aplica somente o sufixo novo, uma vez. Remoção/reordenação/revisão continua
   indisponível; acréscimo que altera uma fotografia já fechada invalida sua
   época, sem fabricar um sinal retroativo.
3. **Aritmética do verificador:** somas de pesos com ordenação diferente usam
   tolerância numérica explícita, mantendo contagem exata e erro de VWAP/sigma
   relativo ao tick. A referência independente usa cálculo em duas passagens
   por lote e combinação Chan, sem subtração instável de momentos absolutos.
4. **Last divergente do histórico:** a revalidação aguardava o cursor, mas não
   garantia que o Last da quote ainda fosse o negócio coletado. Agora preço,
   relógio e identidade do último negócio precisam coincidir; quote sem negócio
   só retém Last já comprovado. Os testes demonstram primeiro uma tese válida,
   depois espera para preço/volume divergente no mesmo milissegundo.
5. **Inventário estático:** a limpeza de `RecordPerf`/`ResetPerfStat`, exclusivos
   do motor analítico removido, foi inicialmente reportada como função protegida
   ausente. A auditoria classifica nominalmente essas remoções; não houve ajuste
   no núcleo financeiro para satisfazer esse teste.

## Contrato de entrada executável

`python3 -m unittest discover -s tests -p test_entry_contract.py -v` extrai as
funções reais da candidata, sem replicar as condições em Python, e compila um
harness C++ temporário. Stubs fornecem tipos de terminal, matemática elementar e
normalização decimal; o código de preço/tempo/validação vem do EA entregue.

| Caso | Evidência exigida |
| --- | --- |
| WIN BUY/SELL | Fechamento 100.000 gera 100.175 / 99.825, preservando margem 175 |
| WDO BUY/SELL | Fechamento 5.000 gera 5.003,5 / 4.996,5, preservando margem 3,5 |
| Referência inválida | NaN, preço fora da grade, direção inválida e margem zero não produzem gatilho alternativo |
| Posterioridade | Negócio no instante da tese não confirma; negócio posterior pode confirmar |
| Mesmo milissegundo | Alteração no mesmo milissegundo não fabrica segundo evento ordenado |
| Perda do gatilho | Novo negócio abaixo/acima do gatilho perde confirmação; preço de referência e trigger continuam congelados |
| Atualização só de quote | Não inventa Last confirmado; preserva apenas evidência válida cujo Last não mudou |
| Quote/relógio inválido | Cruzamento bid/ask, NaN, tempo ausente e execução sem rompimento impedem despacho |
| Despacho único | `ClaimEntryDispatch` só aprova uma vez; nova confirmação não reabre ciclo reclamado |
| Timeout | 299 s mantém prazo; 300 s expira; relógio regressivo não simula expiração |
| B3 congelada | BUY estritamente abaixo da B3 superior e SELL acima da B3 inferior; igualdade, ultrapassagem e mapa indisponível são rejeitados |

Os testes não permitem que B3 altere um stop, take-profit ou posição aberta. O
teste estático financeiro verifica separadamente a preservação desses caminhos.

## Refutação da eficiência bruta

O problema é reproduzível sem lucro/perda como critério:

- A: `100,102,104,106` → progresso 6, caminho bruto 6, eficiência 1.
- B: `100,101,100,101,100,102,103,102,104,105,104,106` → progresso 6, caminho bruto
  14, eficiência `3/7`. Extremos e progresso são iguais; oscilações de um tick
  fariam o limiar 0,60 mudar a decisão.

Fragmentar um negócio em vários negócios ao mesmo preço não muda `grossPath`,
mas o bounce adicional muda. A eficiência bruta permanece observacional. A
amostragem causal por eventos de preço de dois ticks passou pelos casos de
fragmentação/bounce executados no kernel entregue; o numerador usa o mesmo
endpoint dos eventos e registra separadamente o resíduo até o negócio atual.
Não há clamp para ocultar eficiência maior que um. Estes casos não provam
robustez para oscilações maiores, feeds distintos ou mercado real; dois ticks é
hipótese de engenharia, não parâmetro otimizado.

## Coletor e serviços simulados

`test_runtime_contract.py` usa `mql_engine_harness.py` para compilar o include
inteiro. A adaptação é superficial: arrays dinâmicos, declarações `input`, casts
de string e resolução de funções globais. As rotinas reais de coleta, cálculo,
fronteira, fotografia, prontidão e revalidação permanecem no harness. Os stubs
fornecem respostas determinísticas para `CopyTicksRange`, sessão, relógios,
sincronização, conexão e escrita de telemetria.

Foram exercitados multiplicidade e acréscimo same-ms, revisão/remoção/reordenação,
invalidação de fotografia revisada, separação entre M1 fechada e negócio futuro,
reconstrução sem sinal passado, fonte integral válida, mistura/zero/NaN inválidos,
lacuna de feed, prazo mínimo sem garantia de sigma, preço imóvel após 300 s,
agenda ausente/ambígua, override regular fora da agenda, desconexão/reconexão,
quote à frente do cursor e Last/volume divergentes. O motor não lê histórico no
caminho de tick para resolver essas ambiguidades; aguarda a coleta do timer.

O limite de lacuna é diagnóstico de engenharia: ausência de erro no histórico
não prova completude de todos os negócios da bolsa. Um print adicional
**byte a byte idêntico** no mesmo milissegundo é indistinguível na quote isolada;
sua multiplicidade é reconciliada na próxima releitura da fronteira. Essa
limitação não autoriza presumir que cada callback contém um negócio único.

## Matriz de validação obrigatória

| Especificação | Prova local / portão necessário |
| --- | --- |
| A — sigma ponderado | Incremental versus referência independente nos mesmos negócios; pesos desiguais; preços iguais; cenário 100/110 e acréscimo de 98 volumes em 110 |
| B — ondas | Trajetória monotônica não valida ABS por esforço sozinho; trajetória com excursão e retorno difere de preço imóvel; ineficiência pertence à tentativa original, nunca à reação que deve avançar |
| C — causalidade | M1 fechada e bandas sem negócio futuro; reconhecimento de reversão sem retrodatação; reconstrução às 10h não arma sinais das 9h |
| D — fonte/cursor | Real/integral válidos, zero/NaN/mistura rejeitados; multiplicidade de mesmo-ms preservada; revisão de prefixo, reconexão e cobertura incompleta tornam o mapa indisponível |
| E — geografia | B2 inclusiva para novo sinal, B2–B3 inelegível; trigger e execução CONT estritamente antes de B3 congelada; ABS B1/B2/B3 dependem de rejeição; igualdade VWAP explicitamente sem lado |
| F — execução | Kernel de entrada extraído; spread/overshoot/stops/margem/cota/risco protegidos por comparação do código financeiro; DISPARO não significa deal |
| G — FAR | Duas metades, pressão posterior, flags e estrutura preservadas; falta de estrutura é indeterminada; diagnóstico usa trigger congelado real |
| H — recuperação | Parsers BASE/TURBO e journals preservados estaticamente; reinícios, fills parciais, netting/hedging/exchange e EOD exigem terminal |
| I — remoções | Ausência de POC, preço D-1, votação e vetos antigos nos caminhos estratégicos; remanescentes de schema financeiro documentados |
| J — telemetria | Contagens de neutralidade, detecção/elegibilidade, sinais observados durante ARMED, timeout, rejeição e envio; frequência B1/B2/B3 por ativo requer feed real |

## Portões externos

`COMPILACAO_NATIVA_NAO_VERIFICADA`: MetaEditor/MetaTrader 5 não foram encontrados
neste ambiente Linux. Não há resultado nativo de zero erros ou warnings.

`DADOS_INSUFICIENTES`: não há feed real WIN/WDO ou replay fornecido para medir
frequência B3, instante real de READY, oscilação do sigma após READY, percentis
operacionais, cobertura e diferenças entre corretoras. Esses resultados não
podem ser substituídos por contagens sintéticas.

A candidata permanece **NÃO HOMOLOGADA** enquanto os portões nativos e de dados
continuarem pendentes. O relatório final deve registrar os resultados reais das
suítes locais, incluindo falhas corrigidas, sem converter testes não executados
em aprovações.


## Integração posterior a54fbc54

A rodada corrente executou96 testes: as61 provas anteriores,10 testes de consolidação,16 de recuperação/admissão/caracterização CONT e9 da sequência completa de callbacks/decisão/SendOrder, usando stubs explícitos de serviços financeiros. Resultado exato em `artifacts/integracao_1996/test-results.txt`.

O fixture `tests/fixtures/OnTick_54fbc54.mql` preserva o callback controle daquela revisão, com hash verificado pelo teste. A comparação reproduz uma tentativa API sintética aos250ms com a nova admissão, enquanto a agenda anterior observa a retração antes do timer e perde a oportunidade sintética. Isso não é fill ou medição de mercado. Sob saturação acima do orçamento, o teste exige zero confirmação/envio retroativo. Mutação de quote durante a guarda também impede preparação e despacho.

A caracterização de CONT confirma recuo de2ticks cancelando mesmo sem reversão da onda, em BUY/SELLWIN/WDO. A regra foi preservada; o teste não valida sua qualidade preditiva nem resolve a ambiguidade estratégica. A recuperação exige duas leituras consistentes e comparação de volume com M1; falta ou divergência no agregado do broker mantém bloqueio.
