# Architecture Audit Report

================================ ARCHITECTURE AUDIT REPORT ================================
Project: task-manager-api
Stack:   Python 3.13.14; Flask 3.0.0; Flask-SQLAlchemy 3.1.1; SQLAlchemy 2.1.8; Flask-Cors 4.0.0
Files:   14 source/config/documentation files read | lines of code not measured

## Summary
CRITICAL: 1 | HIGH: 2 | MEDIUM: 4 | LOW: 2

## Findings

### [CRITICAL] User serialization exposes password hashes
File: models/user.py:16-25; routes/user_routes.py:27-40
Description: `User.to_dict()` includes the stored password hash. `get_user` uses this serializer and returns it from the unauthenticated `/users/<user_id>` endpoint. `GET /users` also exposes user records without authentication (its separate serializer omits password).
Impact: Any caller can collect password hashes and attempt offline recovery; user data is exposed without identity verification.
Recommendation: Remove password material from every public serializer. Put authentication and authorization at the route boundary before exposing user records; preserve intended response fields only after documenting the contract.

### [HIGH] Hardcoded signing key and SMTP credential
File: app.py:11-13; services/notification_service.py:7-10,15-19
Description: A fixed Flask `SECRET_KEY` is used by the application, and the notification service logs into an SMTP account using a credential embedded in source. These are active configuration values, not environment lookups.
Impact: Anyone with repository access can reuse the signing key and SMTP credential; compromise can enable forged signed state or unauthorized mail access. Flask documentation requires a long random secret and warns against committing it.
Recommendation: Load secrets from validated environment/secret storage, rotate exposed values, and retain only non-sensitive defaults. The existing SMTP integration's configuration behavior must be preserved.

