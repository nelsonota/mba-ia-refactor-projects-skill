## Checklist de Validação

### Fase 1 — Análise
- [x] Linguagem detectada corretamente — Python confirmado por extensão, conteúdo e README; runtime não verificado.
- [x] Framework detectado corretamente — Flask confirmado por imports/inicialização e resolvido como 3.1.1 em ambiente isolado; o ambiente original não tinha dependências instaladas.
- [x] Domínio da aplicação descrito corretamente — API de e-commerce, catálogo, usuários, pedidos e relatório conforme rotas/models.
- [x] Número de arquivos analisados condiz com a realidade — 6 arquivos únicos lidos integralmente; cobertura explicada no relatório.

### Fase 2 — Auditoria
- [x] Relatório segue o template definido nos arquivos de referência — `reports/audit-project.md` criado com findings e seções adicionais.
- [x] Cada finding tem arquivo e linhas exatos — 11 findings com evidências e linhas.
- [x] Findings ordenados por severidade (CRITICAL → LOW) — ordem conferida.
- [x] Mínimo de 5 findings identificados — 11 achados distintos; linhas e impactos descritos.
- [x] Detecção de APIs deprecated incluída (se aplicável) — Flask 3.1.1 e Werkzeug 3.1.9 resolvidos no ambiente temporário; símbolos usados conferidos na documentação oficial Flask 3.1.x, nenhum uso deprecated identificado.
- [x] Skill pausa e pede confirmação antes da Fase 3 — a pausa foi apresentada após a auditoria e a confirmação explícita foi recebida antes da refatoração.

### Fase 3 — Refatoração
- [x] Estrutura de diretórios segue padrão MVC — `src/config`, `src/models`, `src/views`, `src/controllers`, `src/middlewares` e `src/app.py` implementados.
- [x] Configuração extraída para módulo de config (sem hardcoded) — segredo vem do ambiente ou é gerado aleatoriamente; debug off por padrão; token administrativo somente por ambiente.
- [x] Models criados para abstrair dados — SQLite e operações de domínio em `src/models`.
- [x] Views/Routes separadas para visualização ou roteamento — rotas/blueprint em `src/views/routes.py`.
- [x] Controllers concentram o fluxo da aplicação — entrada/resposta em controllers, validação em services e dados em models.
- [x] Error handling centralizado — middleware genérico e respostas de falha sanitizadas; falha injetada exercitada.
- [x] Entry point claro — composition root `src/app.py`, com wrapper legado `app.py` e inicialização explícita do schema no boot.
- [x] Aplicação inicia sem erros — WSGI serviu HTTP em loopback e `/health` respondeu 200; teste em DB temporário.
- [x] Endpoints originais respondem corretamente — baseline original executado em cópia temporária; 34 verificações finais cobrindo todas as rotas/métodos, com mudanças de acesso e endpoint SQL documentadas.

## Evidências e limitações

Fase 1 analisou 6 arquivos originais. Não havia suíte de testes ou lockfile. Após a aprovação, o snapshot original rastreado por Git foi iniciado em diretório/banco temporário para baseline (raiz/produtos/usuários/relatório/admin query). Versões Python 3.13.14, Flask 3.1.1 e Flask-CORS 5.0.1 foram verificadas; Werkzeug 3.1.9 resolvido temporariamente. O daemon Docker permaneceu inacessível, mas Docker não era exigência de execução do usuário. O relatório contém comandos, logs resumidos, evidências, limitações e matriz integral. Contagem final: 15 findings (2 CRITICAL, 7 HIGH, 4 MEDIUM, 2 LOW), todos resolvidos com evidência.

## Linha de base

Original: `git show HEAD:code-smells-project/<arquivo>` para materializar o código original em diretório temporário e cliente Flask com SQLite descartável; raiz 200, produtos 200/10 itens, usuários 200 com senha exposta, relatório 200, SQL SELECT administrativo 200. Refatorado: dependências instaladas em diretório temporário; AST de todos os módulos, 34 verificações de cliente Flask e verificação de servidor WSGI real em loopback; todos passaram. Também verificados token inválido Unicode, acesso de pedido anônimo negado, isolamento entre dois usuários, rollback após falha de estoque, migração de senha plaintext para hash, preservação de produto de exemplo e mensagem 500 sanitizada. Nenhum banco no projeto foi criado/alterado pelos testes.

## Bloqueios e próxima etapa

Fase 3 autorizada pelo usuário (`y`) e concluída. Mudanças de acesso: rotas administrativas, dados gerais de usuários/pedidos/relatórios e escrita de produtos exigem `X-Admin-Token`; token ausente retorna 503, inválido 401. Criação de pedido e leitura por usuário exigem sessão de login e ficam limitadas à conta autenticada; usuário não pode agir em nome de outra conta (403). `/admin/query` responde 410. Sem conta padrão com senha conhecida; a chave secreta não é devolvida por health. Os dez produtos de exemplo permanecem. Configure `ADMIN_TOKEN` antes das operações administrativas e `SECRET_KEY` estável para preservar sessões entre reinícios; senha legada migra para hash no primeiro login bem-sucedido. Testes e baseline foram isolados; nenhuma suíte permanente foi adicionada.
