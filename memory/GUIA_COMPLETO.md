# 📚 Guia Completo - Agora Media Contabilidade

Sistema de gestão contabilística completo para Agora Media Production.

---

## 🚨 CORREÇÕES DE ERROS - ÚLTIMA ATUALIZAÇÃO

### ✅ Erros Corrigidos

1. **KeyError: 'saldo_final'** → ✅ CORRIGIDO (commit 5a699be)
   - Dashboard agora usa `'saldo_total'` corretamente

2. **AttributeError: 'EstadoDespesa' has no attribute 'PENDENTE'** → ✅ CORRIGIDO (commit 702e643)
   - Dashboard agora usa `ATIVO + VENCIDO` para despesas pendentes
   - EstadoDespesa tem: `ATIVO`, `VENCIDO`, `PAGO`

3. **"No route to host" (PostgreSQL)** → ✅ CORRIGIDO com scripts
   - `init_setup.py` força SQLite automaticamente
   - `check_integrity.py` detecta e avisa sobre configuração

### 🔧 Como Corrigir Erros

```bash
# 1. Pull das correções
git pull

# 2. Limpar e reconfigurar (resolve a maioria dos problemas)
python3 init_setup.py

# 3. Verificar integridade
python3 check_integrity.py

# 4. Executar aplicação
python3 main.py
```

---

## 📊 Estado Atual do Sistema

### ✅ COMPLETAMENTE IMPLEMENTADO (MVP Fase 1)

#### 1. Dashboard
- Saldos pessoais em tempo real
- Estatísticas de projetos (Total, Recebidos, Faturados, Não Faturados)
- Estatísticas de despesas (Total, Pagas, Pendentes)
- Estatísticas de boletins (Total, Pagos, Pendentes)
- Contadores de clientes e fornecedores
- Interface responsiva com cards coloridos

#### 2. Saldos Pessoais (CORE)
- Cálculo automático para Bruno e Rafael
- Breakdown detalhado de INs e OUTs
- Visualização lado a lado
- Botão de atualizar

