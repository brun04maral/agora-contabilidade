# 📝 TODO - Agora Media Contabilidade

## 🎯 Fase 1: Setup e Fundação
- [x] Estrutura de diretórios
- [x] README.md
- [x] .gitignore
- [x] requirements.txt
- [x] .env.example
- [x] main.py básico
- [ ] Primeiro commit no GitHub
- [ ] Conta Supabase criada
- [ ] Ambiente virtual Python
- [ ] Dependências instaladas

## 🗄️ Fase 2: Base de Dados
- [ ] Modelos SQLAlchemy:
  - [ ] Projeto (tipo: EMPRESA | PESSOAL_BRUNO | PESSOAL_RAFAEL)
  - [ ] Despesa (tipo: FIXA_MENSAL | PESSOAL_BRUNO | PESSOAL_RAFAEL | EQUIPAMENTO)
  - [ ] Boletim
  - [ ] Cliente
  - [ ] Fornecedor
  - [ ] Equipamento
- [ ] Conexão com Supabase
- [ ] Criar tabelas no Supabase
- [ ] Script de seed (dados iniciais)

## 🖥️ Fase 3: Interface Básica
- [ ] Janela principal com menu/sidebar
- [ ] Dashboard simples
- [ ] Navegação entre módulos
- [ ] Componentes reutilizáveis:
  - [ ] Botões customizados
  - [ ] Inputs de formulário
  - [ ] Tabelas/listas
  - [ ] Mensagens de sucesso/erro

## 📊 Fase 4: Módulos Principais

### Projetos
- [ ] Listar projetos
- [ ] Adicionar projeto
- [ ] Editar projeto
- [ ] Eliminar projeto
- [ ] Filtros (por tipo, estado, cliente)
- [ ] Pesquisa

### Despesas
- [ ] Listar despesas
- [ ] Adicionar despesa
- [ ] Editar despesa
- [ ] Eliminar despesa
- [ ] Filtros (por tipo, credor, estado)
- [ ] Associar a projetos

### ⭐ Saldos Pessoais (CRÍTICO!)
- [ ] Vista de saldo para Bruno
- [ ] Vista de saldo para Rafael
- [ ] Cálculo de INs:
  - [ ] Projetos pessoais
  - [ ] Prémios de projetos da empresa
  - [ ] Investimento inicial (histórico)
- [ ] Cálculo de OUTs:
  - [ ] Despesas fixas mensais ÷ 2
  - [ ] Boletins emitidos
  - [ ] Despesas pessoais excecionais
- [ ] Saldo = INs - OUTs
- [ ] Histórico mensal
- [ ] Breakdown detalhado
- [ ] Sugestão de valor de boletim
- [ ] Gráfico de evolução

### Boletins
- [ ] Listar boletins
- [ ] Emitir boletim (com sugestão automática)
- [ ] Marcar como pago
- [ ] Listagem por sócio
- [ ] Estados (Pendente | Pago)

### Clientes
- [ ] CRUD completo
- [ ] Histórico de projetos

### Fornecedores
- [ ] CRUD completo
- [ ] Classificações
- [ ] Áreas e funções

### Faturação
- [ ] Controlo de faturas emitidas
- [ ] Controlo de faturas recebidas
- [ ] Estados e alertas
- [ ] Vencimentos

### Equipamento
- [ ] Inventário
- [ ] Valor de investimento
- [ ] Data de compra

## 📈 Fase 5: Features Avançadas
- [ ] Dashboard com indicadores:
  - [ ] Saldo bancário
  - [ ] Saldos pessoais (destaque!)
  - [ ] Lucro da empresa
  - [ ] Faturado vs Despesas do mês
  - [ ] Alertas (faturas vencidas, sugestão de boletins)
- [ ] Relatórios customizados
- [ ] Exportar para Excel
- [ ] Análise de rentabilidade por sócio

## 🔌 Fase 6: Integrações (Futuro)
- [ ] TOConline API:
  - [ ] Importar faturas emitidas
  - [ ] Sincronizar clientes/fornecedores
  - [ ] Obter PDFs
- [ ] BizDocs (se possível):
  - [ ] Arquivo digital de documentos

## 🎨 Fase 7: Polimento
- [ ] Melhorias de UI/UX
- [ ] Temas (dark/light)
- [ ] Atalhos de teclado
- [ ] Validações robustas
- [ ] Mensagens de erro claras
- [ ] Loading states
- [ ] Confirmações de ações críticas

## 🧪 Fase 8: Testes e Otimização
- [ ] Testar todas as funcionalidades
- [ ] Performance
- [ ] Backup de dados
- [ ] Documentação de código

---

## 🏆 Prioridade Absoluta
1. **Módulo Saldos Pessoais** - Este é o core do sistema!
2. Projetos (com tipo pessoal/empresa)
3. Despesas (com tipo fixas/pessoais)
4. Boletins
5. Resto

---

**Última atualização**: 2025-01-20
