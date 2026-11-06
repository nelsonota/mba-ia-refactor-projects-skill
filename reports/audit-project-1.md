# ARCHITECTURE AUDIT REPORT

Project: code-smells-project  
Stack: Python 3.13.14 (runtime de validação); Flask 3.1.1 e Flask-CORS 5.0.1 resolvidos em ambiente isolado.  
Files: 6 analyzed | linhas analisadas: não medido

## Summary

CRITICAL: 2 | HIGH: 7 | MEDIUM: 4 | LOW: 2

## Findings

### [CRITICAL] SQL arbitrário exposto sem autenticação
File: `app.py:47-78`
Description: `POST /admin/query` aceita `sql` do cliente e o executa diretamente na conexão SQLite, incluindo comandos de escrita; nenhuma autenticação ou autorização está vinculada à rota.
Impact: Um cliente remoto pode ler, alterar ou apagar dados da loja. A exposição inclui dados de usuários e pedidos e permite alterações persistentes.
Recommendation: Remover a execução arbitrária e substituir por operações explícitas autorizadas. Isso muda o contrato/comportamento da rota; qualquer substituição precisa de aprovação específica antes da implementação, além da confirmação geral da Fase 3.

### [CRITICAL] SQL injection nos fluxos de dados
File: `models.py:47-50, 109-111, 126-129, 148-166, 279-281, 289-299`
Description: Valores recebidos externamente são concatenados em instruções SQL e executados. A cadeia alcança criação/atualização de produtos e usuários, login, criação/status de pedidos e busca de produtos.
Impact: Um atacante pode alterar o significado de consultas e comprometer confidencialidade e integridade do banco. `app.py:59-76` também permite injeção direta pela rota administrativa.
Recommendation: Substituir concatenação por parâmetros SQLite em todas as consultas. Preservar formatos de resposta e efeitos legítimos; testar entradas de aspas e payloads de injeção.

### [HIGH] Operações administrativas e dados sensíveis sem controle de acesso
File: `app.py:47-78`; `controllers.py:128-144, 222-235, 257-262`
Description: Reset e execução de SQL estão públicos; listagem de todos os usuários, pedidos de todos os clientes e relatório de vendas também não aplicam autorização. A listagem de usuários serializa `senha` (`models.py:72-87`).
Impact: Qualquer cliente pode destruir dados, consultar informações pessoais e dados comerciais. Não há identidade autenticada nem verificação de papel.
Recommendation: Aplicar autenticação e autorização fail-closed às rotas administrativas e aos dados restritos; remover campos de senha das respostas. Essa mudança altera o acesso público existente e deve ser declarada no plano de mudança e validada com chamadas anônimas, inválidas e identidade autorizada.

### [HIGH] Senhas armazenadas em texto puro
File: `database.py:26-35, 75-83`; `models.py:72-103, 105-120, 122-131`
Description: A coluna `senha` guarda texto de senha; os registros de exemplo também são inseridos literalmente. Login compara a senha recebida diretamente com o valor persistido.
Impact: Vazamento ou leitura do banco expõe credenciais reutilizáveis em claro. O risco é agravado pelos endpoints de leitura de usuários sem autorização.
Recommendation: Adotar hash de senha com algoritmo apropriado, caminho de verificação compatível e migração controlada dos registros existentes; planejar compatibilidade do login e não expor a senha em respostas.

### [HIGH] Controller concentra regras de negócio, persistência e efeitos
File: `controllers.py:24-58, 64-96, 188-220, 237-255, 264-292`
Description: Os handlers validam domínio e categorias/status, decidem erros, coordenam pedidos e estoque, imprimem notificações e `health_check` abre conexão/consulta diretamente. Assim, controllers não se limitam à coordenação da interface.
Impact: Regras espalhadas dificultam testes isolados e alterações consistentes; efeitos e acesso a dados ficam acoplados ao ciclo HTTP.
Recommendation: Manter rotas para entrada/serialização, controllers finos e extrair casos de uso/regras para services/models/repositórios; centralizar erros e composição de dependências.

### [HIGH] Operações de escrita de produtos sem autenticação
File: `app.py:11-16`
Description: `POST /produtos`, `PUT /produtos/<id>` e `DELETE /produtos/<id>` eram rotas públicas, sem middleware de identidade ou permissão.
Impact: Qualquer cliente podia adulterar o catálogo ou apagar produtos, afetando dados e operações comerciais.
Recommendation: Exigir autorização administrativa fail-closed nessas operações. O acesso público foi alterado para exigir token configurado externamente.

