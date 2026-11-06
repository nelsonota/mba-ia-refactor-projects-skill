# Refatoração arquitetural automatizada com Skills

Este repositório demonstra uma skill reutilizável de auditoria e refatoração para MVC, aplicada a três APIs legadas em stacks diferentes. Os relatórios completos, checklists e evidências de execução estão nas pastas `reports/` de cada projeto e também foram consolidados em `reports/` na raiz.

## Análise Manual

Os itens abaixo foram identificados no código original antes da refatoração. Os relatórios por projeto contêm a auditoria completa, evidências, linhas, plano aprovado e rastreabilidade antes/depois.

### Projeto 1 — `code-smells-project` (Python/Flask, API de e-commerce)

Arquitetura inicial: rotas em `app.py`, controllers com fluxo de aplicação, SQL e persistência em `models.py` e inicialização/schema em `database.py`.

- **CRITICAL — SQL arbitrário sem autenticação:** `app.py:47-78` executava SQL enviado pelo cliente, inclusive escrita, permitindo ler ou alterar o banco.
- **CRITICAL — SQL injection:** `models.py:47-50,109-111,126-129,148-166,279-281,289-299` concatenava dados externos em consultas.
- **HIGH — Senhas em texto puro:** `database.py:26-35,75-83` e `models.py:72-131` armazenavam e comparavam senhas sem hash.
- **MEDIUM — Consultas N+1:** `models.py:171-201,203-233` consultava itens e produtos repetidamente ao montar pedidos.
- **MEDIUM — Validação inconsistente:** `controllers.py:24-54,64-93,146-206` tratava payloads e regras de forma desigual.
- **LOW — Identificadores genéricos:** `controllers.py:56` e `models.py:24,43,54,65,89,122` usavam `id` para entidades distintas.
- **LOW — Literais de domínio sem nome:** `models.py:247-262,272` e `controllers.py:52,242` embutiam estados, categorias e faixas de desconto.

### Projeto 2 — `ecommerce-api-legacy` (Node.js/Express, LMS com checkout)

Arquitetura inicial: `AppManager.js` concentrava rotas, checkout, consultas e escrita; utilitários mantinham estado e configuração compartilhados.

- **HIGH — Relatório financeiro administrativo sem autenticação:** `src/AppManager.js:80-129` expunha dados financeiros pela rota admin.
- **HIGH — God class:** `src/AppManager.js:4-139` misturava roteamento, regras do checkout e persistência.
- **MEDIUM — Exclusão sem tratar erro/resultado:** `src/AppManager.js:131-136` podia declarar sucesso sem confirmar a exclusão.
- **MEDIUM — Consultas N+1:** `src/AppManager.js:92-126` buscava usuário e pagamento repetidamente para matrículas.
- **LOW — Identificadores abreviados:** `src/AppManager.js:29-33,37-40,50-57` usava nomes como `u`, `e`, `p` e `cid` em fluxos de domínio.
- **LOW — Estado global e fallback de senha:** `src/utils.js:9-22` e `src/AppManager.js:46,68` mantinham estado mutável e aplicavam senha padrão silenciosa.

### Projeto 3 — `task-manager-api` (Python/Flask, API de tarefas)

Arquitetura inicial: já separava `models/`, `routes/`, `services/` e `utils/`, mas as rotas acumulavam regras, consultas, commits e montagem de respostas.

- **CRITICAL — Hashes de senha expostos:** `models/user.py:16-25` e `routes/user_routes.py:27-40` retornavam hash de senha em rota sem autenticação.
- **HIGH — Segredos no código:** `app.py:11-13` e `services/notification_service.py:7-10,15-19` continham chave de assinatura e credencial SMTP.
- **HIGH — MD5 sem salt:** `models/user.py:27-32` usava hash inadequado para senhas.
- **MEDIUM — Regras e persistência nas rotas:** `routes/task_routes.py:85-223`, `routes/user_routes.py:42-151` e `routes/report_routes.py:12-223` misturavam HTTP, domínio e acesso ao banco.
- **MEDIUM — API UTC obsoleta:** `app.py:24`, modelos, rotas e serviços usavam `datetime.utcnow()`.
- **LOW — Nomes abreviados:** `routes/task_routes.py:16-17,50-55` e `routes/report_routes.py:33,55-61,159-164` usavam abreviações em lógica de domínio.
- **LOW — Literais repetidos:** `routes/task_routes.py:32,73,110,177,286` e `routes/report_routes.py:19-50,120-129` repetiam estados e limites sem centralização.

## Construção da Skill

A skill está em `.agents/skills/refactor-arch/` dentro de cada projeto, usando o formato de skills do Codex. A cópia é a mesma nos três projetos.

`SKILL.md` organiza a execução em três fases sequenciais: análise da stack e arquitetura; auditoria com relatório e pausa para aprovação; refatoração MVC e validação. As referências separam conhecimento de domínio para manter o fluxo principal conciso:

- `references/analise-projeto.md`: heurísticas de linguagem, framework, banco e arquitetura.
- `references/catalogo-antipatterns.md`: sinais de detecção e severidades CRITICAL, HIGH, MEDIUM e LOW, incluindo APIs deprecated e rota administrativa sem autorização.
- `references/template-relatorio.md`: formato do relatório, checklist e rastreabilidade.
- `references/guidelines-mvc.md`: responsabilidades de Models, Views/Routes, Controllers, services, configuração e composição.
- `references/playbook-refatoracao.md`: transformações antes/depois para injeção SQL, credenciais, autenticação administrativa, separação de responsabilidades, validação, consultas, erros, transações e qualidade.

