# Candidata experimental 1.996 — matriz objetiva

**NÃO HOMOLOGADO. COMPILACAO_NATIVA_NAO_VERIFICADA. DADOS_INSUFICIENTES para validação de microestrutura real.**

Base: main `dabaa1a57b54350b72a91ee821c965a7bbb6b455` de `baalfoonseca-code/Bf`. Branch local: `codex/remora-matriz-objetiva`. Fonte canônico `1995` intacto; SHA-256 `2479ed8e5c9189438d787be1e804abbd95f9e1c06e01042e560251e64ef67fc5`. O comando revisado é a autoridade; PDF é secundário e não estava disponível. Não houve merge, push, publicação ou ativação em conta.

## Código entregue

- `RemoraScalper_MatrizObjetiva.mq5`: cópia integral verificada da base antes das substituições. Mantém o subsistema financeiro original, integra a matriz nova e declara versão1.996. Identidade financeira continua `S1995`, com mesmos Magic, locks, arquivos e journals.
- `include/ObjectiveMatrix.mqh`: motor de dados e decisão sem acesso a posições, ordens ou journals financeiros. API numérica comum aos testes e ao runtime.
- `artifacts/1995_to_objective.patch`: comparação integral fonte-base versus candidata, seguida do include novo; é um diff de revisão, não um instalador. Não deve ser aplicado sobre `1995` para substituir a referência preservada.
- `artifacts/repository_changes.patch`: patch aditivo dos arquivos entregues, sem modificar `1995`.
- `artifacts/symbol_map.tsv`: inventário de funções, inputs e tipos antigos, destino e referências na candidata. `INPUTS_DIFF.md` cobre cada input.

## Alterações estratégicas

VWAP e variância ponderadas pelo volume negociado da sessão: Welford incremental comparado com cálculo independente de duas passagens por lote, agregado por Chan. A comparação usa exatamente os mesmos negócios e instantes; erro expresso em ticks. Não há tick volume nem sigma de pregões anteriores como fallback. B1/B2/B3 são múltiplos uniformes1/2/3 da escala-base0,80WIN/1,50WDO.

Abertura/fim usam a programação publicada pela corretora. Uma única sessão é aceita automaticamente; ambiguidade requer os dois overrides em horário do servidor, contidos na sessão publicada. Intervalos/overnight que o mapeamento diário não suporta são recusados explicitamente. A plataforma não identifica por si só se a sessão publicada inclui leilão: os horários e a convenção do feed precisam ser conferidos no terminal antes de homologação; os overrides permitem recortar a janela regular sem alterar horário de ordens.

READY exige tempo mínimo configurável300s, quantidade/volume válidos, preços distintos, dispersão relativa à grade, cobertura observável e concordância numérica independente. Cinco minutos não comprovam estabilidade estatística. Falhas de fonte, revisão de registros ou lacuna acima do parâmetro mantêm dados indisponíveis até reconstrução/reset/dia/reconexão. A política é conservadora: um silêncio legítimo maior que30s também pode bloquear o dia; esse default é hipótese de engenharia, não calibragem do mercado. Ausência de erro na API não prova completude da bolsa.

Ondas reconhecem reversão somente após60pontosWIN/2WDO, sem retrodatação. A referência de volume é congelada no início da onda com até dez ondas fechadas anteriores; o mínimo experimental é três. A primeira direção e a última tentativa ainda não reconhecida são observadas, sem fabricar esforço ou eficiência.

O caminho negócio a negócio foi refutado como métrica insensível ao feed: bounce de um tick pode mudar a decisão0,60 sem alterar progresso/extremos principais. `grossPath` permanece observacional. A decisão usa caminho de eventos causais de preço de dois ticks, com numerador no mesmo último evento aceito e resíduo registrado separadamente. O parâmetro é explícito e experimental. A invariância foi testada apenas nas transformações documentadas; ruído maior e feeds economicamente diferentes continuam exigindo validação real.

