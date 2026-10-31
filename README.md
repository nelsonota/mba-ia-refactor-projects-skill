# A) Seção "Análise Manual"

A análise abaixo sintetiza os problemas da versão original registrados nos relatórios de auditoria. As localizações e evidências detalhadas estão nos relatórios de cada projeto; as classificações refletem o impacto observado na auditoria.

## code-smells-project

| Severidade | Problema | Relevância |
|---|---|---|
| CRITICAL | Endpoint administrativo executava SQL arbitrário sem autenticação | Qualquer cliente podia ler ou modificar dados. |
| CRITICAL | SQL construído com entradas externas | Permitia injeção em operações de produtos, usuários, login e pedidos. |
| HIGH | Health expunha chave secreta e detalhes internos | Divulgava material sensível e informações da implantação. |
| HIGH | Senhas em texto puro e presentes nas respostas | Uma leitura da API ou do banco expunha credenciais reutilizáveis. |
| MEDIUM | Consultas N+1 em pedidos | O número de consultas crescia com pedidos e itens. |
| MEDIUM | Conexão SQLite global compartilhada entre threads | Requisições concorrentes podiam interferir em cursores e transações. |
| MEDIUM | flask-cors 5.0.1 vulnerável | A correspondência de caminhos da política CORS podia ser incorreta. |

## ecommerce-api-legacy

| Severidade | Problema | Relevância |
|---|---|---|
| HIGH | Relatório financeiro administrativo sem autenticação | Expõe dados financeiros e de alunos a clientes que alcancem a API. |
| HIGH | Transformação previsível de senhas | Facilita a recuperação e aumenta a chance de colisões. |
| HIGH | Rotas, regras e persistência concentradas em `AppManager` | Acopla responsabilidades e dificulta testes e manutenção. |
| HIGH | Número completo do cartão nos logs | Expõe dados de pagamento a quem acessa os registros. |
| MEDIUM | Consultas N+1 no relatório financeiro | A carga de consultas cresce com cursos e matrículas. |
| MEDIUM | Erros de banco ignorados em alguns fluxos | Falhas podiam parecer sucesso ou produzir relatórios incompletos. |
| MEDIUM | Cache global mutável | O estado compartilhado entre requisições não tinha proprietário ou expiração explícitos. |
| MEDIUM | Dependências com advisories de segurança | A árvore de dependências continha versões vulneráveis. |

## task-manager-api

| Severidade | Problema | Relevância |
|---|---|---|
| HIGH | Hash de senha incluído no JSON de usuário | Expõe credenciais derivadas a ataques offline. |
| HIGH | Senhas armazenadas com MD5 sem salt | Facilita tentativas rápidas de recuperação de senha. |
| HIGH | Rotas acumulavam validação, regras e persistência | Acopla o domínio ao Flask e dificulta a evolução e os testes. |
| MEDIUM | Consultas N+1 em listagens e relatórios | Aumenta a latência e a carga conforme crescem os dados. |
| MEDIUM | Uso de `Query.get()` legado no SQLAlchemy resolvido | Dificulta atualizações e pode gerar avisos ou incompatibilidades futuras. |
| MEDIUM | Prioridade sem validação de tipo | Entrada malformada podia gerar erro 500 em vez de resposta de validação. |

Credenciais SMTP e chave fixa no task-manager foram registradas como suspeitas, sem evidência suficiente para classificá-las como achados confirmados.

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

# C) Seção "Resultados"

## Auditorias

| Projeto | CRITICAL | HIGH | MEDIUM | LOW | Total |
|---|---:|---:|---:|---:|---:|
| [code-smells-project](code-smells-project/reports/audit-project.md) | 2 | 2 | 3 | 0 | 7 |
| [ecommerce-api-legacy](ecommerce-api-legacy/reports/audit-project.md) | 0 | 4 | 4 | 0 | 8 |
| [task-manager-api](task-manager-api/reports/audit-project.md) | 0 | 3 | 3 | 0 | 6 |

