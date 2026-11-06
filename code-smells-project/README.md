# code-smells-project

API de E-commerce em Python/Flask usada como entrada do desafio `refactor-arch`.

## Como rodar

```bash
pip install -r requirements.txt
export ADMIN_TOKEN="<token seguro gerenciado fora do código>"
python app.py
```

A aplicação sobe em `http://localhost:5000`. O banco SQLite (`loja.db`) e as tabelas são criados no primeiro boot; os produtos de demonstração são mantidos. Contas de demonstração com senha conhecida não são criadas. Faça login para receber uma sessão assinada e criar pedidos apenas para essa conta ou consultar seus próprios pedidos. Configure `ADMIN_TOKEN` no ambiente para habilitar as rotas administrativas, relatórios e operações de escrita de produtos; sem ele, essas operações falham fechadas com HTTP 503. Envie o token no cabeçalho `X-Admin-Token`. O endpoint legado `POST /admin/query` está desativado e responde HTTP 410 quando autenticado; sem o token, retorna 503.

`SECRET_KEY` deve ser definida no ambiente para manter sessões válidas entre reinícios; se omitida, uma chave aleatória é gerada para a execução atual. Use `FLASK_DEBUG=true` apenas em desenvolvimento e `DATABASE_PATH` para escolher outro arquivo SQLite.

Para executar por um servidor WSGI, inicialize o banco uma vez com `flask --app src.app init-db` antes de iniciar o servidor.
