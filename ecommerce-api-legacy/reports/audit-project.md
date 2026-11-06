================================ PHASE 1: PROJECT ANALYSIS ================================
Language:      JavaScript (Node.js v24.18.0 local; runtime declarado: não especificado)
Framework:     Express declarado ^4.18.2; resolvido no lockfile/ambiente temporário: 4.22.1
Dependencies:  sqlite3 declarado ^5.1.6; resolvido no lockfile/ambiente temporário: 5.1.7
Domain:        API de LMS com checkout, matrículas, pagamentos, usuários e relatório financeiro
Architecture:  Express; composição em src/app.js, rotas, regras e SQL em AppManager, utilitários/estado em utils
Source files:  3 arquivos de aplicação analisados
DB tables:     users, courses, enrollments, payments, audit_logs (SQLite em memória)
===========================================================================================

Cobertura e método: examinados integralmente src/app.js (14 linhas), src/AppManager.js (141 linhas), src/utils.js (25 linhas), package.json (14 linhas), api.http (26 linhas) e README.md (9 linhas): 6 caminhos e 229 linhas. Linhas contadas incluindo linhas em branco, conforme arquivos disponíveis. Inspecionados também package-lock.json para versões resolvidas. Excluídos binários/dependências instaladas e artefatos gerados; node_modules não existia. Não foram encontrados testes, configuração de build ou instruções AGENTS.md aplicáveis neste projeto.

Linha de base: README sugere npm install e npm start. node --version retornou v24.18.0. npm ls --depth=0 no projeto mostrou dependências ausentes. Para auditoria, `npm ci --prefix <TEMP>/ecommerce-api-legacy-audit` em cópia isolada do package.json e lockfile resolveu express@4.22.1 e sqlite3@5.1.7. O npm bloqueou os scripts de instalação do sqlite3; nenhum boot ou endpoint foi exercitado. Nenhuma solicitação HTTP foi feita.

Contratos identificados em api.http e src/AppManager.js: POST /api/checkout (400 entrada incompleta; 404 curso ausente; 500 erros de banco; 400 pagamento recusado; 200 JSON de sucesso e grava matrícula/pagamento/auditoria), GET /api/admin/financial-report (JSON dos cursos e alunos), DELETE /api/users/:id (mensagem textual). Não se confirmou comportamento em execução.

================================ ARCHITECTURE AUDIT REPORT ================================
Project: ecommerce-api-legacy
Stack:   JavaScript / Node.js 24.18.0 local / Express 4.22.1 resolvido temporariamente / sqlite3 5.1.7 resolvido temporariamente
Files:   6 analyzed | 229 linhas analisadas

## Summary
CRITICAL: 0 | HIGH: 2 | MEDIUM: 2 | LOW: 2

## Findings

### [SUSPEITA NÃO CONFIRMADA — não contada como finding] Valores de configuração com aparência de credencial
File: src/utils.js:1-6
Description: `dbPass` e `paymentGatewayKey` contêm valores com aparência de credenciais reais versionadas; a chave de pagamento também é interpolada em log em src/AppManager.js:45. Valores omitidos deste relatório.
Impact: Se forem credenciais válidas, qualquer leitor do repositório pode acessar serviços ou abusar de integração; o log expõe a chave a destinos de logging.
Recommendation: Remover do código, rotacionar credenciais caso reais e obter valores de configuração segura no composition root. Estado real/validade não verificado.

### [HIGH] Relatório financeiro administrativo sem autenticação
File: src/AppManager.js:80-129
Description: A rota GET é registrada diretamente sem middleware de identidade/autorização e retorna cursos, receita e nomes de alunos.
Impact: Qualquer cliente que alcance o endpoint pode consultar dados financeiros e pessoais.
Recommendation: Colocar autenticação e autorização fail-closed para a rota administrativa e validar acesso autorizado e recusas.