A neutralidade tecnológica vem de instruções orientadas a evidências e responsabilidades, com exemplos específicos tratados como ilustrativos. A skill adapta linguagem, framework, persistência, convenções e comandos ao repositório analisado; não presume que a estrutura existente seja totalmente monolítica nem move código sem avaliar contratos. A Fase 2 exige confirmação antes de alterar código.

## Resultados

| Projeto | Stack detectada | Findings originais | Resultado da Fase 3 | Validação registrada |
|---|---|---:|---|---|
| `code-smells-project` | Python / Flask / SQLite | 15: 2 CRITICAL, 7 HIGH, 4 MEDIUM, 2 LOW | 15 resolvidos; 0 parciais; 0 pendentes | Boot WSGI e 34 verificações de cliente Flask em ambiente temporário |
| `ecommerce-api-legacy` | JavaScript / Node.js / Express / SQLite | 6 confirmados: 2 HIGH, 2 MEDIUM, 2 LOW | Os 6 resolvidos; foi resolvido também um achado MEDIUM de manutenção do driver | Boot e chamadas HTTP em container; `npm audit` final sem vulnerabilidades |
| `task-manager-api` | Python / Flask / SQLite | 9: 1 CRITICAL, 2 HIGH, 4 MEDIUM, 2 LOW | 8 resolvidos; 1 parcial (rotação externa de credenciais antigas não verificada) | Compilação e 30 cenários com Flask test client em container descartável |

### Antes e depois

- **E-commerce Python:** de módulos globais com SQL concatenado, credenciais e responsabilidades misturadas para composição em `src/app.py`, configuração, models, views, controllers, services e middleware; SQL parametrizado e acessos sensíveis protegidos.
- **LMS Node:** de uma classe que reunia aplicação e persistência para `src/app.js`, rotas, controller, service, model, configuração e middlewares; rota financeira protegida e consultas agrupadas.
- **Task Manager:** de rotas parcialmente organizadas que ainda consultavam e gravavam no banco para handlers finos em `src/views/`, coordenação em controllers e regras/persistência em services/models.

### Checklist resumido

Os checklists completos estão em `code-smells-project/reports/checklist.md`, `ecommerce-api-legacy/reports/checklist.md` e `task-manager-api/reports/checklist.md`.

- **Projeto 1:** stack e domínio identificados; 15 achados; estrutura MVC, boot e endpoints verificados. As mudanças de autorização e o encerramento de `/admin/query` estão documentados.
- **Projeto 2:** stack e domínio identificados; 6 findings confirmados; boot e interfaces exercitados. A rota administrativa agora exige Bearer token; mudanças de comportamento estão registradas.
- **Projeto 3:** stack e domínio identificados; 9 achados; MVC e 30 cenários verificados. O achado HIGH de segredo permanece parcial até eventual rotação no provedor externo.

### Execução e comportamento entre stacks

Os relatórios registram comandos, versões, resultados e limitações. A skill foi aplicada a Python/Flask em dois níveis de organização e a JavaScript/Express. No terceiro projeto, preservou-se a estrutura parcial e moveram-se responsabilidades restantes para services/controllers. Nenhum repositório tinha suíte automatizada prévia; as validações foram feitas em ambientes descartáveis e com banco de teste/em memória conforme descrito em cada relatório.

## Como Executar

### Pré-requisitos

- OpenAI Codex configurado para o workspace.
- Python e dependências descritas em cada `requirements.txt` para os projetos Flask.
- Node.js compatível com `ecommerce-api-legacy/package.json` e npm para o projeto Express.

### Invocar a skill

Abra cada diretório de projeto no Codex e invoque `refactor-arch` (por exemplo, `$refactor-arch`). A skill deve ser chamada primeiro para auditoria; revise o relatório e confirme explicitamente antes de autorizar a fase de refatoração.

```text
code-smells-project/
ecommerce-api-legacy/
task-manager-api/
```

Para validar uma execução nova, confira o resumo da Fase 1, os findings e suas linhas na Fase 2, confirme que a skill pausa antes de alterar arquivos, e depois verifique o boot e os endpoints originais conforme o checklist da skill e os checklists em `reports/checklist.md` de cada projeto. Os relatórios desta entrega estão em:

- `reports/audit-project-1.md`
- `reports/audit-project-2.md`
- `reports/audit-project-3.md`

## Pendências e limitações conhecidas

- No `task-manager-api`, valores de chave/credencial foram removidos do código e movidos para configuração ambiental, mas a rotação no provedor externo não foi realizada nem verificada. Por isso, a Fase 3 é registrada como incompleta nesse achado HIGH.
- Não há suíte de testes automatizada permanente nos três projetos. As evidências e os cenários executados estão nos respectivos relatórios; cenários não repetidos após alterações específicas também são apontados lá.
- Os projetos locais contêm a skill e relatórios próprios; os relatórios completos também foram copiados para a pasta `reports/` da raiz conforme o formato solicitado.