CONT exige esforço, progresso, eficiência e sustentação (recuo menor que um evento de preço); ABS exige tentativa original esforçada/ineficiente, excursão e rejeição posterior positiva. A ineficiência ABS é congelada no último novo extremo da tentativa, antes da reação: rejeitar o preço não reduz artificialmente o numerador para aprovar ABS. Retestes no mesmo extremo não renovam essa evidência; essa escolha conservadora pode deixar absorções de fora. Conflitos permanecem NEUTRO. Classificação é independente da elegibilidade geográfica; não há votação, cor obrigatória de candle ou filtro macro direcional.

No fechamento M1, nova CONT é elegível até B2 inclusiva. Trigger deve ficar estritamente antes da B3 congelada; preço executável em B3 ou além invalida a nova entrada. Margens175WIN/3,5WDO são mantidas. ABS pode ser elegível em B1/B2/B3/além do lado correspondente, sempre dependendo de rejeição comprovada. Igualdade VWAP é classificada se houver tese, mas operacionalmente inelegível nesta política explícita. B3 jamais participa de SL, TP, BE, proteção progressiva ou EOD.

Novas ordens usam `BASE`/`BASE_CONT` como mapeamento de identidade histórica, sem a antiga classificação de votação. O lote fixo usa apenas `Inp_FixedLots`. O cálculo por risco é literalmente preservado. Nenhum parser de `BASE`/`TURBO` foi alterado.

## Integração e cronologia

A coleta ocorre em lotes no timer, depois da recuperação financeira prevista para aquele evento. O caminho de tick executa proteção financeira antes da estratégia e não coleta histórico novo. O timer analítico é de1s; a parte financeira conserva o prazo original de60s no tester e1s ao vivo. O timer pode avaliar uma entrada com o negócio atual efetivamente verificado pelo coletor; a validade do Last e do quote é novamente conferida nos caminhos originais de envio. Isso pode introduzir espera enquanto o coletor alcança o feed; não foi medido atraso real sem MT5/dados.

Snapshots fechados terminam em `fimM1-1ms`, nunca incluem a barra viva. O close de referência deve coincidir com o fechamento M1 da série; divergência registra `M1_TRADE_CLOSE_MISMATCH`, sem preço alternativo. Reconstrução não arma barras anteriores ao attach/reconnect. Acréscimos legítimos no último milissegundo contam uma vez; alterações/remoções/reordenação do prefixo invalidam dados. Um acréscimo que afete fotografia já fechada invalida sua época de evidência, sem alterar retroativamente o snapshot.

Uma única revalidação de tese substitui vetos antigos Weis/direction/glass. Indisponibilidade crítica aguarda sem aprovar; timeout original continua correndo. Invalidação comprovada cancela somente quando não há posição, pedido ou recuperação financeira detendo o ciclo. Hipóteses novas são observadas durante ARMED sem trocar seu trigger nem renovar timeout. Overshoot terminal mantém precedência sobre HOLD_SPREAD, inclusive quando o spread está alto.

FAR mantém flags, identidades, duas metades, pressão posterior e política de ausência de dados. Dois extremos M1 fechados, equivalentes ao default antigo, são coletados exclusivamente para FAR; não condicionam o armamento nem calculam o gatilho. Sem estrutura verificável, FAR é INDETERMINADO, com a política original de não inventar veto/evidência. O diagnóstico favorável usa o trigger real congelado.

## Telemetria e interpretação

O diagnóstico novo tem namespace próprio, sem alterar o CSV financeiro. Registra origem de volume, prontidão/motivos, W/quantidade/sigma/bandas, erro independente em ticks, ondas/tempos de reconhecimento, trajetórias bruta/amostrada, resíduo, rejeição, observações bloqueadas, visitas B1/B2/B3 e tempos/volume por zona. A ocupação é medida entre negócios observados; não equivale a monitoramento contínuo de um feed desconhecido. As visitas usam o mapa causal anterior ao negócio, sem deslocar uma tese já congelada. Sigma pré/pós-READY e variação relativa permitem avaliar instabilidade em dados reais.