### [HIGH] God class combina rotas, regras de checkout e persistência
File: src/AppManager.js:4-139
Description: `AppManager` inicializa esquema/seeds, associa três endpoints, valida entrada, decide pagamento, cria usuário/matrícula e executa consultas SQL de relatórios e exclusão.
Impact: Alterações de regras, HTTP ou armazenamento ficam interdependentes e difíceis de testar isoladamente; o arquivo ultrapassa 130 linhas e acumula responsabilidades distintas.
Recommendation: Separar rotas/views, controllers coordenadores e models/repositórios sob a estrutura MVC indicada, preservando os contratos.

### [MEDIUM] Exclusão ignora falha do banco e declara sucesso
File: src/AppManager.js:131-136
Description: O callback de DELETE não verifica `err` nem resultado e sempre envia mensagem de usuário deletado, inclusive quando a instrução falha ou o ID não existe.
Impact: Clientes recebem confirmação enganosa e não podem distinguir falha de sucesso.
Recommendation: Tratar erro e resultado conforme contrato acordado; comparar status/corpo com baseline antes de alterar comportamento.

### [MEDIUM] Consultas N+1 no relatório financeiro
File: src/AppManager.js:92-126
Description: A consulta de matrículas por curso é seguida, dentro de cada matrícula, por duas consultas adicionais (usuário e pagamento).
Impact: O número de operações SQL cresce com os cursos e matrículas, aumentando latência e complexidade concorrente do callback.
Recommendation: Buscar dados relacionados em consulta agregada/join ou em lote no model, preservando formato e ordem observável do relatório.

### [LOW] Identificadores abreviados ocultam o papel dos dados
File: src/AppManager.js:29-33, 37-40, 50-57
Description: Variáveis `u`, `e`, `p`, `cid`, `cc`, `enr`, `enrId` e `c` representam campos de requisição, curso ou matrícula sem indicar claramente domínio e papel.
Impact: Dificultam revisão do fluxo de checkout e elevam risco de confundir IDs e dados pessoais durante manutenção.
Recommendation: Renomear com termos de domínio durante a refatoração, sem alterar nomes dos campos externos.

### [LOW] Estado global e valores de domínio sem nome explicativo
File: src/utils.js:9-10, 19-22; src/AppManager.js:46, 68
Description: `globalCache` e `totalRevenue` são estado compartilhado de escopo de módulo; o status depende do prefixo literal `"4"` e a senha padrão `"123456"` é aplicada silenciosamente quando `pwd` falta. O cache é mutável sem isolamento entre requisições.
Impact: Os nomes não explicam política/validade do estado e os literais escondem regra de cartão e fallback de credencial, dificultando auditoria e manutenção. O risco do fallback se agrava porque a validação de fronteira não exige senha.
Recommendation: Tornar regras nomeadas/configuradas e explícitas, limitar estado compartilhado e exigir validação apropriada; mudanças de comportamento de checkout devem ser aprovadas e comparadas com baseline.

================================ Total: 6 confirmed findings ================================

