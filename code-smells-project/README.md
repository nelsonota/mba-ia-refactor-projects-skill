# code-smells-project

API de e-commerce em Python/Flask.

## Como rodar

```bash
pip install -r requirements.txt
```

Defina `SECRET_KEY` e `ADMIN_TOKEN` com valores aleatórios e privados antes de iniciar o servidor. No PowerShell, por exemplo:

```powershell
$env:SECRET_KEY = "<valor aleatório forte>"
$env:ADMIN_TOKEN = "<token administrativo aleatório>"
$env:FLASK_DEBUG = "false"
python app.py
```

A aplicação sobe em `http://localhost:5000`. O entry point compatível `app.py` compõe a aplicação implementada em `src/`. O banco SQLite (`loja.db`) é criado automaticamente na primeira requisição, já com produtos e usuários de exemplo. Senhas legadas são convertidas para hashes na primeira conexão, e senhas não são incluídas nas respostas de usuário. Configure `DATABASE_PATH` para escolher outro arquivo SQLite. O antigo endpoint de SQL arbitrário `/admin/query` foi removido. `/admin/reset-db` exige `Authorization: Bearer <ADMIN_TOKEN>`.
