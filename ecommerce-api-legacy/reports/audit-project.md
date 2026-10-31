# PHASE 1: PROJECT ANALYSIS

Language: JavaScript (Node.js v24.18.0)
Framework: Express 4.22.1, resolved by package-lock.json
Dependencies: Express 4.22.1; sqlite3 5.1.7
Domain: LMS API with checkout, courses, payments, enrollments and financial report
Architecture: Original Express entry point in src/app.js; original AppManager combined routes, business logic and persistence; SQLite in memory
Source files: 3 application source files examined; 4 supporting files also examined
DB tables: users, courses, enrollments, payments, audit_logs

Coverage and method: repository inventory with rg --files; full reading of three original JavaScript sources, package.json, README.md, api.http and relevant package-lock.json entries. No tests, Dockerfile or Compose file were found. Skill files and Git metadata were excluded from the count.

# ARCHITECTURE AUDIT REPORT

Project: ecommerce-api-legacy  
Stack: JavaScript, Node.js 24.18.0, Express 4.22.1, sqlite3 5.1.7  
Files: 3 source files analyzed | LOC not measured

## Summary
CRITICAL: 0 | HIGH: 4 | MEDIUM: 4 | LOW: 0

## Findings

### [HIGH] Administrative route has no authentication or authorization
File: original src/AppManager.js:80-129
Description: GET /api/admin/financial-report was registered without middleware or identity/permission checks.
Impact: A client reaching the API can retrieve revenue and student data.
Recommendation: Define and apply administrative authentication and authorization. The identity provider and access policy are not specified, and this behavior change remains pending.

### [HIGH] Password stored through predictable truncated transformation
File: original src/utils.js:17-23; original src/AppManager.js:66-70
Description: badCrypto repeated two Base64 characters and truncated the result to ten characters before storage.
Impact: Stored passwords were predictable and collisions likely.
Recommendation: Use salted password derivation. Implemented with Node.js scrypt for newly created users; the in-memory database is reseeded at boot, and there is no persistent migration path in this project.

### [HIGH] Controller combined routing, domain logic and persistence
File: original src/AppManager.js:25-138
Description: setupRoutes mixed input validation, checkout, payment decisions, persistence, financial reporting and HTTP responses.
Impact: Coupled responsibilities made rules and failure paths difficult to test in isolation.
Recommendation: Separate routes, controller, model, configuration and error handling. Implemented under src/.

### [HIGH] Checkout logged the complete payment card number
File: original src/AppManager.js:45
Description: The checkout log interpolated the complete card value into the application log.
Impact: Anyone with access to application logs could retrieve payment card data.
Recommendation: Avoid logging sensitive card data. Implemented by logging only a masked value with the last four digits visible.

### [MEDIUM] Financial report performed N+1 queries
File: original src/AppManager.js:83-125
Description: The report queried enrollments per course and then user and payment per enrollment.
Impact: Query count grew with courses and enrollments.
Recommendation: Fetch related data in a JOIN and aggregate in memory. Implemented in src/models/lms_model.js.

### [MEDIUM] Database errors were ignored on some paths
File: original src/AppManager.js:57-60, 92-107, 133-135
Description: Report and deletion paths ignored database errors; audit-log errors were also ignored.
Impact: A failed report/delete could appear successful or return incomplete data.
Recommendation: Handle query failures centrally while keeping normal contracts. Report and delete failures now return 500; audit-log failure is logged while checkout success remains unchanged, matching original success behavior.

### [MEDIUM] Shared mutable global cache
File: original src/utils.js:9-15, 25
Description: A module-level object was mutated by checkout across requests.
Impact: State had process-wide lifetime and no explicit ownership or expiry.
Recommendation: Scope the cache to the composed app/controller. Implemented as an injected Map instance, no longer module-global.

