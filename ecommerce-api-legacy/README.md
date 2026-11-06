# ecommerce-api-legacy

LMS API (com fluxo de checkout) em Node.js/Express usada como entrada do desafio `refactor-arch`.

## Como rodar

Requer Node.js 22 ou superior (necessário para `better-sqlite3` 13).

```bash
npm install
npm start
```

A aplicação sobe em `http://localhost:3000`. O banco SQLite é em memória e já carrega seeds automaticamente no boot; `better-sqlite3` usa chamadas síncronas.

Exemplos de requisições estão em `api.http`.

### Relatório administrativo

O endpoint `GET /api/admin/financial-report` exige um token Bearer. Configure `ADMIN_API_TOKEN` no ambiente antes de iniciar a aplicação e envie `Authorization: Bearer <token>`. Sem token configurado, o endpoint responde `503`; sem credencial ou com credencial inválida, responde `401`.

`PORT` e `DATABASE_PATH` também podem ser definidos por ambiente. Por padrão, a API usa a porta `3000` e SQLite em memória.
