# Entrega 1.996 — fontes e dependências

Verificação de empacotamento em 10/11/2026. Os fontes e os relatórios já existiam; nenhuma função foi reescrita nesta etapa. O pacote é disponibilizado na branch de desenvolvimento `codex/remora-matriz-objetiva` de `baalfoonseca-code/Bf`. O arquivo original `1995` e a branch `main` são preservados.

## Arquivos necessários à compilação

| Arquivo próprio | Bytes | Linhas | SHA-256 |
| --- | ---: | ---: | --- |
| `RemoraScalper_MatrizObjetiva.mq5` | 303697 | 7139 | `8ab7d8b0476264ccfe37fddf43a4fb87c0967676dfb57648160e2f3b54aec2d9` |
| `include/ObjectiveMatrix.mqh` | 37384 | 799 | `9bd44f13e61845be3c490a802035667da5ff0cb491f9b5a6bb127722b09a1b08` |

O principal inclui `"include/ObjectiveMatrix.mqh"` relativamente ao próprio arquivo. O módulo contém a implementação da matriz, não um arquivo vazio ou um placeholder: cálculo ponderado, ondas, classificação, coletor, snapshots, telemetria e revalidação. Não inclui outros arquivos próprios.

O principal também inclui `<Trade\Trade.mqh>` e `<Trade\PositionInfo.mqh>`. Esses arquivos e suas dependências transitivas pertencem à biblioteca padrão instalada com MetaTrader 5/MetaEditor, sob `MQL5/Include`. Não devem ser substituídos por stubs dos testes.

Não foram identificadas outras dependências locais de código, DLLs importadas, indicadores externos via `iCustom` ou serviços via `WebRequest`. A compilação não exige os relatórios, os scripts Python ou os diffs.

## Organização no MetaEditor

Copiar os dois fontes mantendo esta estrutura dentro da pasta de dados do terminal:

```text
MQL5/
  Experts/
    RemoraScalper_1996/
      RemoraScalper_MatrizObjetiva.mq5
      include/
        ObjectiveMatrix.mqh
  Include/
    Trade/
      Trade.mqh                 # biblioteca padrão do terminal
      PositionInfo.mqh          # biblioteca padrão do terminal
```

Abrir `RemoraScalper_MatrizObjetiva.mq5` no MetaEditor e compilar com F7. Não é necessário adicionar o `.mqh` como um programa separado. O `.ex5` deverá ser gerado pelo compilador; nenhum `.ex5` foi fornecido ou certificado nesta entrega.

## Relatórios e verificações

Produzidos e incluídos: `AUDITORIA_PREVIA.md`, `REGRESSION_FINANCE.md`, `INPUTS_DIFF.md`, `TEST_CASES.md` e `CHANGELOG_CIRURGICO.md`. O changelog descreve a primeira entrega local; a observação histórica de que ainda não havia push corresponde àquela etapa. Esta publicação posterior apenas empacota e disponibiliza os mesmos fontes.

Os testes portáteis em `tests/` usam Python 3 e g++ com C++17, sem pacotes Python externos. Esses programas não são dependências do EA no terminal. Os 61 testes aprovados da implementação estão registrados em `artifacts/test-results.txt`; não foram apresentados como compilação MQL5 ou replay financeiro.

`artifacts/1995_to_objective.patch` é a comparação de revisão entre base e candidata. `artifacts/repository_changes.patch` representa os acréscimos da primeira entrega; este documento e o registro de empacotamento posteriores constam diretamente no commit de publicação. `artifacts/entrega_1.996.json` registra os hashes desta conferência. O ZIP contém os fontes, a referência original, os relatórios, os testes e os artefatos de revisão.

## Estado da compilação

**COMPILACAO_NATIVA_NAO_VERIFICADA — compilação nativa pendente.** MetaEditor/MetaTrader 5 não foram encontrados neste ambiente Linux. Portanto, não há quantidade real de erros ou avisos nativos para informar; não se declara zero. A estrutura e as dependências próprias foram conferidas, mas a aceitação pelo compilador só poderá ser confirmada no MetaEditor.

A candidata permanece **NÃO HOMOLOGADA**. A execução e os testes operacionais dependem do terminal, das especificações de contrato/sessão da corretora e de dados reais adequados de WIN/WDO. Esses requisitos de execução não implicam credenciais adicionais para compilar.


## Revisão de integração — escopo posterior à entrega publicada

HEAD de partida conferido: `54fbc544a6dfdf190f010de18ff0d61099c00fb5`, na branch `codex/remora-matriz-objetiva`. O diff desde `9ebc9eedd2243c44601efd9dfb125bc4fcacb55e` acrescentava apenas `RemoraScalper_1996_CONSOLIDADO.mq5`, com a expansão literal do módulo e dois comentários. Esse arquivo histórico permanece intocado. A integração atual usa a branch própria `codex/remora-1996-integracao` e o comando `Comando_Codex_Remora_1996_Integracao_Entrega.md` fornecido pelo usuário.

As seções anteriores registram a primeira entrega. A evidência corrente desta revisão fica em `artifacts/integracao_1996/`; os resultados e ZIPs anteriores foram preservados como históricos, sem sobrescrita.

### Entrega corrente consolidada e modular

Para copiar o código inteiro ao MetaEditor, use **`RemoraScalper_1996_Completo.mq5`**. Ele tem 349987 bytes e SHA-256 `233e00531e8d8106e4bb9439e5409bad55b5cac2c1129e6947d54c48a154ced6`. A incorporação é literal: os testes verificam todos os corpos, inputs e ausência de duplicação. O arquivo requer apenas os includes padrão `Trade\Trade.mqh` e `Trade\PositionInfo.mqh` do MetaTrader5, com suas dependências padrão.

A alternativa modular continua `RemoraScalper_MatrizObjetiva.mq5` e `include/ObjectiveMatrix.mqh`, preservando a pasta relativa. Hashes desta revisão: principal `f192f610bbc01cdd0275bd8980f9439ef654287ebdc52747abd641f98f57efd8`; módulo `47993d4e9d501b43bb84afb6383a33a35cd7d2c663439f6e62a5f76761c66bc4`. Os hashes da tabela anterior correspondem à entrega histórica inicial.

Builder auditável: `python3 tools/build_consolidated.py`; conferência sem escrever: `python3 tools/build_consolidated.py --check`. A geração não altera os fontes nem o controle `1995`. Testes portáteis: Python3 e g++C++17, biblioteca padrão, sem pacotes Python externos. O fixture histórico do callback está incluído; os testes não exigem acesso GitHub para consultar a revisão passada.

Pacote corrente: `artifacts/remora_1996_integracao_completa.zip`. Ele contém a versão única, os fontes modulares da mesma revisão, dependências próprias, testes/fixtures, builder, comando, diff, relatórios e hashes. O consolidado histórico `RemoraScalper_1996_CONSOLIDADO.mq5` não é usado como fonte da entrega nova nem misturado ao ZIP.

No terminal, coloque o `.mq5` consolidado em uma pasta de pesquisa de `MQL5/Experts`, abra e compile com F7. Para a versão modular, mantenha a subpasta `include` ao lado do principal. Não executar simultaneamente as duas apresentações do mesmo EA. Nenhum `.ex5` foi certificado; compilação nativa permanece pendente e a candidata NÃO HOMOLOGADA.
