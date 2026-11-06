# task-manager-api

API de Task Manager em Python/Flask usada como entrada do desafio `refactor-arch`. Diferente dos outros projetos, este já possui alguma separação de camadas (`models/`, `routes/`, `services/`, `utils/`), mas ainda contém problemas arquiteturais e de qualidade.

## Como rodar

```bash
pip install -r requirements.txt
python seed.py
python app.py
```

A aplicação sobe em `http://localhost:5000`. O `seed.py` popula o banco SQLite (`tasks.db`) com usuários, categorias e tasks de exemplo — **rode-o antes do primeiro boot**, caso contrário os endpoints vão retornar listas vazias.

## Security configuration

The API now requires a configured `TASK_MANAGER_SECRET_KEY` before login can issue a token or protected resources can be accessed. Set it to a randomly generated value in the process environment; never commit it. `SMTP_USER` and `SMTP_PASSWORD` are also read from the environment when email notifications are used. Without SMTP credentials, sending is disabled.

`POST /login` returns a signed, expiring bearer token. Send it as `Authorization: Bearer <token>` to task, user, report, and category endpoints. Those routes currently require an authenticated admin identity; missing or invalid credentials return 401, a non-admin identity returns 403, and a missing signing secret fails closed with 503. `/` and `/health` remain public. The password field is no longer returned by user serialization.

Existing MD5 password hashes are upgraded to Werkzeug password hashes after a successful login. Dormant accounts retain their legacy hash until they authenticate. The sample seed data uses demo passwords and is for local development only; `seed.py` deletes existing rows, so do not run it against production data.

Example PowerShell setup:

```powershell
$env:TASK_MANAGER_SECRET_KEY = python -c "import secrets; print(secrets.token_urlsafe(48))"
python seed.py
python app.py
```