### [MEDIUM] Locked dependency graph contains security advisories
File: package-lock.json:1028-1035 (qs 6.14.3); package-lock.json:1302-1314 (sqlite3 6.0.1)
Description: npm audit initially reported 17 advisories (2 critical, 8 high, 5 moderate, 2 low). Compatible fixes reduced this to 12; after the approved sqlite3 6.0.1 major upgrade and native rebuild, the final audit reports one moderate advisory in qs 6.14.3. Express 4.22.1 constrains qs to ~6.14.0; npm audit fix did not move that copy. The sqlite3 upgrade removed the critical and high findings.
Impact: One transitive query-string package remains in an advisory range. The advisory relates to crafted qs stringify inputs; the project does not directly call qs stringify, but the package is part of Express's dependency graph.
Recommendation: Keep the major sqlite3 update. Resolve the remaining qs advisory through a compatible Express update or an explicitly validated override; neither was made because Express pins the current range and query parsing behavior must be preserved.

================================ Total: 8 findings ================================

## Baseline and dependency verification

The original baseline was captured before changes using npm start and HTTP calls against the seeded in-memory database:

- GET /api/admin/financial-report → 200 with seeded courses, revenue and students.
- POST /api/checkout with a declined card → 400, "Pagamento recusado".
- POST /api/checkout with an approved card → 200, {"msg":"Sucesso","enrollment_id":2}; the subsequent report showed the new enrollment and revenue.
- DELETE /api/users/1 → 200 with the original Portuguese message; related enrollment/payment rows remained.
- The original report's course array order varied between runs because results were collected from asynchronous callbacks. The refactor orders by descending course id to match the captured baseline response.

Installed dependencies from the lockfile with npm ci. npm initially could not verify the proxy certificate; using Node's system certificate store succeeded. The npm install-scripts approval for sqlite3 is recorded in package.json; npm rebuild sqlite3 succeeded using the system certificate store. Compatible dependency fixes were applied, then the user approved sqlite3 6.0.1; package.json and package-lock.json now resolve that major. The final npm audit reports one moderate qs advisory.

The project uses express.json(), Express route methods, and sqlite3 Database, serialize, run, get and all. Express 4's official docs document express.json(); no deprecated API method was confirmed in use. The sqlite3 project marks the library itself deprecated/unmaintained. Official sources: https://expressjs.com/en/4x/api/express/ ; https://expressjs.com/4x/api/ ; https://github.com/TryGhost/node-sqlite3 ; https://github.com/TryGhost/node-sqlite3/wiki/API .

## PHASE 3: REFACTORING BLOCKED

### New project structure

```text
src/
├── config/settings.js
├── models/lms_model.js
├── views/routes.js
├── controllers/lms_controller.js
├── middlewares/error_handler.js
├── services/password_hasher.js
└── app.js (composition root and executable entry point)
```

The previous src/AppManager.js and src/utils.js were removed after their responsibilities were moved to MVC modules above. The declared package entry point and start command remain src/app.js and node src/app.js.

### Validation

✓ Application boots without errors (npm start; Node 24.18.0, Express 4.22.1 and sqlite3 6.0.1 after native rebuild)
✓ Original endpoints respond correctly for captured baseline scenarios: GET financial report 200, declined checkout 400, approved checkout 200 with enrollment_id 2, DELETE user 200. Seeded report contents and checkout effects matched; course order matches the captured baseline after ordering by descending course id.
✓ Six of the seven code findings were resolved or handled as described above. Administrative authentication remains unresolved pending an explicit identity/access policy. The sqlite3 major upgrade is complete; one moderate qs advisory remains.

Additional verification: node --check succeeded for all seven JavaScript files under src. An invalid-course checkout returned 404 with "Curso não encontrado"; missing required input returned the original 400 "Bad Request" behavior. Database failures were not injected or exercised.

## Remaining decisions and risks

1. Specify the identity mechanism and access policy for GET /api/admin/financial-report before adding authentication; it changes who may access the route.
2. Decide whether to accept the remaining moderate qs advisory or approve a compatible Express upgrade/validated qs override. The final audit found one advisory; runtime impact in this application's JSON routes was not demonstrated.
3. npm reports deprecated install/build dependencies; sqlite3 itself is deprecated upstream. No schema changes or persistent database migration were performed; this application creates an in-memory database at every start.