APIs deprecated: inventário do código não encontrou chamadas Express conhecidas como deprecated na documentação de migração. As rotas usam `app.post`, `app.get` e `app.delete`; não há uso de `app.param(fn)`, `res.redirect('back')`, métodos singularizados de accepts ou `app.del()`. Dependências executadas em container descartável: Express 4.22.1, SQLite3 5.1.7; runtime do container Node v20.20.2. O runtime local identificado antes foi Node v24.18.0; não há versão declarada pelo projeto. Referências oficiais consultadas: [guia oficial de migração Express 5](https://expressjs.com/en/guide/migrating-5/) descreve APIs removidas/deprecated e [referência Express 4](https://expressjs.com/en/4x/api/) documenta a API da linha declarada. Não foi identificado uso deprecated entre as APIs inventariadas.

Limitações/suspeitas: valores em `utils.js` têm aparência de segredos, mas sua validade não foi testada nem deve ser testada contra serviços reais. Não há middleware de autenticação visível em nenhum dos arquivos de aplicação examinados. A instalação isolada não executou script nativo sqlite3, bloqueando boot e interfaces. Não há evidência de SQL injection nos trechos observados: consultas com entrada usam placeholders; não foi contado como finding.

Plano para Fase 3 (sujeito a aprovação): criar config/settings.js, models para persistência e regras de domínio, views/routes.js, controllers para coordenação, middlewares/error_handler.js e src/app.js como composition root; mover erros e responsabilidades da God class; proteger rota administrativa fail-closed; substituir configuração sensível por ambiente; tornar validação e regras de checkout explícitas; consolidar consultas do relatório. Preservar contratos externos sempre que possível. Correções de autenticação e validação podem alterar acessibilidade/aceitação de requisições e serão descritas como alterações de comportamento.

Baseline executável em Docker: primeira tentativa em `node:24-trixie` não encontrou binding sqlite3; compilação local nessa imagem falhou no node-gyp. Alternativa em container descartável `node:20-bookworm` (workspace montado somente leitura; dependências instaladas em `/tmp`) funcionou após `npm rebuild sqlite3 --foreground-scripts`. Ambiente efetivo: Node v20.20.2, Express 4.22.1, SQLite3 5.1.7. Boot observado pelo log `Frankenstein LMS rodando na porta 3000...`. GET `/api/admin/financial-report` sem credencial retornou 200 e JSON inicial dos cursos; DELETE `/api/users/1` retornou 200 e corpo `Usuário deletado, mas as matrículas e pagamentos ficaram sujos no banco.`; POST `/api/checkout` com cartão iniciado por 5 retornou 400 e `Pagamento recusado`; POST com cartão iniciado por 4 retornou 200 e `{"msg":"Sucesso","enrollment_id":2}`. GET posterior ao checkout retornou 200 e mostrou matrícula `User2` e receita 497 no curso Docker, comprovando o efeito em SQLite em memória. A ordem dos cursos variou entre respostas, conforme concorrência das consultas. Container removido.

Limitação de baseline: a exclusão de usuário foi exercitada em uma requisição isolada antes dos checkouts; os efeitos de integridade referencial não são observáveis porque o banco está em memória e a aplicação não declara constraints. Nenhum teste automatizado existe. O runtime Node 20 do container difere do Node 24.18.0 local, mas não há runtime declarado no projeto; o container foi usado somente para baseline isolado.

Correção de classificação: a primeira versão do relatório contou os valores acima como CRITICAL apesar de não ter confirmado que fossem credenciais válidas. Pela regra do catálogo, são uma suspeita e foram excluídos da contagem confirmada. Permanecem HIGH 2, MEDIUM 2 e LOW 2 — 6 findings confirmados.

Estado da Fase 2: concluída antes da aprovação explícita. Baseline em Docker e documentação de versões/API estão descritos acima.

================================ PHASE 3: REFACTORING COMPLETE ================================
## New Project Structure
src/
├── config/settings.js
├── models/lms_model.js
├── services/checkout_service.js
├── views/routes.js
├── controllers/lms_controller.js
├── middlewares/admin_auth.js
├── middlewares/request_validation.js
├── middlewares/error_handler.js
└── app.js (composition root)

## Validation
✓ Application boots without errors — clean container node:24-trixie, Node v24.22.2, Express 4.22.1, better-sqlite3 13.0.3.
✓ All original endpoints respond correctly — methods, paths, and expected input/output shapes remain available and were exercised; approved security behavior changes are documented below.
✓ All identified anti-patterns resolved — all 6 confirmed source findings and the new MEDIUM driver maintenance finding are resolved. Credential-like configuration remains an unconfirmed suspicion, not a finding.
===============================================================================================

### Execução e comparação de contratos

Validação final em Docker `node:24-trixie`: `npm ci --foreground-scripts`, `npm audit`, `npm ls --depth=0`, `node --check src/models/lms_model.js`, `node --check src/app.js`, `node src/app.js`. Versões efetivas: Node 24.22.2, Express 4.22.1, better-sqlite3 13.0.3. O binding nativo compilou via node-gyp. Audit final: zero vulnerabilidades. Não há suite de testes automatizados.

Resultados HTTP observados via harness executado dentro do container: sem token configurado, admin 503; com configuração injetada, sem credencial/token inválido 401 e válido 200 com JSON. Checkout sem `pwd` 400 `Bad Request`; aprovado 200 `{"msg":"Sucesso","enrollment_id":2}`. DELETE existente 200/corpo baseline; inexistente 404 `Usuário não encontrado`. O relatório retorna os cursos e o checkout cria matrícula/pagamento em SQLite. Após a migração, não repetimos os cenários de pagamento recusado nem a falha simulada do model; ambos haviam passado antes da troca do driver.

### Matriz de rastreabilidade

Reconciliada com `reports/checklist.md`. Dos seis findings confirmados, HIGH rota admin: resolvido por autenticação Bearer fail-closed, testada nas três condições; contrato de acesso alterado. HIGH God class: resolvido; AppManager removido. MEDIUM DELETE: resolvido; existente 200, ausente 404 e falha simulada 500. MEDIUM N+1: resolvido por consulta join no model. LOW identificadores: resolvido com nomes de domínio. LOW estado/default: estado global removido, senha obrigatória e hash scrypt com salt; prefixo de cartão nomeado. Os valores que pareciam credenciais foram removidos, mas sua validade não foi confirmada; são suspeita não contada como finding.

### Limitações e decisão necessária

As autorizações específicas foram recebidas: senha ausente responde 400 e ID DELETE inexistente responde 404. As mudanças foram verificadas no container.

### Atualização de dependências e risco de suporte

`npm audit` no lockfile original registrou 13 advisories (2 CRITICAL, 8 HIGH, 1 MEDIUM, 2 LOW), incluindo `tar`, `proxy-addr`, `sqlite3`, `body-parser`, `ip-address`, `brace-expansion`, `path-to-regexp` e `qs`. Com aprovações específicas, foram aplicadas atualizações compatíveis e o override `qs` 6.17.1, depois o driver arquivado foi substituído por `better-sqlite3` 13.0.3. `package.json` declara Node >=22. Instalação limpa final reportou zero vulnerabilidades; o binding compilou e iniciou em Node 24.22.2. Fontes oficiais: [releases do better-sqlite3](https://github.com/WiseLibs/better-sqlite3/releases), [metadados oficiais do pacote](https://github.com/WiseLibs/better-sqlite3/blob/master/package.json), que exigem Node >=22 na versão 13, [repositório arquivado node-sqlite3](https://github.com/TryGhost/node-sqlite3) e [release sqlite3 6.0.1](https://github.com/TryGhost/node-sqlite3/releases/tag/v6.0.1).

## Estado final da Fase 3

Finding novo durante a Fase 3: [MEDIUM] driver SQLite upstream arquivado. Evidência: versão anterior `sqlite3@6.0.1` e repositório oficial arquivado. Impacto: ausência de manutenção futura de segurança/correções. Resolvido após aprovação explícita: migrado para `better-sqlite3@13.0.3`, dependência mantida, com chamadas síncronas no model e Node mínimo >=22; build do binding, boot, relatório e checkout foram exercitados no container.

Fase 3 concluída conforme o critério esclarecido pelo usuário: as assinaturas de entrada e saída dos três endpoints originais permanecem disponíveis e foram exercitadas. As mudanças aprovadas de comportamento continuam explicitadas: relatório admin agora é protegido e exige Bearer; checkout sem senha retorna 400; DELETE de ID inexistente retorna 404. Os seis findings originais confirmados e o finding novo de manutenção do driver estão resolvidos. A suspeita de credenciais removidas não foi comprovada como credencial real e permanece separada da contagem. A instalação limpa e o audit foram repetidos após a migração; cenários HTTP de pagamento recusado e falha simulada de model não foram repetidos depois da migração do driver, embora ambos tenham sido exercitados antes dela.
