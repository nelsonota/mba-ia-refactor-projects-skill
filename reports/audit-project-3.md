# ARCHITECTURE AUDIT REPORT

Project: task-manager-api  
Stack: Python 3.13.14; Flask 3.0.0; Flask-SQLAlchemy 3.1.1; SQLAlchemy 2.1.6 (resolvido em ambiente temporário isolado)  
Files: 15 analyzed | linhas de código: não medido

## Summary
CRITICAL: 0 | HIGH: 3 | MEDIUM: 3 | LOW: 0

## Findings

### [HIGH] Hash de senha retornado nas respostas da API
File: models/user.py:16-25
Description: `User.to_dict()` inclui o campo `password` no dicionário serializado. A função é usada em respostas de criação, atualização, consulta e login em `routes/user_routes.py:32-34`, `85-86`, `128-129` e `208-210`.
Impact: clientes recebem o hash armazenado de cada senha, permitindo ataques offline e exposição de credencial derivada.
Recommendation: remover o campo password da serializacao publica e declarar explicitamente os campos expostos, preservando os outros campos.
Status: corrigido apos aprovacao explicita; o campo password foi removido dos corpos JSON de usuario e login.

### [HIGH] Senhas armazenadas com MD5
File: models/user.py:27-32
Description: `set_password` e `check_password` usam MD5 sem salt e comparação direta do digest.
Impact: MD5 é inadequado para armazenamento de senhas e permite tentativa offline rápida caso os hashes sejam obtidos.
Recommendation: migrar para hash de senha adaptativo com salt (por exemplo, Werkzeug `generate_password_hash`/`check_password_hash` ou biblioteca equivalente), planejando compatibilidade com hashes existentes.

### [HIGH] Rotas concentram validação, regras de domínio, persistência e apresentação
File: routes/task_routes.py:86-154
Description: `create_task` lê e valida o corpo HTTP, verifica relações, converte data, instancia e persiste o model, trata falhas e monta a resposta. Padrão semelhante ocorre nos fluxos de atualização e nos relatórios em `routes/report_routes.py:13-102`.
Impact: mudanças de regra ficam acopladas ao Flask e ao acesso SQLAlchemy; aumenta o custo de teste e o risco de divergência entre operações.
Recommendation: separar a camada de rotas/views, controllers de coordenação e casos de uso/modelos, mantendo os contratos HTTP.

### [MEDIUM] Consultas repetidas por registro (N+1)
File: routes/task_routes.py:14-16,41-52; routes/report_routes.py:53-60,158-164; routes/user_routes.py:12-23
Description: listagens consultam usuários e categorias dentro do loop de tarefas; o resumo executa uma consulta de tarefas por usuário; categorias contam tarefas uma a uma. A listagem de usuários também acessa `u.tasks` dentro do loop.
Impact: o número de consultas cresce com o número de registros, elevando latência e carga no banco.
Recommendation: usar eager loading, joins ou agregações em lote e medir a quantidade de consultas preservando campos e ordenação atuais.

