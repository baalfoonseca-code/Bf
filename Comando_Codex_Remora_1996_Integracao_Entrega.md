# COMANDO DEFINITIVO AO CODEX — RÊMORA 1.996

## Missão e revisão correta

Audite e conclua a integração e a entrega da Rêmora Scalper 1.996 existente no repositório `baalfoonseca-code/Bf`, branch `codex/remora-matriz-objetiva`. Não use a ausência dos arquivos em `main` como prova de que não existem.

A revisão conferida é `9ebc9eedd2243c44601efd9dfb125bc4fcacb55e`. Identifique o HEAD efetivo antes de trabalhar. Se houver revisão posterior, mostre o diff e faça os testes nela, sem misturar arquivos de commits diferentes.

Leia integralmente, em conjunto:

- `RemoraScalper_MatrizObjetiva.mq5`;
- `include/ObjectiveMatrix.mqh`;
- `AUDITORIA_PREVIA.md`;
- `REGRESSION_FINANCE.md`;
- `DEPENDENCIAS_1.996.md`;
- `Comando_Codex_Remora_1995_Matriz_Objetiva_REVISADO.md`;
- os testes em `tests/` e seus resultados.

Os arquivos já existem nessa branch. Não recrie a estratégia, não substitua o módulo por stubs e não volte à matriz antiga para contornar dificuldades. O Word/PDF isolado não contém o módulo e não substitui esse conjunto nativo.

Preserve a revisão atual e o arquivo original `1995`. Trabalhe em branch própria, com commits e diff verificáveis. A base financeira de comparação é `1995`, SHA-256 `2479ed8e5c9189438d787be1e804abbd95f9e1c06e01042e560251e64ef67fc5`.

## 1. Fronteira autorizada

Esta tarefa autoriza correções demonstráveis de integração, sincronização, recuperação analítica e empacotamento, além dos testes correspondentes. Não autoriza escolher novos critérios estratégicos, alterar parâmetros para aumentar entradas ou reescrever o núcleo financeiro.

Preserve a especificação objetiva revisada: VWAP/sigma da sessão, ondas causais, ABS/CONT, fotografias congeladas, geografia B2/B3, fechamento M1 como referência e margem WIN 175/WDO 3,5. Não reintroduza POC, D1, C1–C5 ou pullback obrigatório retirados nessa evolução. Não imponha a antiga contagem de 72 inputs à arquitetura atual; conte e documente os parâmetros efetivos.

Preserve os controles financeiros, SL/TP, BE, escada até proteger +5R, sizing, horários, timeout, limites, FAR, propriedade de posições, hedge/netting/exchange, journals, persistência, reconciliação, recuperação e EOD. A remoção do multiplicador TURBO para novas entradas fixas já foi autorizada; não a reverta nem altere o sizing percentual. Mantenha reconhecimento dos identificadores históricos.

Não renomeie Magic, comentários ou namespaces financeiros para resolver conflitos de compilação. Uma falha analítica nunca pode impedir proteção de posição existente nem liberar uma obrigação financeira pendente.

## 2. Sincronização do fluxo e oportunidade de execução

Audite conjuntamente `OMServiceStep()`, `OMReadChunk()`, `OMVerifyBoundary()`, `OMLiveReady()`, `EvaluateMatrix()`, `ObjectiveRevalidate()`, `ProcessArmedSignal()`, `EntryDispatchGuard()`, `OnTick()` e `OnTimer()`.

Na revisão conferida, a coleta analítica ocorre pelo timer de um segundo e `OMLiveReady()` exige que o cursor tenha ultrapassado o timestamp avaliado. Um tick novo pode, portanto, aguardar a próxima coleta. Testes existentes que aprovam esse bloqueio não demonstram que uma oportunidade será processada a tempo.

Teste a sequência completa com ticks entre timers, fluxo intenso, processamento mais lento que a chegada de negócios, salto além do gatilho, retração antes do timer, overshoot e mudança de cotação durante a decisão. Registre atraso, espera, cancelamento e oportunidade perdida; não apresente números sintéticos como latência medida no mercado.

Verifique múltiplos negócios no mesmo milissegundo, preços iguais com volumes diferentes, ida e volta ao mesmo preço, flags desconhecidos e atualização exclusiva de bid/ask. Igualdade entre `tk.last` e `gOMLastPrice` não substitui a prova de avanço do fluxo. Descreva o cursor e os limites do histórico fornecido; não prometa identificar negócios que a API não permite distinguir.

Corrija falhas reproduzíveis de integração e processamento, mantendo causalidade, limites de carga e precedência financeira. Não resolva atrasos removendo a prontidão, usando cotações antigas, inventando confirmação retroativa ou fazendo buscas extensas de histórico em cada tick. Não prometa eliminar toda latência.

## 3. Lacunas, sessão e recuperação analítica

Na revisão conferida, `Inp_FeedMaxGapSec=30` e falhas como `FEED_COVERAGE_GAP`/`TRAILING_FEED_GAP` podem tornar `gOMFault` permanente. Um novo negócio, isoladamente, não limpa esse estado.

Reproduza abertura atrasada, leilão, período legítimo sem negócios, histórico temporariamente indisponível, reconexão e lacuna efetiva. Distinga o que os dados comprovam do que permanece indeterminado. Trinta segundos sem negócios não comprovam, por si sós, corrupção do histórico.

