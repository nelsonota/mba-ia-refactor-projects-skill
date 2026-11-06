# Formato da análise e do relatório

Apresente os dois blocos abaixo ao usuário, substituindo os marcadores por dados do projeto. Os nomes de campos e títulos são fixos; o conteúdo descritivo pode ser em português. Valores do exemplo do usuário são ilustrativos, não fatos presumidos.

## Fase 1: análise

```text
================================ PHASE 1: PROJECT ANALYSIS ================================
Language:      <linguagens e versões confirmadas>
Framework:     <frameworks e versões confirmadas>
Dependencies:  <dependências relevantes identificadas>
Domain:        <domínio e funcionalidades identificados>
Architecture:  <arquitetura atual e organização>
Source files:  <quantidade de arquivos efetivamente analisados>
DB tables:     <tabelas identificadas; ou não aplicável / não verificado>
===========================================================================================
```

Informe também cobertura, exclusões e método de contagem; indique o que não foi possível verificar. Não confunda dependência declarada com uso confirmado.

## Fase 2: relatório

Grave o relatório completo em `reports/audit-project.md` na raiz do projeto analisado e apresente-o ao usuário neste formato. Use apenas evidências verificadas; nunca reproduza valores de segredos.

```text
================================ ARCHITECTURE AUDIT REPORT ================================
Project: <nome do projeto>
Stack:   <linguagens e frameworks confirmados>
Files:   <quantidade analisada> analyzed | <linhas de código analisadas, se contadas>

## Summary
CRITICAL: <n> | HIGH: <n> | MEDIUM: <n> | LOW: <n>

## Findings

### [<SEVERIDADE>] <título>
File: <caminho relativo>:<linha ou intervalo exato>
Description: <problema e evidência verificada>
Impact: <consequência concreta e justificativa da severidade>
Recommendation: <correção proposta e compatibilidade necessária>

<repita o bloco para cada achado>

================================ Total: <n> findings ================================
```

Ordene CRITICAL → HIGH → MEDIUM → LOW. Os números do resumo e total devem corresponder aos achados efetivos. Inclua todos os locais necessários para demonstrar cada problema; para API deprecated, informe versão, fonte oficial e substituto confirmado. Se as linhas de código não forem contadas, indique “não medido”.

Complemente o relatório com cobertura e método de contagem, exclusões, linha de base (comandos e resultados de testes, boot e interfaces), limitações, suspeitas não comprovadas e plano de refatoração relacionado aos achados. Informe o total real; se houver menos de cinco, explique sem inventar ou desdobrar artificialmente.

Depois de apresentar o relatório e plano, se os itens aplicáveis da Fase 2 estiverem verificados, pergunte no chat:

**Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]**

Se houver item aplicável ainda não verificado, não use “Phase 2 complete”: explique a pendência e solicite a ação necessária para resolvê-la. Em qualquer caso, aguarde confirmação afirmativa explícita antes de modificar outros arquivos do projeto.

## Fase 3: conclusão da refatoração

Apresente este bloco de conclusão somente depois de implementar e verificar todos os itens aplicáveis e corrigir os achados aprovados:

```text
================================ PHASE 3: REFACTORING COMPLETE ================================
## New Project Structure
<árvore real dos diretórios e arquivos relevantes, identificando o entry point>

## Validation
<✓ / ✗ / não verificado> Application boots without errors
<✓ / ✗ / não verificado> All original endpoints respond correctly
<✓ / ✗ / não verificado> All identified anti-patterns resolved
===============================================================================================
```

A árvore deve refletir o projeto resultante e mostrar a estrutura `src/` exigida pelas guidelines, identificando config, models, views, controllers, middlewares e composition root. Adapte a linha de endpoints à interface equivalente quando não houver HTTP. Use ✓ apenas para resultado efetivamente comprovado; use ✗ para falha e “não verificado” quando não houver evidência suficiente. Não declare que todos os anti-patterns foram eliminados sem verificar todos os achados identificados; informe correções pendentes e limitações. Se boot ou interfaces não puderem ser verificados, indique que a validação está incompleta. Abaixo do bloco, registre comandos e resultados, relação entre achados e correções e riscos restantes.