Custos p95/p99/máximo usam janela móvel de128 chamadas do serviço; são instrumentação, não garantia de latência. O orçamento suave após uma chamada não pode interromper uma API MT5 síncrona. O diagnóstico de entrada correlaciona sinal, confirmação, pedido e deal. `SEND_ATTEMPT` é registrado retrospectivamente ao retorno do fluxo que realmente chamou a API, identificado como `OBSERVED_AFTER_API_AND_FINANCIAL_COMPLETION`, para não inserir I/O entre a barreira durável e o envio. `DISPATCH_CANDIDATE` é pré-verificação; `DEAL_CONFIRMED` exige deal real. Delays de tese/trigger/quote/fill são proxies claramente nomeados; quote-to-fill não é latência pura da API.

## Defeitos encontrados e corrigidos durante os testes

1. Pedido do snapshot usando a abertura da barra viva, enquanto o motor indexa a barra fechada: corrigido para shift1 e identidade temporal explícita.
2. Rejeição de qualquer crescimento da fronteira same-ms: corrigida para aceitar apenas sufixo com prefixo idêntico, processado uma única vez.
3. Comparação exata do peso real acumulado em ordens diferentes: substituída por tolerância numérica relativa estreita, conservando comparação de média/sigma em ticks e quantidade exata.
4. Overshoot tratado como espera, ou subordinado ao spread: cancelamento terminal restaurado antes de HOLD_SPREAD.
5. Eficiência maior que1 por dividir progresso ainda não amostrado pelo caminho incompleto: numerador e denominador passaram a usar o mesmo evento; resíduo explícito, sem clamp.

## Validação e portões pendentes

Executar `python3 -m unittest discover -s tests -v`. Resultados reais da última execução estão em `artifacts/test-results.txt` e `artifacts/validation.json`. Os testes extraem código real e/ou traduzem sintaxe superficial do módulo para C++ com serviços MT5 simulados, além de comparar código protegido; não são uma réplica Python escolhida para passar.

A compilação nativa permanece NÃO EXECUTADA: MetaEditor e MetaTrader5 não estão instalados. Não há log de zero erros ou warnings nativos. Para compilar, manter o `.mq5` e o diretório `include` juntos em uma área de pesquisa do MetaEditor, com a biblioteca padrão `Trade/Trade.mqh` e `Trade/PositionInfo.mqh`. Compilar sem anexar a uma conta real e preservar log/build do terminal.

Faltam replay tick a tick do mesmo feed real para base/candidata, testes operacionais de reinício/BE/pending/partial/netting/EOD, cobertura de leilão e sessões da corretora, desempenho real, distribuição do instante de READY, variação de sigma e frequência B3 por ativo. Nenhuma taxa de acerto, melhora de rentabilidade ou homologação é alegada. Não executar base e candidata enviando ordens simultaneamente na mesma conta netting.


## Integração posterior — revisão atual

A revisão `codex/remora-1996-integracao`, derivada de54fbc54, acrescenta admissão limitada do fluxo corrente após proteção financeira, recuperação analítica controlada com validação cruzada em barras M1 e entrega única `RemoraScalper_1996_Completo.mq5`. O código financeiro protegido, os65inputs e as regras estratégicas não foram reparametrizados. Detalhes, evidências, diff e pendências estão em `INTEGRACAO_ENTREGA_1.996.md` e `artifacts/integracao_1996/`.

A referência a coleta exclusivamente no timer nas seções anteriores descreve a revisão histórica inicial e é substituída pelo caminho limitado e auditado desta integração. Da mesma forma, o bloqueio antes permanente por silêncio passa a requerer recuperação verificável; falhas sem prova suficiente continuam bloqueadas. As outras restrições e pendências nativas permanecem.


## Correção cirúrgica CONT — 11/11/2026

Base b6961c4, branch `codex/remora-1996-cont-surgical`.
Retirado o veto drawdown/eventStep de OMClassify e OMRevalidate, sem novo
limiar e sem alterar medição, inputs, financeiro ou o controle 1995. Completo
regenerado fielmente. Atualizados os quatro oráculos que esperavam o defeito
e acrescentadas regressões específicas. Diff e provas em
`artifacts/correcao_cont_1996/`. COMPILACAO_NATIVA_NAO_VERIFICADA; NÃO HOMOLOGADO.