### [HIGH] Chave de assinatura fixa e exposta pela verificação de saúde
File: `app.py:7`; `controllers.py:285-289`
Description: A aplicação configurava uma chave constante para Flask e a incluía na resposta de `/health`.
Impact: A chave ficava disponível a qualquer cliente e poderia permitir a falsificação de cookies assinados se sessões fossem usadas.
Recommendation: Remover o literal, aceitar segredo do ambiente (ou chave efêmera segura) e nunca incluir segredo em respostas.

### [HIGH] Modo debug ativo por padrão em interface de rede pública
File: `app.py:8, 88`
Description: `DEBUG` era fixado em `True` e o servidor iniciava com debug ligado em `0.0.0.0`.
Impact: A interface de depuração e comportamento de desenvolvimento ficam expostos fora da máquina local, aumentando o risco de execução/inspeção indevida e vazamento de detalhes.
Recommendation: Desabilitar debug por padrão, habilitá-lo apenas por configuração explícita de desenvolvimento e não usar o servidor de desenvolvimento em produção.

### [HIGH] Pedidos podiam ser criados e consultados como outro usuário
File: `controllers.py:188-203, 222-225`; `app.py:23-26`
Description: `POST /pedidos` confiava no `usuario_id` enviado no JSON e `GET /pedidos/usuario/<id>` confiava no identificador de caminho; o login não estabelecia identidade/sessão.
Impact: Qualquer cliente podia registrar pedidos no nome de outra conta, reduzir estoque e consultar dados de pedidos alheios.
Recommendation: Estabelecer identidade autenticada no login, exigir sessão para criar pedido e limitar leitura por usuário à própria identidade; permitir o token administrativo para operações de suporte.

### [MEDIUM] Consultas N+1 ao compor pedidos
File: `models.py:171-201, 203-233`
Description: Para cada pedido consulta itens, e para cada item consulta o nome do produto, além da consulta inicial. O mesmo padrão aparece nas duas funções de listagem.
Impact: O número de idas ao SQLite cresce com pedidos e itens, aumentando latência e duplicando lógica de composição.
Recommendation: Consultar pedidos, itens e produtos em consultas agrupadas (ou JOIN) e compartilhar uma única rotina de montagem; comparar dados retornados.

### [MEDIUM] Validação de entrada inconsistente na fronteira
File: `controllers.py:24-54, 64-93, 146-165, 167-186, 188-206, 237-245`
Description: Criação e atualização de produto duplicam validações diferentes (atualização não valida categoria nem tamanho do nome); login e atualização de status acessam `dados.get` sem validar se JSON existe/é objeto; quantidades de itens não são validadas antes do uso em `models.py:139-146`.
Impact: Payloads malformados produzem 500, e dados inválidos podem ser persistidos ou provocar comportamento inesperado no estoque.
Recommendation: Definir schemas/validação de fronteira consistentes para cada operação e manter as mesmas regras entre criação e atualização, preservando status/respostas conforme o contrato aprovado.

### [MEDIUM] Erros internos são devolvidos ao cliente
File: `controllers.py:10-12, 21-22, 60-62, 95-96, 125-126, 164-165, 185-186, 218-220, 291-292`; `app.py:77-78`
Description: Exceções são convertidas em texto no campo `erro` ou `detalhes` e retornadas ao cliente.
Impact: Mensagens de SQLite e exceções podem revelar estrutura, consultas ou dados internos e respostas de falha ficam inconsistentes.
Recommendation: Centralizar tratamento HTTP, registrar detalhes apenas no servidor e devolver mensagem pública estável, definindo mapeamento de erros sem alterar silenciosamente contratos existentes.

### [MEDIUM] Pedido não é criado em transação atômica
File: `models.py:133-169`
Description: O código valida estoque, insere pedido, itens e atualiza estoque antes de um único `commit`, mas não inicia transação explícita nem desfaz alterações em falha; a validação e atualização do estoque não são condicionais/atômicas.
Impact: Falha no meio do fluxo ou pedidos simultâneos podem deixar dados inconsistentes ou vender além do estoque.
Recommendation: Executar caso de uso em transação explícita, com rollback em falha e atualização condicional do estoque; validar com cenário de falha e concorrência em banco de teste.