Se um bloqueio impeditivo persistir após alternativas seguras e todo o trabalho independente tiver sido concluído, substitua o título por `PHASE 3: REFACTORING BLOCKED`. Apresente a estrutura e os resultados reais, identifique os itens pendentes, tentativas, causa e ação concreta necessária para retomar. Não use `COMPLETE` nem declare sucesso nessa situação.

## Checklist de validação

Crie `reports/checklist.md` na raiz do projeto com os itens abaixo. Na Fase 2, registre os resultados disponíveis das fases 1 e 2 e deixe os itens da Fase 3 pendentes; atualize após a confirmação e durante a validação da Fase 3. Marque `[x]` somente quando houver evidência suficiente. Para item pendente, falho, não aplicável ou não verificado, mantenha `[ ]` e acrescente uma breve explicação do estado e da evidência ou limitação. Se houver menos de cinco achados reais, não invente problemas: mantenha o item correspondente desmarcado e explique. Para aplicações sem HTTP, mantenha o item de endpoints como não aplicável e documente a verificação da interface equivalente.

O checklist é fechado: mantenha exatamente as caixas e a ordem do modelo, sem adicionar, remover, renomear ou duplicar itens. Use seções separadas de texto sem caixas para linha de base, evidências, achados corrigidos, comandos, bloqueios e verificações adicionais. Não marque boot ou endpoints com base em análise estática, configuração de Compose ou build. Compare respostas e efeitos com a linha de base; alteração intencional de contrato, mesmo aprovada, deve ser registrada e não comprova que o contrato original foi preservado.

```markdown
## Checklist de Validação

### Fase 1 — Análise
- [ ] Linguagem detectada corretamente
- [ ] Framework detectado corretamente
- [ ] Domínio da aplicação descrito corretamente
- [ ] Número de arquivos analisados condiz com a realidade

### Fase 2 — Auditoria
- [ ] Relatório segue o template definido nos arquivos de referência
- [ ] Cada finding tem arquivo e linhas exatos
- [ ] Findings ordenados por severidade (CRITICAL → LOW)
- [ ] Mínimo de 5 findings identificados
- [ ] Detecção de APIs deprecated incluída (se aplicável)
- [ ] Skill pausa e pede confirmação antes da Fase 3

### Fase 3 — Refatoração
- [ ] Estrutura de diretórios segue padrão MVC
- [ ] Configuração extraída para módulo de config (sem hardcoded)
- [ ] Models criados para abstrair dados
- [ ] Views/Routes separadas para visualização ou roteamento
- [ ] Controllers concentram o fluxo da aplicação
- [ ] Error handling centralizado
- [ ] Entry point claro
- [ ] Aplicação inicia sem erros
- [ ] Endpoints originais respondem corretamente
```

O item da pausa só pode ser marcado após a pausa e o pedido de confirmação terem ocorrido. Não trate um item não aplicável como validado nem afirme conclusão quando os testes necessários estiverem bloqueados.

Para APIs deprecated, consulte as fontes oficiais pertinentes à versão efetivamente identificada. A ausência de API obsoleta pode ser registrada após a verificação; falta de acesso à documentação ou versão desconhecida é “não verificado”, não “não aplicável”. Para a conclusão de cada fase, reconcilie cada item aplicável com evidência; pendências verificáveis impedem a declaração de conclusão. Se a execução em Docker for obrigatória e o daemon estiver inacessível após diagnóstico e alternativas autorizadas, registre o bloqueio e não marque boot nem endpoints.

Itens aplicáveis e pendentes exigem continuidade do trabalho após a aprovação, salvo bloqueio impeditivo real. O mínimo de cinco findings não exige inventar achados quando existirem menos; itens não aplicáveis e esse mínimo não atingido devem ser explicados e não impedem, por si só, a conclusão. Achados fora do escopo aprovado devem ser registrados como pendentes e não apresentados como corrigidos.
