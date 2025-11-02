# 🚀 Setup - Agora Media Contabilidade

## ⚠️ Resolver erro "No route to host"

Se encontrares o erro de conexão ao Supabase, segue estes passos:

### 1️⃣ Limpar sessão antiga e verificar configuração

```bash
python3 clear_session.py
```

Este script vai:
- ✅ Remover sessões antigas
- ✅ Verificar se o `.env` está configurado para SQLite
- ✅ Confirmar que a base de dados existe

### 2️⃣ Verificar ficheiro `.env`

O ficheiro `.env` deve ter esta linha:

```
DATABASE_URL=sqlite:///./agora_media.db
```

**NÃO deve ter** a linha do PostgreSQL ativa (deve estar comentada):
```
# DATABASE_URL=postgresql://postgres:...
```

### 3️⃣ Inicializar base de dados (se necessário)

Se a base de dados não existir ou estiver vazia:

```bash
python3 setup_database.py
```

Isto vai:
- Criar todas as tabelas
- Criar utilizadores iniciais:
  - **Bruno**: `bruno@agoramedia.pt` / senha: `bruno123`
  - **Rafael**: `rafael@agoramedia.pt` / senha: `rafael123`

### 4️⃣ Executar aplicação

```bash
python3 main.py
```

---

## 📋 Credenciais de Login

Após inicializar a base de dados, usa estas credenciais:

| Utilizador | Email | Senha |
|------------|-------|-------|
| Bruno Amaral | bruno@agoramedia.pt | bruno123 |
| Rafael Reigota | rafael@agoramedia.pt | rafael123 |

---

## 🔧 Resolução de Problemas

### Problema: Erro "connection to server at db.udylooqbigoufafbqjtl.supabase.co"

**Causa**: Sessão antiga a tentar conectar ao PostgreSQL

**Solução**:
```bash
# Limpar sessão
python3 clear_session.py

# Ou manualmente:
rm -rf ~/.agora_contabilidade/session.json

# Depois executar
python3 main.py
```

### Problema: Base de dados vazia ou sem utilizadores

**Solução**:
```bash
# Re-inicializar base de dados
rm agora_media.db
python3 setup_database.py
python3 main.py
```

### Problema: Módulo não encontrado

**Solução**:
```bash
# Instalar dependências
pip3 install -r requirements.txt
```

---

## 🎯 Estado Atual do Sistema

### ✅ Módulos Completos (MVP Fase 1):

1. **Dashboard** - Visão geral com todos os indicadores
2. **Saldos Pessoais** - Cálculo em tempo real dos saldos de Bruno e Rafael
3. **Projetos** - CRUD completo com gestão de tipos e estados
4. **Despesas** - CRUD completo com 5 tipos diferentes
5. **Boletins** - CRUD completo com sugestão inteligente
6. **Clientes** - CRUD completo com pesquisa avançada
7. **Fornecedores** - CRUD completo com classificações

### 🔜 Próximos Passos (Fase 2 - Polishing):

- Date pickers em vez de campos de texto
- Validações avançadas
- Melhorias visuais
- Geração de PDFs para boletins
- Integração com TOConline API

---

## 💡 Dicas

1. **Usar SQLite localmente** - Mais rápido e sem dependência de internet
2. **Backup regular** - Copia o ficheiro `agora_media.db` regularmente
3. **Testar funcionalidades** - Todos os CRUDs estão funcionais
4. **Feedback** - Anota os pontos que precisam de melhorias para a Fase 2

---

## 🆘 Ajuda

Se continuares com problemas:

1. Verifica que o Python 3.11+ está instalado
2. Confirma que todas as dependências estão instaladas
3. Executa `python3 clear_session.py` para diagnóstico completo
4. Verifica que o ficheiro `.env` existe e está correto