No code-smells, os sete achados foram tratados. No task-manager, as correções foram aplicadas, mas contas com MD5 legado só são migradas após login bem-sucedido. No ecommerce, a refatoração ficou **bloqueada** quanto à conclusão integral: o relatório financeiro continua sem autenticação enquanto não houver política de acesso, e resta um advisory moderado em `qs`. Os totais acima são de achados arquiteturais, não a contagem de advisories de dependências.

## Estrutura antes e depois

| Projeto | Antes | Depois |
|---|---|---|
| code-smells-project | Arquivos de aplicação, controllers, models e banco na raiz, com responsabilidades concentradas. | MVC em `src/config`, `models`, `views`, `controllers` e `middlewares`; arquivos da raiz permanecem como adaptadores. |
| ecommerce-api-legacy | `src/app.js`, `AppManager.js` e `utils.js`; o manager acumulava rotas, regras e persistência. | Camadas MVC e configuração em `src/`, serviço de hash e middleware; `src/app.js` compõe a aplicação. |
| task-manager-api | `app.py`, `models/`, `routes/`, `services/` e `utils/`; as rotas ainda concentravam regras e acesso a dados. | MVC em `src/`, serializadores e configuração centralizados; entradas e imports antigos permanecem como adaptadores. |

## Checklist e evidências de execução

Os checklists preenchidos incluem análise, auditoria, estrutura MVC, inicialização e comparação das interfaces: [code-smells](code-smells-project/reports/checklist.md), [ecommerce](ecommerce-api-legacy/reports/checklist.md) e [task-manager](task-manager-api/reports/checklist.md). As caixas marcadas registram as verificações feitas; não eliminam as pendências e limitações descritas nos relatórios.

Execuções realizadas para esta documentação em 31/10/2026. Os ambientes Python e bancos SQLite foram temporários; o `seed.py` destrutivo não foi executado. Os logs abaixo são saídas coletadas diretamente dos processos/clientes nesta sessão:

```text
code-smells-project (Flask 3.1.1; DATABASE_PATH temporário):
GET /health -> 200 {"counts":{"pedidos":0,"produtos":10,"usuarios":3},"database":"connected","status":"ok","versao":"1.0.0"}
Listando 10 produtos
GET /produtos -> 200 {"status":true,"items":10}

ecommerce-api-legacy (Express; servidor em porta efêmera):
Frankenstein LMS rodando na porta 3000...
200 /api/admin/financial-report [{"course":"Docker","revenue":0,"students":[]},{"course":"Clean Architecture","revenue":997,"students":[{"student":"Leonan","paid":997}]}]
Processando cartão ************4444
400 /api/checkout card-prefix=5 Pagamento recusado
Processando cartão ************4444
[LOG] Salvando no cache: last_checkout_3
200 /api/checkout card-prefix=4 {"msg":"Sucesso","enrollment_id":2}

task-manager-api (Flask-SQLAlchemy; SQLite temporário vazio):
GET / -> 200 {"message":"Task Manager API","version":"1.0"}
GET /health -> 200 {"status":"ok","timestamp":"2026-10-31 17:38:45.992007"}
GET /tasks -> 200 []
```

Os dois Flask foram exercitados via `Flask.test_client()` porque as regras deste ambiente bloquearam conexões TCP locais; os endpoints e status HTTP foram verificados diretamente contra as aplicações. O Express foi iniciado e acessado por HTTP em porta efêmera. A lista vazia de tarefas é esperada: não foi executado o `seed.py`, que apaga e repopula as tabelas. O code-smells inicializou seu SQLite temporário com 10 produtos e 3 usuários de demonstração. Os cenários comparativos mais amplos e mudanças de contrato aprovadas estão nos [checklists](code-smells-project/reports/checklist.md), [checklists](ecommerce-api-legacy/reports/checklist.md) e [checklists](task-manager-api/reports/checklist.md); os achados pendentes continuam descritos nas respectivas auditorias.

