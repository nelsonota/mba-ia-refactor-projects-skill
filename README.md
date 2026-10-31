# A) Seção "Análise Manual":
# B) Seção "Construção da Skill":

A skill [refactor-arch](refactor-arch/SKILL.md) orienta a análise de um projeto, a produção de uma auditoria e, após aprovação explícita, sua refatoração para MVC e validação. Ela foi escrita para ser adaptada à stack e às convenções encontradas no projeto analisado.

## Decisões de design

O `SKILL.md` é o ponto de entrada e descreve o fluxo em três fases. Na análise, a skill identifica a stack, o domínio, a arquitetura e os comandos disponíveis. Na auditoria, produz `reports/audit-project.md` na raiz do projeto analisado e pede confirmação antes de modificar outros arquivos. Na refatoração, aplica as mudanças aprovadas e verifica testes, inicialização e interfaces existentes.

O conhecimento mais detalhado foi separado em cinco referências, vinculadas à fase em que são necessárias:

- [Análise de projeto](refactor-arch/references/analise-projeto.md): heurísticas de descoberta e contagem de arquivos efetivamente examinados.
- [Catálogo de anti-patterns](refactor-arch/references/catalogo-antipatterns.md): sinais, evidências e severidades para orientar a auditoria.
- [Template de relatório](refactor-arch/references/template-relatorio.md): formato dos achados, cobertura, limitações e plano de mudanças.
- [Guidelines MVC](refactor-arch/references/guidelines-mvc.md): responsabilidades das camadas e orientações de configuração, erros e inicialização.
- [Playbook de refatoração](refactor-arch/references/playbook-refatoracao.md): transformações ilustrativas antes e depois para os problemas do catálogo.

Essa divisão mantém o fluxo principal conciso e permite consultar os detalhes relevantes em cada etapa. A confirmação entre as fases 2 e 3 dá ao usuário a oportunidade de avaliar o relatório e o escopo antes da refatoração.

O checklist em `reports/checklist.md` mantém somente os itens definidos no template; evidências e bloqueios adicionais ficam em texto separado. Cada fase só é declarada concluída quando seus itens aplicáveis estão comprovados. Se o usuário exigir Docker e o daemon estiver inacessível, a skill deve registrar o bloqueio e não afirmar que boot ou endpoints foram validados. Mudanças no contrato de endpoints precisam de aprovação específica.

## Anti-patterns incluídos

O catálogo cobre segurança, separação de responsabilidades, manutenção, desempenho e legibilidade. A severidade indicada é típica: a classificação final depende da evidência e do impacto no projeto.

| Anti-pattern | Severidade típica | Motivo da inclusão |
|---|---|---|
| Credenciais hardcoded | CRITICAL | Pode expor acesso a dados e serviços sensíveis. |
| SQL injection | CRITICAL | Entrada não confiável em consultas pode comprometer dados. |
| God Class ou arquivo monolítico | CRITICAL ou HIGH | A concentração de roteamento, regras e persistência compromete a separação de responsabilidades. |
| Controller pesado | HIGH | Regras de negócio presas ao tratamento da interface dificultam manutenção e testes. |
| Acoplamento rígido | HIGH | Dependências concretas criadas dentro do fluxo dificultam substituição e testes. |
| Estado global mutável | HIGH quando amplamente compartilhado | Pode causar interferência entre requisições ou módulos. |
| Duplicação de regras | MEDIUM | Cópias de regras podem divergir durante a manutenção. |
| Consultas N+1 | MEDIUM | Consultas repetidas por item podem degradar o desempenho. |
| Validação ausente na fronteira | MEDIUM | Entradas inválidas podem chegar a operações que exigem restrições. |
| Tratamento de erros disperso | MEDIUM | Pode produzir respostas inconsistentes ou expor detalhes internos. |
| API deprecated | MEDIUM por padrão | APIs obsoletas podem dificultar atualizações; o substituto deve ser confirmado para a versão instalada. |
| Nomes ambíguos ou números mágicos | LOW | Dificultam a compreensão de nomes e regras de domínio. |

Os sinais do catálogo são pontos de investigação, não provas automáticas. Cada achado deve ter evidência e localização; suspeitas não comprovadas são apresentadas separadamente.

## Independência de tecnologia

A análise combina manifests, arquivos de configuração, imports, código de inicialização e testes para identificar a stack em vez de presumir uma linguagem ou framework. As guidelines descrevem responsabilidades MVC e admitem os mecanismos e nomes nativos do framework. O playbook usa pseudocódigo ilustrativo, que deve ser adaptado à sintaxe, às APIs e às transações da aplicação.

Para APIs deprecated, a skill exige consultar a documentação oficial correspondente à versão instalada antes de afirmar a obsolescência ou recomendar uma substituição. A validação prevê endpoints HTTP e, quando eles não existem, a interface equivalente, como CLI, eventos ou interface gráfica. Essas escolhas favorecem a adaptação a diferentes tecnologias, mas não comprovam compatibilidade com todas as stacks.

## Desafios e limitações

- **Equilibrar padronização e convenções existentes:** as responsabilidades MVC são obrigatórias como orientação, mas a estrutura concreta pode seguir o framework, evitando exigir diretórios ou camadas artificiais.
- **Produzir achados confiáveis:** o relatório exige arquivo, linhas e evidência, distingue suspeitas de problemas confirmados e não inventa achados para atingir o mínimo desejado de cinco.
- **Preservar comportamento durante mudanças:** a skill estabelece uma linha de base quando possível, pede aprovação antes da refatoração e orienta comparar testes, inicialização e interfaces originais após as alterações.
- **Validar sem ambiente completo:** quando dependências, serviços ou dados de teste impedem boot ou verificação de interfaces, a skill deve registrar o bloqueio e marcar a validação como incompleta.
- **Verificar a própria skill:** foram conferidos os links das cinco referências, as 12 entradas do catálogo, as quatro severidades e as 12 transformações. O validador oficial foi executado, mas não iniciou porque o Python disponível não tinha `PyYAML`; a skill ainda não foi validada em projetos reais.

## Executado
codex -m gpt-6-luna -c 'model_reasoning_effort="low"' "Execute .agents/skills/refactor-arch"

# C) Seção "Resultados":