Implemente recuperação analítica controlada quando a cobertura puder ser novamente verificada: reconstrução limitada, nova época de dados, invalidação de snapshots incompatíveis, nenhuma entrada durante a recuperação e nenhum sinal retroativo. Não limpe `gOMFault` apenas porque chegou um tick, não ignore lacunas e não aumente silenciosamente o limite.

Se a lacuna continuar sem solução verificável, mantenha novas entradas bloqueadas, com motivo explícito. A gestão financeira permanece ativa. Não fabrique abertura de sessão ou cobertura ausente.

## 4. Invalidação de CONT e semântica dos inputs

Na revisão conferida, `OMRevalidate()` pode invalidar CONT quando `drawdown >= cfg.eventStep`, e `eventStep = Inp_PathEventTicks * gTickSize`. Com default de dois ticks, isso corresponde a 10 pontos no WIN e 1 ponto no WDO, quando os tamanhos de tick forem respectivamente 5 e 0,5.

Reproduza compras e vendas: CONT válida, pequeno recuo, manutenção da direção da onda e posterior retomada. Demonstre qual condição cancela e confronte-a com a especificação objetiva revisada. Verifique o reaproveitamento de um parâmetro de amostragem do caminho como tolerância de invalidação.

Não remova a proteção, aumente o limiar ou crie nova regra por conta própria. Corrija divergências inequívocas da especificação. Se a decisão exigir escolher uma nova tolerância estratégica, apresente a ambiguidade e a menor alteração proposta; não a implemente silenciosamente nem declare esse ponto resolvido. O teste comprova o comportamento, não sua qualidade preditiva.

## 5. Sigma, bandas, ABS/CONT e FAR

Execute o código efetivamente entregue, não apenas uma réplica independente dele. Compare o sigma incremental ponderado por volume com cálculo independente sobre os mesmos negócios. Inclua preços 100/110 com volumes 1/1: VWAP 105, sigma 5; depois mais 98 de volume em 110: VWAP 109,9 e sigma aproximadamente 0,994987.

Comprove bandas em ±Kσ, ±2Kσ e ±3Kσ, escala por ativo, sessão correta, aquecimento e indisponibilidade de dados. Teste congelamento das bandas, B2 inclusiva para armar CONT e gatilho/preço executável estritamente antes da B3 congelada. B3 não fecha posição existente.

Teste ABS/CONT em compra e venda, esforço sem avanço, reação posterior, trajetória imóvel, ida e volta, ruído de preços, referências insuficientes e conflito de teses. Nenhum snapshot pode usar negócios posteriores ao seu instante causal.

Preserve FAR_OFF/OBSERVAR/APLICAR, default vigente APLICAR/60%, duas metades, volume desconhecido no denominador e política vigente de indisponibilidade. Extremos congelados usados exclusivamente pelo FAR não voltam a determinar gatilho nem se tornam requisito de armamento. FAR não pode apagar journals ou interferir em requisição possivelmente despachada.

## 6. Provas financeiras e compilação

Execute `python3 -m unittest discover -s tests -v`, examine os testes e acrescente os cenários de integração descritos acima. Os 61 testes da revisão conferida já passaram em ambiente portátil; não confunda isso com compilação MQL5, servidor MT5 ou validação financeira em mercado real.

Compare as funções e estruturas financeiras com `1995`. Preserve especialmente `SendOrder`, `ManageBreakEven`, `OnTradeTransaction`, `ProcessEOD`, parsers, journals e recuperação. Mostre o diff das integrações alteradas. Identidade textual de funções não prova, sozinha, equivalência operacional de todos os caminhos.

Compile no MetaEditor se disponível, informando versão/build, arquivo/commit, erros, warnings e log real. Corrija erros demonstrados sem mutilar a estratégia. Se indisponível, declare `COMPILACAO_NATIVA_NAO_VERIFICADA`; não informe zero erros ou aprovação nativa.

## 7. Entrega completa para o usuário

Entregue um ZIP contendo o `.mq5`, `include/ObjectiveMatrix.mqh`, demais dependências próprias, testes, diff e documentos atualizados, todos da mesma revisão. Preserve o diretório relativo do include.

Entregue também `RemoraScalper_1996_Completo.mq5`, para meu processo de copiar o código para o MetaEditor. Incorpore fielmente o módulo e eventuais dependências próprias, preservando os includes da biblioteca padrão Trade. Não basta apagar o include. Não use abreviações, trechos omitidos ou placeholders.

Verifique a equivalência entre a versão modular e a consolidada, ordem/defaults dos inputs e ausência de dependências próprias não entregues. Registre SHA-256 e instruções de instalação. O arquivo consolidado não pode receber uma segunda implementação da estratégia.

Atualize `AUDITORIA_PREVIA.md`, `REGRESSION_FINANCE.md` e `DEPENDENCIAS_1.996.md` com evidências reais e limitações. Informe branch, commit, caminhos e links da entrega. Não sobrescreva históricos nem ative o EA de produção.

Finalize com uma tabela objetiva: problema, evidência, correção realizada, teste executado e pendência. Separe pacote completo, compilação, testes portáteis, testes MT5 e validação operacional. Não declare execução real autorizada ou superioridade estatística apenas porque os arquivos existem ou compilam.

Execute as correções tecnicamente demonstradas dentro desse escopo. Não substitua os fontes e testes por um relatório, não recrie o módulo que já existe e não declare conclusão integral enquanto houver requisito crítico pendente.