### [MEDIUM] Uso de `Query.get()` obsoleto no SQLAlchemy resolvido
File: routes/task_routes.py:42,51,67,117,122,158,188,195,227; routes/user_routes.py:29,94,136,155; routes/report_routes.py:105,192,213
Description: a instalação temporária isolada, resolvida a partir de `requirements.txt`, identificou SQLAlchemy 2.1.6; o projeto usa `Model.query.get()` nos pontos listados. A documentação oficial classifica `Query.get()` como API legada desde SQLAlchemy 2.0 e indica `Session.get()` como substituto: [SQLAlchemy 2.0 Legacy Query API](https://docs.sqlalchemy.org/en/20/orm/queryguide/query.html) e [guia oficial de migração](https://docs.sqlalchemy.org/en/20/changelog/migration_20.html).
Impact: uso de API legada dificulta evolução e pode gerar avisos ou incompatibilidades em futuras versões.
Recommendation: substituir por `db.session.get(Model, id)` mantendo o mesmo comportamento de busca por chave primária e o tratamento atual de ausência.

### [MEDIUM] Prioridade de entrada sem validação de tipo na fronteira
File: routes/task_routes.py:103-114
Description: o valor JSON `priority` é comparado numericamente sem validar/converter seu tipo. Valores como texto ou objeto podem gerar `TypeError` não tratado nessa etapa, resultando em erro 500 em vez da resposta 400 usada para prioridade fora da faixa.
Impact: entrada malformada produz resposta de erro inesperada e pode afetar a disponibilidade do endpoint.
Recommendation: validar tipo e faixa antes da comparação e preservar a resposta 400 para entrada inválida, cobrindo também o fluxo de atualização.

================================ Total: 6 findings ================================

## PHASE 1: PROJECT ANALYSIS

```text
================================ PHASE 1: PROJECT ANALYSIS ================================
Language:      Python 3.13.14
Framework:     Flask 3.0.0; Flask-SQLAlchemy 3.1.1; SQLAlchemy 2.1.6 resolvido isoladamente
Dependencies:  Flask-CORS 4.0.0; Marshmallow 3.20.1 (declarado, uso não confirmado); Requests 2.31.0 (declarado, uso não confirmado); python-dotenv 1.0.0 (declarado, uso não confirmado)
Domain:        Gerenciamento de tarefas, usuários, categorias, login e relatórios
Architecture:  Flask app.py como entry point; blueprints em routes/, modelos SQLAlchemy em models/, serviço de notificação e utilitários. Separação parcial; rotas contêm regras e persistência.
Source files:  15 caminhos de produto lidos; 17 arquivos elegíveis no inventário
DB tables:     users, tasks, categories (models/user.py:6; models/task.py:6; models/category.py:5)
===========================================================================================
```

### Cobertura, método e limitações

- Inventário: `rg --files` encontrou 17 arquivos de produto `.py`, `.md` e `.txt`, excluindo `.agents/skills`; 15 arquivos únicos foram lidos integralmente (código, README e dependências). Dois `__init__.py` vazios não foram lidos. Dependências instaladas, binários e artefatos gerados foram excluídos da leitura detalhada.
- O código usa SQLite (`app.py:11`) e cria tabelas em `app.py:30-31`. Não foi encontrado arquivo de teste no inventário. O README documenta `python seed.py` e `python app.py`; `seed.py` apaga e repovoa tabelas, portanto não foi executado.
- Python local: 3.13.14. Dependências não estavam instaladas no ambiente original. Foram resolvidas em `$env:TEMP\task-manager-api-audit-deps` a partir de `requirements.txt` para inspecionar versões: Flask 3.0.0, Flask-SQLAlchemy 3.1.1, SQLAlchemy 2.1.6, Flask-CORS 4.0.0, Marshmallow 3.20.1, Requests 2.31.0 e python-dotenv 1.0.0. SQLAlchemy 2.1.6 é versão do ambiente temporário, não do ambiente original.
- Linha de base registrada posteriormente em copia isolada; durante a Fase 1 o Docker daemon negou acesso. O seed nao foi executado por apagar dados. Na copia, a aplicacao original iniciou e as rotas foram exercitadas sem tocar no banco do projeto.
- Suspeita não comprovada: `services/notification_service.py:7-10` contém credenciais SMTP fixas e o método usa essas variáveis em `:15-19`, mas não foi possível confirmar se são credenciais reais ou valores demonstrativos; não classificado como finding confirmado. `app.py:13` contém chave fixa, cujo uso e contexto de deployment não foram comprovados.
- Não foram encontrados usos de `Query.get()` além dos locais documentados, e a versão temporária identificada foi confrontada com a documentação oficial SQLAlchemy 2.0. A lista de ocorrências é do inventário completo do projeto.

## Plano de refatoração proposto

Após aprovação explícita: criar `src/config/settings.py`, `src/models/`, `src/views/routes.py`, `src/controllers/`, `src/middlewares/error_handler.py` e `src/app.py` como composition root, adaptando o carregamento existente e preservando rotas/status/respostas; remover hashes da serialização e substituir MD5 com estratégia de compatibilidade; mover fluxos de tarefa e relatório para controllers/casos de uso; otimizar consultas em lote; atualizar `Query.get()`; validar tipos de entrada. O tratamento das credenciais suspeitas requer primeiro determinar se são reais; qualquer alteração de contrato será apresentada separadamente antes de ser feita.

## PHASE 2: AUDIT CHECKLIST STATUS

The Phase 2 pause was presented, and explicit approval for Phase 3 was received before changes began.

## PHASE 3: REFACTORING COMPLETE

A autorização foi recebida. A estrutura criada está em `src/config/settings.py`, `src/database.py`, `src/models/`, `src/views/routes.py`, `src/views/serializers.py`, `src/controllers/`, `src/middlewares/error_handler.py` e `src/app.py`. Os pontos de entrada e imports anteriores continuam disponíveis como adaptadores (`app.py`, `database.py`, `models/` e `routes/`).

Correções aplicadas: `Query.get()` substituído por `db.session.get()`; carregamento relacionado com `joinedload`/`selectinload` e agregações em lote; prioridade inválida validada como HTTP 400; configuração de banco, chave de sessão e SMTP centralizada em variáveis de ambiente; erros não tratados centralizados preservando respostas HTTPException e a página padrão 500; serialização movida para `src/views/serializers.py`; novas senhas usam hash adaptativo e hashes MD5 legados são migrados após login válido.

Validação isolada: 25 cenários de rotas foram executados contra cópias separadas da linha de base e da refatoração. Status iguais nos fluxos válidos; prioridade malformada passou de 500 para 400. Um servidor iniciado em cópia temporária respondeu 200 em `/`, `/health` e `/tasks`. Nenhum banco real foi acessado. O seed destrutivo não foi executado. Docker não foi usado porque o daemon negou acesso.

Remaining risk: previously persisted MD5 hashes are upgraded individually after successful login. Accounts without successful login retain the legacy hash until then. No project database file was present or modified.



================================ PHASE 3: REFACTORING COMPLETE ================================
## New Project Structure
src/
  config/settings.py
  database.py
  models/
    user.py
    task.py
    category.py
  views/
    routes.py
    serializers.py
  controllers/
    user_controller.py
    task_controller.py
    report_controller.py
  middlewares/error_handler.py
  app.py  (composition root; create_app)
Legacy adapters remain at app.py, database.py, models/, and routes/.

## Validation
✓ Application boots without errors (isolated copy; HTTP server smoke checked)
✓ All original endpoints respond correctly (25 scenarios; approved response changes documented)
✓ All identified anti-patterns resolved in source; existing MD5 accounts upgrade on successful login
===============================================================================================

Approved contract changes: user JSON responses no longer include password hashes; malformed task priority now returns 400 instead of the previous 500. Both changes are recorded in reports/checklist.md. The seed was not run, and no real database was modified.