### [LOW] Identificador genérico `id` obscurece papel
File: `controllers.py:56`; `models.py:24, 43, 54, 65, 89, 122`
Description: `id` é usado para produto/usuário criado e como argumento de diversas operações, apesar de entidades diferentes.
Impact: Em módulos com vários domínios aumenta a chance de confundir identificadores e torna chamadas/revisões menos legíveis.
Recommendation: Usar nomes explícitos como `produto_id` e `usuario_id`, preservando parâmetros externos das rotas.

### [LOW] Literais de domínio e percentuais sem nome
File: `models.py:247-262, 272`; `controllers.py:52, 242`
Description: Limiares e percentuais de desconto, estados de pedido e lista de categorias estão embutidos nas expressões de negócio.
Impact: Alterações de política exigem localizar literais entre código e tornam regras menos autoexplicativas.
Recommendation: Nomear constantes/enums de domínio para estados, categorias e faixas de desconto, sem tratar valores que sejam dados estruturais como magic numbers.

================================ Total: 15 findings ================================

## Análise do projeto e cobertura

Componente auditado: API de e-commerce descrita no README. Foram efetivamente lidos 6 arquivos únicos: `README.md`, `requirements.txt`, `app.py`, `controllers.py`, `models.py` e `database.py`. Inventário foi obtido com `Get-ChildItem` e `rg --files`; conteúdo e linhas foram conferidos integralmente nos arquivos de aplicação. Não foram encontrados testes, lockfiles, configuração de deploy, Dockerfile/Compose ou migrations. O diretório de relatórios não existia antes desta auditoria. Uma revisão completa adicional do código original expandiu o relatório inicial de 11 para 15 findings ao confirmar escrita de catálogo pública, chave fixa exposta, debug público e ausência de vínculo de identidade em pedidos.

Linguagem: Python (versão/runtime não verificados). Framework: imports e API indicam Flask; `requirements.txt` declara Flask 3.1.1 e Flask-CORS 5.0.1, sem lockfile/ambiente instalado para confirmar resolução. Persistência: SQLite, caminho relativo `loja.db`; tabelas `produtos`, `usuarios`, `pedidos`, `itens_pedido`, criadas no primeiro acesso por `database.get_db`. Arquitetura atual: módulos globais com rotas no `app.py`, funções de controller em `controllers.py`, SQL/acesso a dados misturado em `models.py` e inicialização/conexão/schema/seeds em `database.py`.