#### 3. Projetos
- Criar, editar, apagar projetos
- Filtrar por tipo (EMPRESA, PESSOAL_BRUNO, PESSOAL_RAFAEL)
- Filtrar por estado (NÃO_FATURADO, FATURADO, RECEBIDO)
- Gestão de clientes
- Gestão de prémios
- Numeração automática (#P0001)

#### 4. Despesas
- Criar, editar, apagar despesas
- 5 tipos diferentes (FIXA_MENSAL, PESSOAL_BRUNO, PESSOAL_RAFAEL, EQUIPAMENTO, PROJETO)
- 3 estados (ATIVO, VENCIDO, PAGO)
- Marcar como pago
- Associar a fornecedores e projetos
- Numeração automática (#D000001)

#### 5. Boletins
- Emitir, editar, apagar boletins
- Sugestão inteligente de valor
- Marcar como pago/pendente
- Botões condicionais por estado
- Filtros por sócio e estado
- Numeração automática (#B0001)

#### 6. Clientes
- CRUD completo
- Pesquisa avançada (nome, NIF, email)
- Contador de projetos associados
- Validação antes de apagar
- Formulário completo (Nome, NIF, País, Morada, Contacto, Email, Angariação, Nota)
- Numeração automática (#C0001)

#### 7. Fornecedores
- CRUD completo
- 3 estatutos (EMPRESA, FREELANCER, ESTADO)
- Classificação 1-5 estrelas
- Áreas e funções
- Validade do seguro de trabalho
- Pesquisa multi-campo
- Validação antes de apagar
- Numeração automática (#F0001)

#### 8. Autenticação
- Login com JWT
- Sessões persistentes
- 2 utilizadores pré-criados
- Gestão de permissões

---

## 🎯 Enums Corretos (IMPORTANTE!)

### EstadoProjeto ✅
```python
NAO_FATURADO   # Projeto não faturado
FATURADO       # Faturado mas não recebido
RECEBIDO       # ✅ Pago e recebido (conta para saldos)
```

### EstadoDespesa ✅
```python
ATIVO          # Despesa ativa (não paga)
VENCIDO        # Despesa vencida (não paga)
PAGO           # ✅ Despesa paga (conta para saldos)
# ❌ NÃO EXISTE: PENDENTE
```

### EstadoBoletim ✅
```python
PENDENTE       # Boletim emitido mas não pago (já desconta do saldo)
PAGO           # ✅ Boletim pago
```

### TipoProjeto ✅
```python
EMPRESA           # Projeto da empresa (só prémios contam)
PESSOAL_BRUNO     # Projeto pessoal do Bruno (valor total)
PESSOAL_RAFAEL    # Projeto pessoal do Rafael (valor total)
```

### TipoDespesa ✅
```python
FIXA_MENSAL      # Divide por 2 (cada sócio paga metade)
PESSOAL_BRUNO    # Desconta apenas do Bruno
PESSOAL_RAFAEL   # Desconta apenas do Rafael
EQUIPAMENTO      # Equipamento
PROJETO          # Associada a projeto
```

### EstatutoFornecedor ✅
```python
EMPRESA          # Fornecedor é uma empresa
FREELANCER       # Fornecedor é freelancer
ESTADO           # Fornecedor é entidade do Estado
```

---

## 🔧 Scripts Disponíveis

### `python3 init_setup.py` - Inicialização Completa
**Executa 5 verificações/correções:**
1. Remove sessões antigas
2. Verifica/cria ficheiro .env
3. **Força SQLite** (corrige PostgreSQL automaticamente)
4. Cria base de dados se não existir
5. Cria utilizadores padrão

**Quando usar**: Primeira execução, após git pull, ou quando há erros de conexão

### `python3 check_integrity.py` - Verificação Completa
**Executa 7 verificações:**
1. Versão do Python
2. Dependências instaladas
3. Configuração .env
4. Base de dados e utilizadores
5. Sintaxe de ficheiros Python
6. **Imports e enums corretos** (previne erros)
7. Estrutura de diretórios

**Quando usar**: Antes de executar, após alterações, ou para diagnóstico

### `python3 clear_session.py` - Limpeza Rápida
**Executa limpeza simples:**
- Remove sessão antiga
- Verifica configuração básica

**Quando usar**: Erros de "No route to host"

### `python3 setup_database.py` - Setup Manual
**Cria base de dados manualmente:**
- Cria todas as tabelas
- Cria utilizadores

**Quando usar**: Raramente (init_setup.py já faz isto)

---

## 🐛 Troubleshooting

### Problema: AttributeError com enums

**Sintoma**: `AttributeError: type object 'EstadoDespesa' has no attribute 'PENDENTE'`

**Causa**: Código a usar enum que não existe

**Solução**:
```bash
git pull  # Já corrigido no commit 702e643
```

**Enums corretos**:
- EstadoDespesa: `ATIVO`, `VENCIDO`, `PAGO` (❌ não `PENDENTE`)
- EstadoBoletim: `PENDENTE`, `PAGO` (✅ tem `PENDENTE`)

### Problema: KeyError em dicionários

**Sintoma**: `KeyError: 'saldo_final'`

**Causa**: Código a procurar chave errada no dicionário

**Solução**:
```bash
git pull  # Já corrigido no commit 5a699be
```

**Chaves corretas do SaldosCalculator**:
```python
{
    'socio': 'BRUNO',
    'saldo_total': 1000.00,  # ✅ não 'saldo_final'
    'ins': {...},
    'outs': {...},
    'sugestao_boletim': 1000.00
}
```

### Problema: Conexão PostgreSQL

**Sintoma**: `No route to host` ao conectar ao Supabase

**Causa**: .env a apontar para PostgreSQL ou sessão antiga

**Solução**:
```bash
python3 init_setup.py  # Corrige automaticamente
```

### Problema: Dashboard não carrega

**Sintomas possíveis**:
- KeyError
- AttributeError
- Tela em branco

**Solução completa**:
```bash
# 1. Pull das correções
git pull

# 2. Limpar tudo
rm -f agora_media.db
rm -rf ~/.agora_contabilidade/session.json

# 3. Reconfigurar
python3 init_setup.py

# 4. Verificar
python3 check_integrity.py

# 5. Executar
python3 main.py
```

---

## 📋 Credenciais

```
Bruno:  bruno@agoramedia.pt  / bruno123
Rafael: rafael@agoramedia.pt / rafael123
```

---

## 🔜 Roadmap Fase 2

- [ ] Date pickers modernos
- [ ] Validações avançadas
- [ ] Melhorias visuais
- [ ] Geração de PDFs
- [ ] TOConline API
- [ ] Gráficos e relatórios
- [ ] Export Excel
- [ ] Backup automático

---

## ✅ Checklist de Verificação

Antes de reportar um problema, verifica:

- [ ] Executei `git pull`?
- [ ] Executei `python3 init_setup.py`?
- [ ] Executei `python3 check_integrity.py` com sucesso?
- [ ] A base de dados existe (`agora_media.db`)?
- [ ] O .env tem `DATABASE_URL=sqlite:///./agora_media.db`?
- [ ] Todas as dependências estão instaladas?
- [ ] Python 3.11+ está instalado?

Se tudo está ✅ e ainda há erro:

1. Copia a mensagem de erro completa
2. Executa `python3 check_integrity.py` e copia o output
3. Reporta ambos

---

*Última atualização: 2025-10-27 • Commits: 5a699be, 702e643, 4937390*
