# Integração e entrega1.996 — evidência corrente

Código existente preservado e integrado na branch `codex/remora-1996-integracao`, a partir de54fbc54. `1995` mantém SHA-2562479ed8e5c9189438d787be1e804abbd95f9e1c06e01042e560251e64ef67fc5; o consolidado histórico também permanece intacto.

| Problema | Evidência | Correção realizada | Teste executado | Pendência |
| --- | --- | --- | --- | --- |
| Tick cruza/retrai entre timers | Fixture cruza aos250ms e retrai aos750ms; agenda anterior perde a oportunidade sintética | Admissão causal de cauda atual após proteção, com uma consulta limitada e sem reconstrução por tick | Callback real até `SendOrder`, comparação com callback54fbc preservado | Latência e fills de mercado real não medidos |
| Fluxo maior que orçamento | Mais de256 registros ou cursor atrasado mais de1s | Sem commit parcial, aguarda timer; nenhuma execução por cruzamento passado | Densidade e retração antes do timer; zero tentativas retroativas | Há oportunidades perdidas sob saturação; não se promete eliminar toda espera |
| Silêncio30s bloqueava permanentemente | Gap e histórico temporariamente indisponível reproduzidos | Reconstrução limitada, releitura estável e comparação de volume com barras M1; nova época e bloqueio durante recuperação | Silêncio legítimo, volume ausente/incompatível, mesma-ms, restart controlado | APIs do broker não provam completude de bolsa; dados incompatíveis continuam bloqueados |
| Snapshot/ARMED da época anterior | Nova época com mapa ainda indisponível | Invalidação causal antes da prontidão, respeitando posição/pedido/accounting antes de cancelar | Época durante pedido incerto e sem obrigação financeira | MT5 real/reinícios financeiros não executados |
| CONT cancela em dois ticks | BUY/SELLWIN:10pontos; WDO:1ponto; onda ainda mantém direção | Nenhum limiar alterado; associação entre amostragem e tolerância documentada | Recuo de1tick versus2ticks nas duas direções/ativos | AMBIGUIDADE ESTRATÉGICA PENDENTE: escolher tolerância independente requer decisão explícita |
| Copiar módulo separado era inconveniente | Principal depende do `.mqh` existente | Arquivo único gerado por expansão literal, sem nova implementação | Cada função,65inputs, includes, determinismo e dependência ausente | Compilação MetaEditor ainda pendente |

Os atrasos0ms e750ms dos fixtures são diferenças de relógio sintético definido pelo teste.0ms não significa latência zero da plataforma nem fill. As chamadas de API/IO reais podem bloquear. Métricas de chamadas, esperas, orçamento e custo são mantidas em memória e emitidas no diagnóstico periódico, sem flush por tick.

A recuperação aceita apenas consistência observável: duas cópias idênticas de cada intervalo e volume M1 independente disponível e concordante. Um tick novo não limpa falha; volume de barra faltante ou incompatível mantém bloqueio. Se ambos os serviços do broker omitirem os mesmos negócios, essa ausência pode ser indistinguível. Falhas de fonte, preço/flags inválidos e revisão de prefixo continuam fail-closed.

O arquivo `RemoraScalper_1996_Completo.mq5` preserva os dois includes da biblioteca padrão MT5 e incorpora fielmente as dependências próprias. Os testes originais de sigma, bandasB2/B3, ABS/CONT, conflito, FAR, gatilhos e invariantes continuam executados. Novos testes exercitam o módulo e as funções efetivamente entregues, com serviços MT5 explicitamente simulados.

Separação dos estados: pacote completo e equivalência portátil verificados; compilação nativa `COMPILACAO_NATIVA_NAO_VERIFICADA`; testes MT5 NÃO EXECUTADOS; feed/latência operacional `DADOS_INSUFICIENTES`; tolerância CONT pendente. Candidata NÃO HOMOLOGADA. Nenhuma superioridade estatística ou execução de produção é autorizada por esta entrega.
