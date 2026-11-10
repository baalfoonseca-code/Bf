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
