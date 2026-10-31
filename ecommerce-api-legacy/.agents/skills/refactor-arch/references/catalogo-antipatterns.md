# Catálogo de anti-patterns

Classifique pelo impacto demonstrado e contexto, não apenas pelo nome do padrão. Cada sinal é uma pista a investigar, não prova automática. Registre evidência e linhas dos trechos responsáveis; não inclua segredos no relatório.

| Anti-pattern | Severidade típica | Sinais e evidência a procurar |
|---|---|---|
| Credenciais hardcoded | CRITICAL | Segredo real embutido em código/configuração versionada e usado para acessar recurso; diferencie placeholders. Nunca reproduza o valor. |
| SQL injection | CRITICAL | Entrada não confiável interpolada em SQL executado sem parâmetros; rastreie origem até execução. |
| God Class ou arquivo monolítico | CRITICAL quando a separação é completamente violada; senão HIGH | Um mesmo componente executa roteamento, regras complexas e persistência; aponte trechos de cada responsabilidade. |
| Controller pesado | HIGH | Tratador implementa regras extensas ou consultas em vez de coordenar operações; identifique responsabilidade e fluxo. |
| Acoplamento rígido | HIGH | Dependências concretas criadas dentro do fluxo impedem substituição e testes; confirme o impacto em vez de exigir um container de DI. |
| Estado global mutável | HIGH quando compartilhado amplamente | Escritas e leituras de estado global entre requisições ou módulos criam interferência; identifique os acessos. |
| Duplicação de regras | MEDIUM | Mesma regra não trivial replicada em fluxos distintos e sujeita a divergência; cite cada localização. |
| Consultas N+1 | MEDIUM | Consulta por item dentro de iteração além da consulta inicial; confirme caminho e mecanismo de acesso. |
| Validação ausente na fronteira | MEDIUM | Entrada externa chega a operações que exigem restrições sem validação equivalente em outra camada; demonstre consequência. |
| Tratamento de erros disperso | MEDIUM | Respostas inconsistentes ou detalhes internos expostos por tratadores duplicados; diferencie exposição sensível de inconsistência simples. |
| API deprecated | MEDIUM por padrão; ajuste por impacto | Uso de símbolo comprovadamente obsoleto na versão instalada. Confirme status, versão, substituto e compatibilidade na documentação oficial correspondente; cite fonte e linha de uso. Se não puder confirmar, registre como suspeita, não como fato. |
| Nomes ambíguos ou números mágicos | LOW | Nome impede compreender papel ou literal de domínio repetido sem explicação; cite uso e impacto. |

CRITICAL cobre falha grave de funcionamento, exposição de dados ou ausência completa de separação; HIGH, violações que dificultam muito manutenção e testes; MEDIUM, duplicação, padronização e performance moderada; LOW, legibilidade. Ajuste severidade diante de evidência concreta. Riscos não confirmados ficam separados dos achados.
