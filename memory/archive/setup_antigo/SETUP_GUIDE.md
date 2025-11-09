# 🚀 Guia de Setup - Agora Media Contabilidade

## 📋 Checklist de Configuração

- [ ] Repositório GitHub criado e clonado
- [ ] Estrutura de ficheiros criada
- [ ] Ambiente virtual Python configurado
- [ ] Dependências instaladas
- [ ] Conta Supabase criada
- [ ] Base de dados configurada
- [ ] Variáveis de ambiente configuradas
- [ ] Primeiro commit feito

---

## 1️⃣ Configurar GitHub Desktop

### Já está feito! ✅
O repositório está em: `/Users/brunoamaral/Documents/github/agora-contabilidade`

### Próximo passo no GitHub Desktop:
1. Abre o **GitHub Desktop**
2. Vês o repositório "agora-contabilidade" com ficheiros novos
3. **Commit inicial:**
   - Título: `✨ Inicial: Estrutura base do projeto`
   - Descrição: `Setup inicial com estrutura de pastas, README e dependências`
4. Clica em **"Commit to main"**
5. Clica em **"Push origin"** para enviar para o GitHub

---

## 2️⃣ Configurar Ambiente Python

### Criar ambiente virtual:
```bash
cd /Users/brunoamaral/Documents/github/agora-contabilidade
python3 -m venv venv
```

### Ativar ambiente virtual:
```bash
source venv/bin/activate
```

Deves ver `(venv)` no início da linha de comando.

### Instalar dependências:
```bash
pip install -r requirements.txt
```

---

## 3️⃣ Criar Conta Supabase (GRÁTIS)

### Passo 1: Criar conta
1. Vai a: https://supabase.com
2. Clica em **"Start your project"**
3. Faz login com GitHub (recomendado)

### Passo 2: Criar projeto
1. Clica em **"New Project"**
2. Preenche:
   - **Name**: `agora-media-contabilidade`
   - **Database Password**: (guarda isto!) - usa um password forte
   - **Region**: `Europe (Frankfurt)` ou `Europe (London)` (mais perto de PT)
   - **Pricing Plan**: `Free` (500MB storage, 50,000 requests/mês)
3. Clica em **"Create new project"**
4. Aguarda ~2 minutos enquanto cria a base de dados

### Passo 3: Obter credenciais
Quando o projeto estiver pronto:
1. No menu lateral, clica em **"Project Settings"** (ícone de engrenagem)
2. Clica em **"API"**
3. Copia estes valores:

```
Project URL: https://xxxxx.supabase.co
anon public key: eyJhbGci....... (token longo)
```

---

## 4️⃣ Configurar Variáveis de Ambiente

### Criar ficheiro .env:
```bash
cd /Users/brunoamaral/Documents/github/agora-contabilidade
cp .env.example .env
```

### Editar o .env:
Abre o ficheiro `.env` e preenche com as tuas credenciais do Supabase:

```env
# Supabase Configuration
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=eyJhbGci.......

# Database Configuration (do Supabase)
DATABASE_URL=postgresql://postgres:[PASSWORD]@db.xxxxx.supabase.co:5432/postgres

# Application Settings
APP_NAME=Agora Media Contabilidade
DEBUG=True

# Sócios
SOCIO_1_NOME=Bruno Amaral
SOCIO_2_NOME=Rafael Reigota
```

**⚠️ IMPORTANTE**: O `.env` NÃO será commitado para o GitHub (está no .gitignore)

---

## 5️⃣ Testar a Aplicação

### Executar pela primeira vez:
```bash
cd /Users/brunoamaral/Documents/github/agora-contabilidade
source venv/bin/activate  # se ainda não estiver ativo
python main.py
```

Deve abrir uma janela com:
- Título: "Agora Media Contabilidade"
- Texto: "🎬 Agora Media - Sistema de Contabilidade"
- Botão: "Testar Conexão"

Se aparecer, está tudo OK! ✅

---

## 6️⃣ Usar com Claude Code

### O que é o Claude Code?
É uma ferramenta de linha de comando que te permite delegar tarefas de coding ao Claude diretamente do terminal.

### Como usar:
1. No terminal (com venv ativo):
```bash
cd /Users/brunoamaral/Documents/github/agora-contabilidade
```

2. Usa Claude Code para pedir funcionalidades:
```bash
# Exemplo:
claude "Cria o modelo de base de dados para Projetos com todos os campos do brief"
```

3. O Claude Code irá:
   - Ler o contexto do projeto
   - Gerar o código
   - Criar/modificar ficheiros
   - Podes revisar antes de aceitar

---

## 7️⃣ Workflow Recomendado

### Ciclo de desenvolvimento:
1. **Pede ao Claude** (via chat ou Claude Code) para criar uma feature
2. **Testa** a funcionalidade
3. **Commit** no GitHub Desktop:
   - Título descritivo (ex: `✨ Feature: Módulo de Projetos`)
   - Descrição breve do que foi feito
4. **Push** para o GitHub
5. Repete!

### Convenções de commits:
- `✨ Feature:` - Nova funcionalidade
- `🐛 Fix:` - Correção de bug
- `📝 Docs:` - Documentação
- `♻️ Refactor:` - Refatoração de código
- `🎨 UI:` - Melhorias de interface
- `🔧 Config:` - Mudanças de configuração

---

## 🆘 Problemas Comuns

### Erro: "No module named 'customtkinter'"
**Solução**: Certifica-te que o venv está ativo e corre:
```bash
pip install -r requirements.txt
```

### Erro ao conectar com Supabase
**Solução**: Verifica se o `.env` tem as credenciais corretas do Supabase

### GitHub Desktop não vê mudanças
**Solução**: Verifica se estás no diretório correto: `/Users/brunoamaral/Documents/github/agora-contabilidade`

---

## 📞 Próximos Passos

Depois deste setup:
1. ✅ Criar modelos de base de dados (Projeto, Despesa, Cliente, etc.)
2. ✅ Criar tabelas no Supabase
3. ✅ Interface básica funcional
4. ✅ Módulo de Saldos Pessoais (o mais importante!)

---

**Pronto para começar! 🚀**

Qualquer dúvida, pergunta ao Claude!
