# Playbook de refatoração

Os exemplos são pseudocódigo ilustrativo: adapte sintaxe, parâmetros de segurança, transações, erros e APIs à versão e ao framework reais. Confirme contratos antes e depois. Cada transformação corresponde ao catálogo; adicione testes de comportamento relevantes antes de alterar fluxos quando viável.

## 1. Credenciais hardcoded

Antes:
```text
db = connect("admin", "segredo-real")
```
Depois:
```text
config = load_and_validate_environment()
db = connect(config.db_user, config.db_password)
```
Remova valores do código, não os reproduza no relatório e comunique a necessidade de rotação quando houver exposição; não revogue credenciais sem autorização.

## 1a. Rota administrativa sem autenticação/autorização

Antes:
```text
GET /admin/report -> controller.financialReport()
```
Depois:
```text
GET /admin/report -> requireAdminIdentity -> requireAdminPermission -> controller.financialReport()
```
Use o provedor de identidade e as permissões existentes quando houver. Se o projeto não tiver identidade configurada, falhe fechado: exija configuração explícita de credencial/permissão segura e mantenha o recurso indisponível enquanto ela faltar. Nunca deixe a rota pública aguardando decisão externa nem invente credenciais padrão. Verifique sem credencial, com credencial inválida e com identidade autorizada quando disponível; registre a mudança do contrato de acesso.

## 2. SQL injection

Antes:
```text
db.query("SELECT * FROM users WHERE email = '" + email + "'")
```
Depois:
```text
db.query("SELECT * FROM users WHERE email = ?", [email])
```
Use placeholders e binding suportados pelo driver. Identificadores dinâmicos exigem allowlist, pois parâmetros geralmente não os substituem.

## 3. God Class

Antes:
```text
handle_order(req): validate(req); calculate_total(); db.save(); render()
```
Depois:
```text
route -> order_controller.create
order_controller.create(input): order = order_service.create(input); return view(order)
order_service.create(input): order = calculate(input); order_repository.save(order)
```
Separe entrada, coordenação, domínio e persistência preservando ordem, transações e respostas.

## 4. Controller pesado

Antes:
```text
controller.checkout(req): total = sum(req.items) - discount(req); return response(total)
```
Depois:
```text
controller.checkout(req): return response(checkout_service.calculate(req.items))
checkout_service.calculate(items): return sum(items) - discount(items)
```
Mova regras para domínio ou serviço, deixando o controller coordenar o caso de uso.

## 5. Acoplamento rígido

Antes:
```text
service.run(): repo = new SqlRepository(); return repo.find()
```
Depois:
```text
service(repo).run(): return repo.find()
app = compose(service(new SqlRepository(config)))
```
Injete dependências por construtor ou composição nativa; não exija container de DI.

## 6. Estado global mutável

Antes:
```text
global current_user
handle(req): current_user = req.user; return process()
```
Depois:
```text
handle(req): return process(req.user)
process(user): return operation(user)
```
Use contexto por requisição ou armazenamento apropriado, preservando isolamento e concorrência.

## 7. Duplicação de regras

Antes:
```text
web_total = price * quantity * 0.9
cli_total = price * quantity * 0.9
```
Depois:
```text
calculate_total(price, quantity): return price * quantity * DISCOUNT_FACTOR
web_total = calculate_total(price, quantity)
cli_total = calculate_total(price, quantity)
```
Extraia apenas regras comprovadamente equivalentes e teste os consumidores.

## 8. Consultas N+1

Antes:
```text
orders = db.orders()
for order in orders: order.items = db.items_for(order.id)
```
Depois:
```text
orders = db.orders_with_items_eager_loaded()
```
Use join, eager loading ou busca em lote disponível na stack; preserve paginação e resultado, medindo consultas quando viável.

## 9. Validação ausente

Antes:
```text
route(req): return controller.create(req.body.quantity)
```
Depois:
```text
route(req): input = validate_quantity(req.body); return controller.create(input)
```
Rejeite entrada inválida na fronteira conforme contrato e mantenha invariantes essenciais no domínio.

## 10. Erros dispersos

Antes:
```text
route(req): try return create(req) catch e: return response(500, e.stack)
```
Depois:
```text
route(req): return create(req)
error_handler(error): log_internal(error); return safe_contract_response(error)
```
Centralize tradução e registro, sem vazar detalhes; preserve status e formato públicos.

## 11. API deprecated

Antes:
```text
result = legacy_api(input)  // declarada obsoleta na versão instalada
```
Depois:
```text
result = documented_replacement(input)
```
Consulte documentação oficial da versão instalada para status, substituto e diferenças; adapte chamadas e testes. Se não houver substituto compatível comprovado, registre a limitação em vez de inventar um.

## 12. Nomes ambíguos e números mágicos

Antes:
```text
x = total * 0.9
```
Depois:
```text
MEMBER_PRICE_FACTOR = 0.9
member_total = total * MEMBER_PRICE_FACTOR
```
Use nomes de domínio e constantes que expliquem valores estáveis; não altere a regra.

Ao concluir a Fase 3, reavalie cada finding contra seu impacto descrito. Uma mudança de arquivo, nome ou camada não resolve um finding por si só: só marque como resolvido quando evidência da implementação e uma verificação pertinente demonstrarem que o impacto foi eliminado. Findings pendentes, parcialmente tratados ou não verificados permanecem abertos, com risco e evidência explícitos.