### [HIGH] Passwords use unsalted MD5
File: models/user.py:27-32
Description: `set_password` and `check_password` use MD5 directly with no salt or work factor.
Impact: A database disclosure enables fast offline guessing, placing all user credentials at risk.
Recommendation: Use a password hashing API designed for passwords (for example Werkzeug's supported password hashing helpers) and plan a compatible migration/rehash path for existing hashes.

### [MEDIUM] Route handlers contain business logic and persistence
File: routes/task_routes.py:85-154,156-223; routes/user_routes.py:42-90,92-151; routes/report_routes.py:12-101,103-155,167-223
Description: Route functions validate domain rules, query related records, mutate models, commit/rollback sessions, aggregate reports, and format response payloads directly. This responsibility is repeated across task, user, and category flows.
Impact: Changes to domain rules and persistence are coupled to HTTP behavior, increasing inconsistency and making isolated tests difficult.
Recommendation: Keep routes as boundary adapters and move use cases/data access to controllers/services and models, preserving paths, status codes, response shapes, and transaction effects.

### [MEDIUM] N+1 database access in collection/report routes
File: routes/task_routes.py:14-16,41-55; routes/user_routes.py:12-24; routes/report_routes.py:53-68,157-165
Description: Task list fetches all tasks then performs separate user/category lookups per task. User list traverses each user's task relationship, and summary report issues a task query for every user; category list similarly counts tasks per category.
Impact: Query count grows with returned entities and can cause slow responses as datasets grow.
Recommendation: Use eager loading, grouped aggregate queries, or joins and verify returned JSON remains equivalent.

### [MEDIUM] Deprecated naive UTC API is used throughout the application
File: app.py:24; models/task.py:15-16,52; routes/task_routes.py:31,72,136,203,285; routes/report_routes.py:35,42,45,71,133; services/notification_service.py:35; utils/helpers.py:38,45,48
Description: `datetime.utcnow()` is used across timestamps, date validation, task overdue checks, and reports. The observed Python runtime is 3.13.14, and the Python 3.13 official documentation marks this API deprecated since 3.12 and recommends `datetime.now(UTC)`.
Impact: Runtime warnings and continued dependence on naive UTC timestamps make timezone behavior less explicit and may complicate future Python upgrades. Effective behavior/storage compatibility must be checked before changing timestamp semantics.
Recommendation: Replace with timezone-aware UTC consistently, review SQLite/model comparison compatibility, and verify serialized timestamps and endpoint contracts.
### [MEDIUM] Validation and error handling are inconsistent at HTTP boundaries
File: routes/task_routes.py:87-114,151-154,162-223,240-271; routes/user_routes.py:44-65,92-132; routes/report_routes.py:169-209
Description: Payload fields are used with assumptions about type/shape (for example `len(title)` and `int(priority)`), while exception handling varies between bare catches, broad catches, and no handling. Invalid query values can raise before a structured response; update category dereferences parsed JSON without checking it.
Impact: Malformed input can produce inconsistent failures and unexpected 500 responses, and broad catches conceal operational causes.
Recommendation: Validate request schemas at the boundary and centralize exception-to-response translation while preserving existing intentional status/body contracts.

### [LOW] Ambiguous abbreviated names obscure domain roles
File: routes/task_routes.py:16-17,50-55; routes/report_routes.py:33,55-61,159-164; seed.py:65-90
Description: Names such as `t`, `cat`, `c`, `u`, and `td` are used for task, category, user, and task-data objects across nontrivial loops and mutation logic.
Impact: Readers must repeatedly infer domain roles while tracing aggregation and persistence flows.
Recommendation: Use descriptive names such as `task`, `category`, `user`, and `task_data` in the approved refactor.

### [LOW] Repeated status and priority literals encode unnamed domain rules
File: routes/task_routes.py:32,73,110,177,286; routes/report_routes.py:19-28,36,48-50,120-129; models/task.py:38-48
Description: Task states and priority bounds are embedded repeatedly as string/integer literals even though `utils/helpers.py:110-116` already defines partial constants for related rules.
Impact: A domain change can leave comparisons or validation limits inconsistent, and the existing constants do not centralize all consumers.
Recommendation: Define a single domain-level set of status/priority values and use it consistently in validation, aggregation, and reporting.

================================ Total: 9 findings ================================

## Phase 1: Project analysis

- Language/runtime: Python source; runtime observed as Python 3.13.14.
- Framework: Flask is imported and configured; requirements declare Flask 3.0.0. Resolved versions were read inside a disposable Python 3.13.14 container after installing the declared requirements; the workspace was mounted read-only and source copied to the container filesystem.
- Dependencies: requirements declare Flask-SQLAlchemy 3.1.1, Flask-Cors 4.0.0, marshmallow 3.20.1, requests 2.31.0, python-dotenv 1.0.0. Only Flask, Flask-SQLAlchemy, and Flask-Cors imports were observed in inspected source. Marshmallow, requests, and dotenv use was not confirmed.
- Domain/persistence: task manager with users, categories, tasks, SQLite through Flask-SQLAlchemy. Model tables declared: `tasks`, `users`, `categories`; `app.py` invokes `db.create_all()` at import/boot. No migrations found.
- Architecture: partial layers (`models/`, `routes/`, `services/`, `utils/`) but route modules mix HTTP, domain rules, serialization, and database access. `app.py` is composition and boot entry point.
- Interfaces: `/`, `/health`; task CRUD/search/stats; user CRUD/tasks/login; summary and per-user reports; category CRUD. Exact methods are registered in the route decorators. Interface responses were not exercised.
- Inventory: 17 project files listed by `rg --files` excluding generated artifacts; 14 source/config/documentation files were read in detail (app.py, database.py, 3 model modules, 3 route modules, notification service, helpers, seed.py, README.md, requirements.txt). Small package `__init__.py` files were inventoried but not read in detail. `__pycache__` and compiled files were excluded. No test files, lockfile, project build manifest, or migration directory were found.
- Database tables: three model tables above; live schema was not inspected.

## Coverage, baseline, and limitations

Static review used file inventory, targeted symbol searches, and line-numbered reads of 14 files. `git status --short` showed pre-existing untracked `.agents/` directories; these were not modified. No reports directory existed before this audit.

Baseline commands/results:
- `python --version`: Python 3.13.14.
- `python -m pip show ...`: packages absent from the host environment. In a disposable Docker container, installed requirements resolved to Flask 3.0.0, Flask-SQLAlchemy 3.1.1, SQLAlchemy 2.1.8, Flask-Cors 4.0.0, marshmallow 3.20.1, requests 2.31.0, python-dotenv 1.0.0.
- `docker info --format '{{.ServerVersion}}'`: initial sandbox attempt was denied; approved elevated retry succeeded (Docker 29.8.2).
- `seed.py` was not run because it deletes existing task/user/category rows before repopulating SQLite. Disposable container command installed requirements, copied the read-only mounted workspace into `/tmp/audit-app`, imported the app (creating tables in container-only SQLite), and used Flask test client. Boot/import succeeded. GET results: `/` 200, `/health` 200, `/tasks` 200, `/tasks/1` 404, `/tasks/search` 200, `/tasks/stats` 200, `/users` 200, `/users/1` 404, `/users/1/tasks` 404, `/reports/summary` 200, `/reports/user/1` 404, `/categories` 200. `/login` and `/categories/1` returned 405 on GET because those routes do not register GET. POST/PUT/DELETE routes were not exercised in this read-only baseline.

Deprecated API review: `datetime.utcnow()` locations and the Python 3.13 deprecation are recorded as the MEDIUM finding above. The official replacement is `datetime.now(UTC)` (Python docs: https://docs.python.org/3.13/library/datetime.html).

Flask-SQLAlchemy 3.1.1's query interface is documented as legacy with a preference for `session.execute(select(...))` (https://flask-sqlalchemy.palletsprojects.com/en/stable/legacy-query/). The disposable environment resolved SQLAlchemy 2.1.8. This remains a legacy API risk, not a separate version-specific deprecation finding.

Official references checked:
- Python 3.13 `datetime`: https://docs.python.org/3.13/library/datetime.html
- Flask-SQLAlchemy legacy query interface: https://flask-sqlalchemy.palletsprojects.com/en/stable/legacy-query/
- Flask secret-key configuration: https://flask.palletsprojects.com/en/stable/config/

## Suspicions not confirmed

- Notification service hardcoded SMTP account appears illustrative; whether it authenticates successfully or belongs to a real account was not tested. Its embedded credential is nevertheless active configuration and should be treated as exposed.
- SQLAlchemy 2.1.8 `Query` API is documented as legacy; no runtime warning was observed or assessed.

## Proposed Phase 3 plan

1. Introduce `src/config/settings.py` and a composition root while preserving SQLite default and current routes; remove committed secrets and configure them externally (credential rotation needed outside code).
2. Move route orchestration/business logic to controllers and service/model operations; keep `src/views/routes.py` limited to request/response mapping.
3. Remove password hashes from public serialization and replace MD5 with a password-hashing mechanism. This changes the existing `/users/<id>` response by removing `password`; security requires an explicitly documented contract change, so implementation of that response change needs specific approval before Phase 3.
4. Centralize error handling and request validation, preserving documented response contracts where possible.
5. Replace deprecated `datetime.utcnow()` with timezone-aware UTC consistently and assess SQLite storage compatibility.
6. Optimize relationship/report collection queries; expand domain constants and descriptive names.
7. After approval, verify tests, boot, and each original route against a safe baseline. The disposable baseline covered boot and GET routes; mutating methods remain to be checked after approval.

## Phase 2 status

Complete. Dependency versions, app import/boot, and the registered GET interface were checked in a disposable Docker container. POST/PUT/DELETE behavior was not exercised in the baseline; Phase 3 will compare those routes after approval. The workspace was mounted read-only during execution. No application source files were changed.





================================ PHASE 3: REFACTORING INCOMPLETE ================================

## New Project Structure

```text
app.py                              compatibility entry point
src/
  app.py                            application factory/composition root
  config/settings.py               environment-backed settings
  models/{task,user,category}_model.py and constants.py
  views/routes.py                  blueprint composition and access guards
  views/{task,user,report}_routes.py thin HTTP adapters
  views/validation.py              request-boundary validation
  controllers/{task,user,report,auth}_controller.py use-case coordination
  services/{task,user,report,auth}_service.py business/data operations
  services/clock.py                UTC clock helper
  middlewares/{auth,error_handler}.py
  errors.py                         safe service error type
routes/*.py and models/*.py         compatibility import shims
services/notification_service.py   environment-backed email integration
utils/
```

## Validation

- `python -m compileall -q src routes app.py seed.py` succeeded in the Docker run. Afterward, unused imports were removed and the same compile command succeeded on the host.
- Final Flask test-client matrix passed 30 scenarios across boot, auth, task/user/category CRUD, search, reports, and malformed inputs.
- Missing/invalid auth returned 401; invalid fields/query returned 400; CRUD returned expected 200/201; valid login returned 200 and invalid login 401. Prior checks confirmed non-admin 403, missing secret 503, password omission, and persisted legacy password upgrade.
- Workspace was read-only in Docker, application data used an in-memory SQLite database, and the seed script was not run.
- Eight of nine findings are resolved. The HIGH secret finding remains partial until external credential rotation is confirmed.

## Changes made

- Established an active MVC layout under `src/`: `views/` owns HTTP adapters and input validation; `controllers/` coordinates use cases; `services/` owns queries, domain rules, and persistence; `models/` owns ORM models; `config/` owns environment-backed settings; `middlewares/` translates errors and enforces access. Root `routes/*.py` and `models/*.py` remain compatibility shims.
- Extracted task CRUD, search, statistics, user CRUD/reports, category CRUD, and aggregate reports to services and controllers. Active views no longer access ORM models or the database session.
- Added shared request-boundary validation for JSON object shape and known field types, plus integer query parameters. Invalid input is translated by the central error handler to HTTP 400.
- Added centralized translation for service transaction failures and unexpected errors. Services roll back failed writes and raise safe operation errors; the middleware serializes them without exposing internal exception details.
- Kept the approved fail-closed admin bearer-token policy for task, user, report, and category APIs; `/login`, `/`, and `/health` remain public. Password hashes remain excluded from serialization, and legacy MD5 credentials upgrade to Werkzeug hashes after successful login.
- Kept credentials in environment settings and SMTP sends disabled without configured credentials. Rotation of previously embedded values in any external provider was not performed.
- Replaced deprecated UTC calls, retained the existing naive SQLite timestamp representation, kept eager/grouped collection queries, and centralized status, role, priority, title/password limit, and category color constants.

## Verification commands and results

- Disposable Docker container: `python:3.13.14-slim`; dependencies installed from `requirements.txt`; workspace bind-mounted read-only and copied into the container; database configured in-memory.
- `python -m compileall -q src routes app.py seed.py` completed successfully in the final container run.
- Flask test client passed 30 scenarios: root/health; missing and invalid bearer token; task list/create/read/update/search/stats/delete; task invalid field and query rejection; user create/list/read/tasks/update/delete; invalid user field rejection; category create/list/update/delete and invalid field rejection; summary and user report; missing user report; valid and invalid login.
- Observed expected status codes: public health/root 200; unauthorized access 401; CRUD success 200/201; malformed inputs 400; absent report user 404; valid login 200 and invalid login 401. Earlier checks also confirmed non-admin access 403, missing signing secret 503, password omission, and persisted MD5-to-Werkzeug upgrade.
- No repository test suite was present. No project SQLite file or seed data was used; all endpoint data was isolated to the container.

## Traceability matrix

| Finding / severity | Original impact and location | Approved scope | Current location and evidence | State |
|---|---|---|---|---|
| User serialization exposes password hashes — CRITICAL | Hash returned from `models/user.py:16-25` through `routes/user_routes.py:27-40` | Remove hash from public serialization and fail closed on sensitive routes | `src/models/user_model.py:20-28`; admin guard in `src/middlewares/auth.py:18-38`; final endpoint run confirmed protected requests and previous response check confirmed no `password` field | resolved |
| Hardcoded signing key and SMTP credential — HIGH | Embedded values in `app.py:11-13` and `services/notification_service.py:7-10,15-19` | Move secrets to environment and rotate exposed values | `src/config/settings.py:6,11-12`; notification service reads settings and skips send when credentials are missing. External rotation was not performed or verified | partial |
| Unsalted MD5 passwords — HIGH | `models/user.py:27-32` | Strong password hashing with compatibility migration | `src/models/user_model.py:31-43`; `src/services/auth_service.py:10-22`; prior disposable-container check confirmed successful legacy login persisted a Werkzeug hash | resolved |
| Route handlers contain business logic and persistence — MEDIUM | `routes/task_routes.py:85-223`, `routes/user_routes.py:42-151`, `routes/report_routes.py:12-223` | Extract service/model responsibilities and keep HTTP adapters thin | Root `routes/*.py` now re-export blueprints. Active handlers in `src/views/task_routes.py:7-40`, `src/views/user_routes.py:7-41`, `src/views/report_routes.py:7-36` call controllers; ORM and commits are in `src/services/task_service.py`, `user_service.py`, and `report_service.py`. Static search found no database access in views/controllers; endpoint matrix passed | resolved |
| N+1 database access — MEDIUM | Task/user/report/category collections in original route locations listed above | Eager loading and grouped queries | `src/services/task_service.py:16` uses eager relationships; `user_service.py:15-16` groups task counts; `report_service.py:49-60` aggregates loaded tasks and `147-152` groups category counts; collection endpoints passed | resolved |
| Deprecated `datetime.utcnow()` — MEDIUM | Original locations listed in the Phase 2 finding | Use supported UTC API without changing stored timestamp semantics | `src/services/clock.py:4`; static search found no `datetime.utcnow()`; final compile and endpoint run passed | resolved |
| Inconsistent boundary validation/error handling — MEDIUM | Duplicated checks and broad catches in original route files listed above | Validate at the HTTP boundary and centralize safe error translation | `src/views/validation.py:21-58`; `src/middlewares/error_handler.py:8-28`; `src/errors.py:1-2`; final run confirmed malformed task/user/category fields and search integers return 400 | resolved |
| Ambiguous abbreviated names — LOW | Original task/report routes and `seed.py` locations listed in the Phase 2 finding | Use descriptive domain names | Active code uses `category_id`, `category_data`, `task_data`, `user_task_statistics`, and descriptive controller/service names; static search found no `cat_id`/`cat_data` remnants | resolved |
| Repeated status/priority literals — LOW | Original route/model/helper locations listed in the Phase 2 finding | Centralize domain values and limits | `src/models/constants.py:1-22` defines statuses, roles, priorities, limits, and defaults; services, models, auth middleware, and seed use the constants. Static search found no duplicated title/password bounds or role defaults in active code | resolved |

## Remaining work and final reconciliation

Initial findings: 9. Resolved: 8. Partial: 1. Pending: 0. The approved code refactor and all applicable checklist items are implemented and verified. Phase 3 remains **incomplete** because the external rotation portion of the HIGH credential finding is unresolved. If the old embedded values were used in an environment, an operator must rotate them in the relevant secret provider; this repository does not have access to that provider. The access contract change remains intentional and approved: sensitive APIs require an admin bearer token, missing/invalid credentials return 401, non-admin credentials return 403, and missing signing-key configuration returns 503.