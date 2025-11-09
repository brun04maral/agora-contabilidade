# 📋 PLANO DE IMPLEMENTAÇÃO - ORÇAMENTOS

## 🎯 Visão Geral

Sistema de orçamentos integrado com Projetos e Equipamento.

---

## 📊 INFORMAÇÃO RECOLHIDA

### Estrutura de Dados

**Orçamento tem:**
- ID (ex: #O0001) - não "Número"
- Cliente
- Descrição/Título
- Valor total
- Data de criação
- Data de validade
- Estado (PENDENTE / APROVADO / REJEITADO / EXPIRADO)
- Lista de equipamentos (item a item)
- Notas internas

**2 Tipos de Orçamento:**
1. **BACKEND** (interno) - com breakdown de equipamento, custos reais
2. **FRONTEND** (para cliente) - versão limpa para apresentação
- São independentes mas valor total tem de bater certo

### Estados do Orçamento

- `PENDENTE` - Criado, aguarda resposta do cliente
- `APROVADO` - Cliente aprovou → cria projeto automaticamente
- `REJEITADO` - Cliente rejeitou
- `EXPIRADO` - Prazo de validade passou

### Integração com Projetos

**Quando orçamento é APROVADO:**
- ✅ Cria automaticamente um projeto com os mesmos dados
- ✅ Projeto mantém referência ao orçamento original
- ✅ Orçamento pode ser editado depois
- ✅ Edição do orçamento também edita o projeto associado

### Integração com Equipamento

**Equipamento:**
- Aba EQUIPAMENTO existe no Excel (para importar)
- Cada equipamento tem valor base de aluguer (na DB)
- No orçamento, inserimos item a item de equipamento
- Estipulamos manualmente quanto € do orçamento vai para aquele equipamento
- **Amortização NÃO é automática** - nós definimos o valor

**Funcionalidades:**
- Poder duplicar orçamentos (facilita orçamentos parecidos)
- Lista de equipamentos por orçamento

### Dados no Excel

- ✅ Existe aba EQUIPAMENTO no Excel atual
- ✅ Existe outro Excel com orçamentos (separado)

---

## 🚀 PLANO DE IMPLEMENTAÇÃO (FASES)

### FASE 1: Equipamento (Base)
1. Criar modelo `Equipamento` na DB
2. Importar aba EQUIPAMENTO do Excel
3. Criar tela CRUD de Equipamento
4. Testar e validar

### FASE 2: Orçamentos Backend (Interno)
1. Criar modelo `Orcamento` na DB
2. Criar modelo `OrcamentoEquipamento` (relação N:N)
3. Criar tela de listagem de Orçamentos
4. Criar formulário de criação (com equipamentos)
5. Implementar estados (PENDENTE/APROVADO/REJEITADO/EXPIRADO)
6. Testar criação manual

### FASE 3: Integração Orçamento → Projeto
1. Quando estado = APROVADO, criar projeto automaticamente
2. Manter referência projeto ↔ orçamento
3. Sincronizar edições orçamento → projeto
4. Testar conversão

### FASE 4: Orçamento Frontend
1. Criar modelo `OrcamentoFrontend`
2. Ligar ao OrcamentoBackend
3. Validar que valores totais batem certo
4. Gerar PDF/export para cliente

### FASE 5: Features Avançadas
1. Duplicar orçamentos
2. Cálculo automático de totais
3. Relatórios de amortização
4. Import de orçamentos do Excel externo

---

## 📝 NOTAS IMPORTANTES

- **ID não Número** - já foi alterado em todas as tabelas
- Orçamentos backend e frontend são independentes
- Valores têm de bater certo entre os dois
- Equipamento tem valor base de aluguer
- Amortização é manual (nós estipulamos)

---

*Criado: 08/11/2025*
*Status: Planeamento*
