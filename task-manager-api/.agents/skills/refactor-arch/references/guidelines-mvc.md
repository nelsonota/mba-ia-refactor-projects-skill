# Arquitetura MVC alvo

Organize a refatoração sob `src/` conforme a estrutura abaixo. Use os nomes de diretórios indicados; adapte nomes de arquivos e extensões à linguagem e ao domínio do projeto. Os arquivos de produto e usuário são exemplos de domínios, não exigências para aplicações de outros domínios.

```text
src/
├── config/settings.<ext>
├── models/
│   └── <domínio>_model.<ext>
├── views/
│   └── routes.<ext>
├── controllers/
│   └── <domínio>_controller.<ext>
├── middlewares/error_handler.<ext>
└── app.<ext> (composition root)
```

Adapte a implementação aos mecanismos do framework, mantendo essas responsabilidades e a estrutura solicitada. Se alguma exigência técnica concreta da stack impedir essa organização, registre a incompatibilidade e proponha a adaptação no plano da Fase 2 para aprovação antes de implementá-la.

- **Models:** representam dados e regras de domínio; abstraem acesso e persistência por modelos, repositórios ou mecanismos equivalentes. Não dependem de requisição HTTP nem formatação de resposta.
- **Views/Routes:** rotas associam interface e controller; views apresentam dados ou serializam respostas. Validam formato de entrada na fronteira conforme o framework, sem executar regras de negócio ou consultas.
- **Controllers:** recebem entrada validada, coordenam casos de uso e models e escolhem resposta ou view. Regras complexas pertencem ao domínio ou a serviços de aplicação; acesso a dados deve ser delegado.
- **Configuração:** centralize leitura e validação de configuração em módulo apropriado; injete valores e dependências na inicialização. Use ambiente ou gerenciador de segredos, nunca valores sensíveis embutidos; preserve defaults não sensíveis necessários ao comportamento.
- **Erros:** centralize tradução de erros para a interface usando mecanismo nativo (middleware, filtro ou equivalente). Preserve contratos existentes e não divulgue detalhes internos.
- **Entry point:** um ponto claro compõe configuração, dependências, rotas e inicialização; evite efeitos de boot ao importar módulos quando a stack permitir.

Serviços e repositórios adicionais podem apoiar essas camadas. Preserve caminhos, métodos, entradas, respostas, autorização, transações e efeitos observáveis; justifique qualquer mudança necessária de contrato e obtenha aprovação específica quando aplicável. Não mova dados nem altere schema sem avaliar compatibilidade e autorização.
