# ⚙️ Setup de Desenvolvimento

Guia completo para configurar o ambiente de desenvolvimento.

---

## 📋 Pré-requisitos

### Sistema Operativo
- **Linux** (testado: Ubuntu 22.04+)
- **macOS** (10.15+)
- **Windows** (10/11)

### Python
- **Versão:** 3.12+ (recomendado)
- **Mínimo:** 3.10

### Ferramentas
- `git` - controlo de versão
- `pip` - gestor de pacotes Python
- (Opcional) `venv` ou `virtualenv` - ambientes virtuais

---

## 🚀 Setup Rápido

### 1. Clonar Repositório

```bash
git clone <repo-url> agora-contabilidade
cd agora-contabilidade
```

### 2. Criar Ambiente Virtual (Recomendado)

```bash
# Criar venv
python3 -m venv venv

# Ativar
# Linux/Mac:
source venv/bin/activate
# Windows:
venv\Scripts\activate
```

### 3. Instalar Dependências

```bash
pip install -r requirements.txt
```

**Dependências principais:**
- `sqlalchemy` - ORM
- `alembic` - Migrations
- `customtkinter` - UI
- `pillow` - Imagens
- `openpyxl` - Excel
- `pandas` - Dados

### 4. Configurar Base de Dados

```bash
# Criar DB e aplicar migrations
alembic upgrade head

# (Opcional) Seed data para desenvolvimento
python -c "from database.seed import seed_database; seed_database()"
```

### 5. Executar Aplicação

```bash
python main.py
```

---

## 🗄️ Base de Dados

### Estrutura

- **Ficheiro:** `agora_media.db` (SQLite)
- **Localização:** Raiz do projeto
- **Git:** `.gitignore` (não fazer commit do DB)

### Migrations (Alembic)

#### Ver estado atual
```bash
alembic current
```

#### Aplicar migrations
```bash
alembic upgrade head
```

#### Reverter última migration
```bash
alembic downgrade -1
```

#### Criar nova migration (depois de alterar models)
```bash
alembic revision --autogenerate -m "descrição da mudança"
```

#### Reset completo do DB (desenvolvimento)
```bash
rm agora_media.db
alembic upgrade head
python -c "from database.seed import seed_database; seed_database()"
```

---

## 📁 Estrutura do Projeto

```
agora-contabilidade/
├── main.py                 # Entry point
├── requirements.txt        # Dependências Python
├── agora_media.db         # SQLite DB (gitignored)
│
├── database/              # Camada de dados
│   ├── models/           # SQLAlchemy models
│   ├── migrations/       # Alembic migrations
│   └── seed.py          # Dados iniciais
│
├── logic/                # Lógica de negócio
│   ├── saldos.py        # Cálculo de saldos (CORE)
│   └── ...              # Outros managers
│
├── ui/                   # Interface gráfica
│   ├── screens/         # 10 screens principais
│   └── components/      # Componentes reutilizáveis
│
├── assets/              # Recursos visuais
│   └── resources.py     # Ícones Base64
│
├── media/               # Logos PNG
│   └── logos/
│
└── memory/              # 🧠 Documentação dev
    ├── README.md
    ├── CURRENT_STATE.md
    ├── ARCHITECTURE.md
    └── ...
```

---

## 🧪 Testes

### Executar aplicação em modo de desenvolvimento

```bash
python main.py
```

### Verificar imports
```bash
python -c "from database.models import *; from logic import *; from ui.screens import *"
```

### Testar migration
```bash
# Aplicar
alembic upgrade head
# Reverter
alembic downgrade -1
# Re-aplicar
alembic upgrade head
```

---

## 🔧 Troubleshooting

### Erro: `ModuleNotFoundError`
```bash
# Reinstalar dependências
pip install -r requirements.txt
```

### Erro: `No such table`
```bash
# Aplicar migrations
alembic upgrade head
```

### Erro: `Database is locked`
```bash
# Fechar todas as instâncias da app
# Remover ficheiro .db-journal se existir
rm agora_media.db-journal
```

### CustomTkinter não aparece bonito
```bash
# Verificar versão
pip show customtkinter
# Atualizar se necessário
pip install --upgrade customtkinter
```

### Logos não aparecem (Windows)
Os PNGs devem estar em `media/logos/`:
```
logo_sidebar.png
logo_sidebar@2x.png
logo_login.png
logo_login@2x.png
```

Se faltarem, consultar `memory/ASSET_SYSTEM.md`.

---

## 📦 Build para Produção (Windows)

### Instalar PyInstaller
```bash
pip install pyinstaller
```

### Criar executável
```bash
pyinstaller --name "Agora Media" \
            --windowed \
            --icon=media/logos/icon.ico \
            --add-data "media;media" \
            main.py
```

### Output
- `dist/Agora Media/` - pasta com executável
- Distribuir pasta completa (contém DLLs)

---

## 🌳 Git Workflow

### Branches
- `main` - produção (stable)
- `claude/*` - desenvolvimento (sessions)

### Commits
Seguir convenção:
```
✨ Adicionado: nova feature
🔧 Alterado: mudança em feature
🐛 Corrigido: bug fix
📝 Documentação: docs
🎨 Estilo: formatação, ícones
```

### Antes de commit
```bash
git status
git diff
git add <ficheiros>
git commit -m "mensagem"
git push
```

---

## 💡 Dicas

### IDE Recomendado
- **VS Code** com extensões:
  - Python
  - Pylance
  - SQLite Viewer

### Configuração VS Code
```json
{
  "python.linting.enabled": true,
  "python.formatting.provider": "black",
  "editor.formatOnSave": true
}
```

### Debugging
```python
# Adicionar breakpoints com print
print(f"DEBUG: variavel = {variavel}")

# Ou usar debugger
import pdb; pdb.set_trace()
```

### Performance
- SQLite usa índices automáticos (PKs, FKs)
- Para queries lentas: adicionar índices manualmente
- DB file ~200KB (muito rápido)

---

## 📚 Recursos

- [CustomTkinter Docs](https://customtkinter.tomschimansky.com/)
- [SQLAlchemy Docs](https://docs.sqlalchemy.org/)
- [Alembic Tutorial](https://alembic.sqlalchemy.org/en/latest/tutorial.html)

---

**Mantido por:** Equipa Agora Media
**Última atualização:** 2025-11-09
