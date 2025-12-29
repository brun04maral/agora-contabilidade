# 🚀 Setup Local - Django + Unfold

## Sem Docker? Sem Problema!

### Quick Start (3 comandos)

```bash
# 1. Executar setup (cria venv, instala deps, cria DB)
./setup_local.sh

# 2. Iniciar servidor
./run_local.sh

# 3. Abrir navegador
# http://localhost:8000/admin/
```

### O Que o Setup Faz

1. ✅ Cria ambiente virtual Python
2. ✅ Instala Django + Unfold + deps
3. ✅ Configura **SQLite** (não precisa PostgreSQL)
4. ✅ Cria base de dados
5. ✅ Pede para criar superuser (admin)

### Problemas?

**Erro: `python3: command not found`**
```bash
# Instala Python via Homebrew
brew install python@3.12
```

**Erro: Permission denied**
```bash
chmod +x setup_local.sh run_local.sh
```

**Erro: Django não importa**
```bash
# Ativar venv primeiro
source venv/bin/activate
```

### Parar o Servidor

`Ctrl + C` no terminal

### Reset Completo

```bash
rm -rf venv db.sqlite3
./setup_local.sh
```

### Screenshots

Após login em `http://localhost:8000/admin/`:
- Sidebar moderna com ícones
- Dashboard com estatísticas
- CRUD de Projetos, Despesas, Clientes
- Theme Unfold (dark mode disponível)

---

**Nota:** Esta é versão **local/dev** com SQLite. Para produção, usa Docker com PostgreSQL.