## Comportamento em stacks diferentes

A skill identificou Flask com SQLite direto no code-smells, Express com SQLite em memória no ecommerce e Flask-SQLAlchemy no task-manager. Em cada caso adaptou a separação de responsabilidades às bibliotecas existentes: SQL parametrizado e ciclo de conexão no primeiro, módulos e callbacks/consultas no segundo, e carregamento relacionado e `Session.get()` no terceiro. Os resultados demonstram essas três execuções, não compatibilidade com toda tecnologia. As decisões de segurança e as limitações de ambiente exigiram tratamento específico em cada projeto.

# D) Seção "Como Executar"

## Pré-requisitos

- PowerShell e Codex CLI instalado, autenticado e configurado, com acesso ao modelo `gpt-6-luna`.
- As dependências e runtimes dos projetos: Python 3.13 e pip para os projetos Flask; Node.js e npm para o projeto Express. Os relatórios registram Node 24.18.0 para a execução do ecommerce.
- A skill está em `.agents/skills/refactor-arch` dentro de cada projeto. Os comandos abaixo partem da raiz deste repositório. A skill produz a auditoria e solicita aprovação antes de refatorar; avalie os achados e mudanças de contrato antes de responder.

## Executar a skill

Execute cada bloco a partir da raiz, separadamente:

```powershell
Push-Location code-smells-project
codex -m gpt-6-luna -c 'model_reasoning_effort="low"' "Execute .agents/skills/refactor-arch"
Pop-Location
```

```powershell
Push-Location ecommerce-api-legacy
codex -m gpt-6-luna -c 'model_reasoning_effort="low"' "Execute .agents/skills/refactor-arch"
Pop-Location
```

```powershell
Push-Location task-manager-api
codex -m gpt-6-luna -c 'model_reasoning_effort="low"' "Execute .agents/skills/refactor-arch"
Pop-Location
```

Os projetos já estão refatorados neste repositório. Para repetir a análise da versão original, utilize uma cópia da versão anterior à refatoração com a skill disponível; uma nova execução sobre o estado atual analisará o código atual e poderá alterar os relatórios.

## Validar as aplicações

Em terminais separados, partindo da raiz, instale as dependências e inicie cada servidor. Para Python, recomenda-se um ambiente virtual por projeto. Os dois servidores Flask usam a porta 5000 por padrão, portanto execute-os separadamente.

```powershell
cd code-smells-project
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
$env:SECRET_KEY = '<segredo local forte>'
$env:ADMIN_TOKEN = '<token local forte>'
$env:FLASK_DEBUG = 'false'
python app.py
```

Em outro terminal, confira `Invoke-RestMethod http://localhost:5000/health` e as demais rotas conforme o [relatório](code-smells-project/reports/checklist.md). Use banco temporário para exercitar o reset administrativo, pois ele apaga dados.

```powershell
cd ecommerce-api-legacy
npm ci
npm start
```

Confira `Invoke-RestMethod http://localhost:3000/api/admin/financial-report` e os cenários em [api.http](ecommerce-api-legacy/api.http). O banco é recriado em memória a cada inicialização. Se a instalação do módulo nativo falhar, consulte o [checklist](ecommerce-api-legacy/reports/checklist.md) para os detalhes do rebuild realizado na validação.

```powershell
cd task-manager-api
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python app.py
```

Confira `Invoke-RestMethod http://localhost:5000/health` e `Invoke-RestMethod http://localhost:5000/tasks`. As listas podem estar vazias. O `seed.py` apaga e repovoa tabelas: execute-o somente em banco descartável. Para validação completa, compare status e respostas dos cenários registrados nos checklists com uma linha de base isolada, incluindo as mudanças de contrato aprovadas e as pendências acima.