Interfaces observadas: Flask HTTP, rotas de produtos, usuários/login, pedidos, relatório, health, raiz e administração, conforme `app.py:11-78`; entry point `app.py:80-88`. O README sugere `pip install -r requirements.txt` e `python app.py`, mas não foi executado. Não foi identificada API Flask explicitamente deprecated no uso visível (`Flask`, `jsonify`, `request`, `add_url_rule`, `route`, `run`); a documentação oficial da API consultada descreve a API Flask 3.1.x. Como o runtime e as versões efetivamente instaladas não foram verificados, a inspeção de deprecation fica limitada à API visível e não comprova ambiente resolvido: [Flask API 3.1.x](https://flask.palletsprojects.com/en/stable/api/) e [Flask changelog 3.1.x](https://flask.palletsprojects.com/en/stable/changes/).

## Linha de base e limitações da auditoria inicial

Na fase de auditoria, não foi executado teste/boot para evitar criar `loja.db` e dados no projeto. Após autorização da Fase 3, o snapshot original rastreado por Git foi executado em diretório temporário com banco descartável. Baseline observado: raiz 200; produtos 200 com 10 itens; usuários 200 expondo `senha`; health 200 expondo chave fixa e `debug=true`; relatório 200; `POST /admin/query` com `SELECT COUNT(*)` 200; escrita de produto anônima 201; pedido anônimo 201; pedidos de outro usuário consultáveis sem login 200. A execução não alterou o banco do projeto. Nenhuma contagem de LOC foi realizada.

Suspeita inicial: `database.py:8-10` mantinha conexão global compartilhada com `check_same_thread=False`; foi eliminada pela conexão por contexto de requisição na implementação final.

## Plano de refatoração proposto


Plano aprovado e implementado: composição em `src/app.py`; configuração em `src/config/settings.py`; rotas em `src/views/routes.py`; validação/casos de uso em `src/services.py`; controllers finos e persistência em `src/models`; middleware de erro central; SQL parametrizado; `/admin/query` desativado; token administrativo fail-closed nas operações sensíveis e escrita de produto; sessão assinada no login para criar pedidos como a própria conta e ler os próprios pedidos; segredo removido das respostas e de configuração fixa; novas senhas com hash e migração gradual de senha antiga ao login; consultas agrupadas de pedidos; pedidos transacionais e validação de entrada. Rotas administrativas exigem `X-Admin-Token`; sem token configurado retornam 503, token inválido retorna 401. Rotas de pedido exigem sessão própria (401 anônimo, 403 ao tentar agir como outro usuário) ou token administrativo. `/admin/query` retorna 410 após autorização. Contas de demonstração conhecidas não são recriadas; os 10 produtos iniciais continuam sendo semeados. Essas diferenças foram registradas como mudança intencional.

## Validação após refatoração

Dependências declaradas foram instaladas apenas em diretório temporário, sem alteração de requirements/lockfile: Flask 3.1.1, Flask-CORS 5.0.1; dependências transitivas resolvidas nesse ambiente incluíram Werkzeug 3.1.9. Python confirmado: 3.13.14. O daemon Docker não estava acessível no sandbox (`docker info` retornou acesso negado ao pipe); como Docker não era requisito do usuário, foi usado ambiente local isolado. A documentação oficial consultada para APIs Flask não mostra uso deprecated nos símbolos visíveis: [Flask API 3.1.x](https://flask.palletsprojects.com/en/stable/api/) e [Flask changelog 3.1.x](https://flask.palletsprojects.com/en/stable/changes/).

Comandos executados: `python -m pip install --target <TEMP>/code-smells-project-deps -r requirements.txt` (após autorização de rede); suíte temporária de cliente Flask com `ast.parse` em todos os módulos, banco SQLite temporário e 34 verificações; comando Flask `init-db`; suíte adicional com WSGI em `127.0.0.1` verificando `/health` por HTTP. Resultados: sucesso. Cenários incluíram rotas públicas e protegidas, token ausente/inválido/Unicode/válido, sessão de login, criação de pedido anônima negada e tentativa entre usuários negada, hashes e migração de login, CRUD de produtos, pedidos/estoque, status, relatório, endpoint SQL desativado, reset autorizado e anônimo, payload de busca tipo SQL injection, rollback no meio da transação, sanitização de erro interno e preservação dos 10 produtos de exemplo. A validação comparativa do baseline original também foi feita no diretório/banco temporário descrito acima.

Durante a validação do comando `init-db`, a primeira execução na instância criada pela factory não encontrou o comando porque ele estava registrado apenas na instância global. A inscrição foi movida para `create_app`; o teste do CLI runner e o boot WSGI passaram após a correção.

## Matriz de rastreabilidade final

| Finding | Impacto original | Arquivo/linha original | Escopo aprovado | Localização atual | Evidência final | Estado |
|---|---|---|---|---|---|---|
| CRITICAL — SQL arbitrário | Leitura/escrita SQL pública | `app.py:59-78` | Desativar endpoint | `src/controllers/store_controller.py:205-207`; `src/views/routes.py` | POST autenticado respondeu 410; SQL não executado | resolvido |
| CRITICAL — SQL injection | Entrada concatenada em SQL | `models.py:47-50,109-111,126-129,148-166,279-299` | Binding parametrizado | `src/models/store.py` | revisão de todas as consultas; payload de busca não alterou consulta | resolvido |
| HIGH — acesso a dados administrativos | Reset, usuários, pedidos e relatório públicos; senha serializada | `app.py:47-78`; `controllers.py:128-144,222-235,257-262`; `models.py:72-87` | Fail-closed e remoção de senha da resposta | `src/views/routes.py`; `src/models/store.py:66-74` | anônimo 401, sem configuração 503, token válido 200; nenhuma chave `senha` serializada | resolvido |
| HIGH — senha em texto puro | Banco e login comparavam texto puro | `database.py:26-35,75-83`; `models.py:72-131` | Hash e migração gradual | `src/models/store.py:80-101`; `src/models/database.py` | novo login e migração legada verificados no banco descartável | resolvido |
| HIGH — controller pesado | Regras, SQL e efeitos no fluxo HTTP | `controllers.py:24-58,64-96,188-220,237-255,264-292` | Separar camadas | `src/controllers/store_controller.py`; `src/services.py`; `src/models/store.py` | revisão de responsabilidades e exercício de rotas | resolvido |
| HIGH — escrita pública de produtos | Cliente podia criar, alterar ou remover catálogo | `app.py:11-16` | Proteger escrita com token administrativo | `src/views/routes.py` | sem token 401, token válido completou CRUD | resolvido |
| HIGH — chave de assinatura fixa/exposta | Chave constante em config e em `/health` | `app.py:7`; `controllers.py:285-289` | Config externa/efêmera e remover resposta | `src/config/settings.py`; `src/models/store.py` | leitura de config e resposta de health; chave não retornada | resolvido |
| HIGH — debug público | Debug ligado no bind de todas as interfaces | `app.py:8,88` | Debug off por padrão | `src/config/settings.py`; `src/app.py` | configuração padrão `False`; WSGI boot e HTTP health passaram | resolvido |
| HIGH — identidade de pedido falsificável | `usuario_id` e ID de caminho confiados sem login | `controllers.py:188-203,222-225`; `app.py:23-26` | Sessão e autorização por proprietário | `src/views/routes.py`; `src/controllers/store_controller.py` | anônimo 401; usuário tentando ID de outro 403; usuário autenticado cria e consulta o próprio pedido | resolvido |
| MEDIUM — consultas N+1 | Consultas por pedido/item | `models.py:171-233` | Agrupar consultas | `src/models/store.py:136-161` | query agrupada/LEFT JOIN revisada; payload de pedidos exercitado | resolvido |
| MEDIUM — validação inconsistente | Payloads malformados e quantidades inválidas | `controllers.py:24-54,64-93,146-206,237-245`; `models.py:139-146` | Validação de fronteira e invariantes | `src/services.py`; controllers | CRUD/pedido/estoque inválido verificados | resolvido |
| MEDIUM — erro interno exposto | Texto de exceção no JSON público | `controllers.py:10-292`; `app.py:77-78` | Resposta genérica e log privado | `src/middlewares/error_handler.py`; `src/controllers/store_controller.py` | exceção injetada retornou JSON genérico sem detalhe | resolvido |
| MEDIUM — não atomicidade do pedido | Estoque/pedido podiam divergir em falha | `models.py:133-169` | Transação com rollback/estoque condicional | `src/models/store.py:106-133` | falha após update parcial por item duplicado deixou estoque/pedidos inalterados | resolvido |
| LOW — nomes genéricos | Identificadores `id` ocultavam entidade | `controllers.py:56`; `models.py:24,43,54,65,89,122` | Nomes explícitos | `src/controllers/store_controller.py`; `src/views/routes.py`; wrappers compatíveis | assinatura/rota usa `produto_id`, `usuario_id`, `pedido_id`; `id` restante é chave do contrato JSON/SQLite | resolvido |
| LOW — literais de domínio | Estados, categorias e faixas sem nomes | `models.py:247-262`; `controllers.py:52,242` | Constantes de domínio | `src/models/store.py:5-7` | `VALID_CATEGORIES`, `ORDER_STATUSES`, `DISCOUNT_TIERS`; busca final revisada | resolvido |

**Reconciliação:** 15 findings identificados no código original: 2 CRITICAL, 7 HIGH, 4 MEDIUM, 2 LOW. 15 resolvidos; 0 parciais; 0 pendentes. As mudanças observáveis intencionais de acesso são descritas acima; o comportamento de endpoint não foi considerado preservado anonimamente quando o acesso passou a exigir sessão/token.

================================ PHASE 3: REFACTORING COMPLETE ================================
## New Project Structure
```text
app.py                         # compatibility entry point
src/
├── app.py                     # composition root
├── config/settings.py
├── controllers/store_controller.py
├── middlewares/error_handler.py
├── models/database.py
├── models/store.py
├── services.py
└── views/routes.py
```

## Validation
✓ Application boots without errors — WSGI server started in a temporary test process; `/health` returned HTTP 200.
✓ All original endpoints respond correctly — route/method exercise and baseline comparison completed; the intentional authentication changes and disabled `/admin/query` are recorded above.
✓ All identified anti-patterns resolved — 15/15 findings reviewed and verified in the traceability matrix.
===============================================================================================

The temporary validation used isolated dependencies and SQLite files. No temporary test suite or dependency files were added to the project. Configure `ADMIN_TOKEN` to enable administrative operations and a stable `SECRET_KEY` to preserve login sessions across restarts. The development server remains the README entry point and should be deployed behind a production WSGI server.
