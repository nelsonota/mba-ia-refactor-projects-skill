## Checklist de Validação

### Fase 1 — Análise
- [x] Linguagem detectada corretamente
- [x] Framework detectado corretamente
- [x] Domínio da aplicação descrito corretamente
- [x] Número de arquivos analisados condiz com a realidade

### Fase 2 — Auditoria
- [x] Relatório segue o template definido nos arquivos de referência
- [x] Cada finding tem arquivo e linhas exatos
- [x] Findings ordenados por severidade (CRITICAL → LOW)
- [x] Mínimo de 5 findings identificados
- [x] Detecção de APIs deprecated incluída (se aplicável)
- [x] Skill pausa e pede confirmação antes da Fase 3

### Fase 3 — Refatoração
- [x] Estrutura de diretórios segue padrão MVC
- [x] Configuração extraída para módulo de config (sem hardcoded)
- [x] Models criados para abstrair dados
- [x] Views/Routes separadas para visualização ou roteamento
- [x] Controllers concentram o fluxo da aplicação
- [x] Error handling centralizado
- [x] Entry point claro
- [x] Aplicação inicia sem erros
- [x] Endpoints originais respondem corretamente — verificação comparativa registra as mudanças de contrato aprovadas: `/admin/query` removido; `/admin/reset-db` requer token; health omite campos internos; usuários não incluem senha

## Linha de base, evidências e comandos

- Projeto inicialmente: seis arquivos de produto na raiz; sem testes e sem lockfile.
- Container `python:3.13-slim`; código montado read-only; SQLite em diretório temporário descartável. Dependências resolvidas após a correção: Flask 3.1.1, flask-cors 6.0.0, Blinker 1.9.0, Click 8.5.0, ItsDangerous 2.2.0, Jinja2 3.1.6, MarkupSafe 3.0.4, Werkzeug 3.1.9.
- Comparação da versão original `HEAD` com MVC após as correções: 26 chamadas com status/corpo equivalentes (timestamps gerados normalizados), zero diferenças imprevistas. Testes adicionais confirmaram as mudanças de contrato listadas na caixa de endpoints.
- Segurança em container: SQL injection em login e busca não alterou consultas; entrada com aspas em produto foi aceita como dado; senha legada foi migrada para hash scrypt e login continuou funcionando; nova senha também armazenada em hash; APIs de usuário omitiram senha; health omitiu chave/path/debug/ambiente; SECRET_KEY ausente impede boot.
- Admin: `/admin/query` removido (404, com ou sem token); `/admin/reset-db` retorna 401 sem token e 200 com Bearer token válido. Reset executado somente em banco temporário.
- MVC/servidor: boot verificado com Flask debug desligado. Erros simulados em controller e health retornaram os corpos/status existentes via middleware; HTTP 4xx/405 preservados.
- Pedidos: JOIN validado com pedido e item. Conexões isoladas por thread e fechadas no teardown; concorrência simultânea não submetida a stress test.
- Finding CVE-2024-6844 resolvido pelo pin `flask-cors==6.0.0`, que foi instalado e testado. Fonte do advisory: https://github.com/advisories/GHSA-8vgw-p6qm-5gr7 ; release 6.0.0: https://github.com/corydolphin/flask-cors/releases/tag/6.0.0 .
- APIs deprecated verificadas contra Flask 3.1.x API/changelog e uso do Flask-CORS; nenhum símbolo utilizado identificado como deprecated: https://flask.palletsprojects.com/en/stable/api/ ; https://flask.palletsprojects.com/en/stable/changes/ .

## Correções

- SQL de domínio usa placeholders e parâmetros SQLite.
- Endpoint de SQL arbitrário removido; reset administrativo protegido com token Bearer e comparação em tempo constante.
- SECRET_KEY obrigatório no ambiente; segredo e detalhes internos removidos do health.
- Senhas legadas migradas para hash scrypt; novas senhas armazenadas em hash e nunca serializadas.
- flask-cors atualizado para 6.0.0.
- MVC em `src/`, entry points compatíveis na raiz, conexões SQLite por thread, consultas de pedidos com JOIN e erros centralizados.

## Limitações residuais

- `/admin/reset-db` permanece uma operação destrutiva, agora protegida por `ADMIN_TOKEN`; configure e rotacione esse token como segredo operacional.
- A configuração global `CORS(app)` permanece permissiva para origens, como no comportamento anterior; a auditoria não avaliou requisitos de origens por cliente.
- Não foi executado stress test de concorrência. A verificação de endpoints foi funcional/contratual em servidores e bancos isolados, sem serviços externos.
