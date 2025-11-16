### ESTADO ATUAL: ORÇAMENTOS (16/11/2025)

- Implementada arquitetura v2.0 de orçamentos separando lado CLIENTE (proposta comercial) e lado EMPRESA (repartição interna)
- Secções fixas: Serviços, Equipamento (c/ subsecções), Despesas (sincronizadas CLIENTE→EMPRESA)
- Diálogos tabulares avançados para cada tipo de item (serviço, equipamento, transporte, refeição, outro). Campos variáveis por tipo.
- CRUD completo em ambos os lados: validação em tempo real de totais, feedback visual de diferença.
- Dialog especial de Comissões (auto-preenchido, % editável, sincronização automática)
- Total de Despesas sempre igual dos dois lados — bloqueio de aprovação caso não bata.
- Novo workflow: Aprovação só possível quando TOTAL_CLIENTE = TOTAL_EMPRESA.
- Testes completos com exemplos reais (multi-serviços, multi-despesas, equipamento próprio/terceiros, freelancers).
- Código legacy substituído — TODO antigo removido (planos estão em BUSINESS_LOGIC.md)

---

### ESTADO ATUAL: OUTRAS ÁREAS

- Sócios: página individual em desenvolvimento (BA/RR), migrations a decorrer
- Boletins: modelo itinerário e valores de referência já aplicados; a refatorar para novo esquema após sócios
- Despesas/Projetos: alinhados com estrutura tabular e interfaces UX

---

### PRÓXIMOS PASSOS
- Finalizar onboarding e tutoriais para novo fluxo de orçamentos (screenshots, casos de teste)
- Ajustar arquitetura do lado EMPRESA com opção de duplicação rápida/auto-população (para projetos recorrentes)
- Integração/exportação automática para TOConline/Excel (ficheiros de receitas/custos)
- Consolidar documentação técnica, diagrams e fluxograms
