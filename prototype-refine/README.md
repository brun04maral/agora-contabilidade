# 🚀 Protótipo Refine + FastAPI

Protótipo moderno full-stack para Agora Contabilidade.

## 🏗️ Stack

**Backend:**
- FastAPI (Python 3.12)
- SQLAlchemy ORM
- PostgreSQL
- **REUTILIZA 80-90% da lógica Python existente!**

**Frontend:**
- Refine.dev (React)
- Ant Design
- TypeScript
- Vite

## ✨ Features Implementadas

- ✅ **Dashboard** com saldos em tempo real
- ✅ **Projetos** - CRUD completo
- ✅ **Despesas** - CRUD completo
- ✅ **Clientes** - CRUD completo
- ✅ **API REST** - FastAPI com docs automáticas
- ✅ **UI Moderna** - Refine + Ant Design

## 🏃 Como Rodar

### Docker Compose (Recomendado)

```bash
cd prototype-refine

# Start tudo
docker-compose up --build

# Acessar:
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Local (Manual)

**Backend:**
```bash
cd backend

# Criar venv
python3 -m venv venv
source venv/bin/activate

# Install deps
pip install -r requirements.txt

# Run
uvicorn main:app --reload

# API: http://localhost:8000
# Docs: http://localhost:8000/docs
```

**Frontend:**
```bash
cd frontend

# Install deps
npm install

# Run dev server
npm run dev

# App: http://localhost:3000
```

## 📸 Screenshots

### Dashboard com Saldos
![Dashboard](../screenshots/refine-dashboard.png)

### Lista de Projetos
![Projetos](../screenshots/refine-projetos.png)

### Form de Criar Projeto
![Create](../screenshots/refine-create.png)

## 🎯 Vantagens

✅ **Backend 100% Python** - Reutiliza lógica existente
✅ **UI Moderna** - Refine = geração automática de CRUD
✅ **Type-Safe** - TypeScript no frontend
✅ **API Docs Automáticas** - FastAPI Swagger UI
✅ **Mobile Responsive** - Funciona em tablets/telemóveis
✅ **Escalável** - Arquitetura profissional

## 🔧 Como Funciona

### Backend (FastAPI)

```python
# Reutiliza os models existentes!
from models import Socio, Projeto, Despesa

@app.get("/api/projetos")
def list_projetos(db: Session = Depends(get_db)):
    return db.query(Projeto).all()
```

### Frontend (Refine)

```tsx
// Refine gera UI automaticamente!
<Refine
  resources={[
    { name: "projetos", list: ProjetoList, create: ProjetoCreate },
    { name: "despesas", list: DespesaList, create: DespesaCreate },
  ]}
/>
```

**Refine cria automaticamente:**
- Tabelas com sorting/filtering
- Forms de criação/edição
- Navegação
- State management
- API calls

## ⚙️ Estrutura do Projeto

```
prototype-refine/
├── backend/               # FastAPI
│   ├── main.py           # API endpoints
│   ├── models.py         # SQLAlchemy models (REUSADOS!)
│   ├── schemas.py        # Pydantic schemas
│   └── database.py       # DB connection
│
├── frontend/             # React + Refine
│   ├── src/
│   │   ├── App.tsx       # Refine config
│   │   ├── pages/        # CRUD pages
│   │   │   ├── projetos/
│   │   │   ├── despesas/
│   │   │   └── clientes/
│   │   └── components/
│   └── package.json
│
└── docker-compose.yml    # Full stack deploy
```

## 📝 Próximos Passos

Se escolher esta opção:

1. **Migrar todos os models** (Boletins, Orçamentos, etc)
2. **Completar CRUD** para todas entidades
3. **Dashboard avançado** (gráficos, estatísticas)
4. **Relatórios/Exports** (Excel, PDF)
5. **Auth de produção** (JWT, OAuth)
6. **Deploy no teu servidor**

## 🔗 API Endpoints

Backend expõe API REST completa:

- `GET /api/saldos` - Saldos dos sócios
- `GET /api/projetos` - Listar projetos
- `POST /api/projetos` - Criar projeto
- `GET /api/despesas` - Listar despesas
- `GET /api/clientes` - Listar clientes
- `GET /docs` - Swagger UI (docs interativas)

## 💡 Por Que Escolher Esta Opção?

**Vs Django:**
- ✅ UI mais moderna/flexível (React vs Django Admin)
- ✅ Frontend/Backend separados (mais profissional)
- ❌ Mais trabalho inicial (2 projetos vs 1)

**Vs ERPNext:**
- ✅ Controlo total (não estás preso a framework)
- ✅ Código mais limpo/simples
- ❌ Menos features out-of-the-box

## 🕐 Timeline Estimada

- **Setup inicial:** 1 semana
- **Core features:** 2 semanas
- **Features avançadas:** 1 semana
- **TOTAL:** ~3-4 semanas (30-50h)

## 🔧 Tecnologias Usadas

- [FastAPI](https://fastapi.tiangolo.com/) - Backend framework
- [Refine](https://refine.dev/) - React framework CRUD
- [Ant Design](https://ant.design/) - UI components
- [PostgreSQL](https://www.postgresql.org/) - Database
- [SQLAlchemy](https://www.sqlalchemy.org/) - ORM
- [Vite](https://vitejs.dev/) - Frontend build tool
