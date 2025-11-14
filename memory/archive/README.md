# 🗄️ Archive - Documentação Histórica

Este diretório contém documentação histórica que já não é necessária no dia-a-dia, mas que pode ser útil para consulta futura.

## 📁 Estrutura

```
archive/
├── importacao/          # Documentação da importação inicial do Excel (Nov 2025)
├── setup_antigo/        # Guias de setup antigos (Supabase, Windows, etc.)
├── migrations_docs/     # Documentação antiga de migrations
├── problemas/           # Documentação de problemas específicos resolvidos
└── README.md            # Este ficheiro
```

## 📂 Conteúdo por Pasta

### `importacao/`
Documentação da importação única de dados do Excel para a base de dados SQLite (08/11/2025):

- `IMPORTACAO_20251108.md` - Registo completo da importação de 08/11/2025
- `INSTRUCOES_FINAIS.md` - Instruções pós-importação (29/10/2025)
- `RESULTADO_IMPORTACAO.md` - Resultados da importação
- `RESULTADO_FINAL.md` - Resultados finais
- `run_import.py` - Script de importação automática
- `validate_import.py` - Script de validação de dados importados

**Contexto:** Estes ficheiros documentam a migração inicial de dados do Excel para o sistema. A importação foi feita uma única vez e não será repetida (os dados agora são geridos pela aplicação).

**Script atual:** O script de importação ativo é `scripts/import_from_excel.py`, que lê diretamente do Excel usando pandas.

### `setup_antigo/`
Guias de setup antigos que foram substituídos por `memory/DEV_SETUP.md`:

- `README_SETUP.md` - Setup antigo com Supabase (obsoleto)
- `SETUP_GUIDE.md` - Guia de setup com Supabase (obsoleto)
- `WINDOWS_SETUP.md` - Setup específico para Windows
- `run_setup.py` - Script de setup automático
- `check_python_version.py` - Verificador de compatibilidade Python

**Contexto:** Estes guias mencionam **Supabase** (PostgreSQL cloud), que foi substituído por **SQLite** local. O setup atual está documentado em `memory/DEV_SETUP.md`.

### `migrations_docs/`
Documentação antiga sobre migrations:

- `MIGRATION_EXAMPLE.md` - Exemplos de migrations Alembic
- `MIGRATION_INSTRUCTIONS.md` - Instruções para criar migrations

**Contexto:** Esta informação está agora integrada em `memory/DEV_SETUP.md` na secção de Alembic.

### `problemas/`
Documentação de problemas específicos que foram resolvidos:

- `RESUMO_PROBLEMA_DESPESAS_FIXAS.md` - Problema de cálculo de despesas fixas (resolvido)

**Contexto:** Documentação de troubleshooting de problemas específicos. Preservado para referência histórica.

## ⚠️ Importante

**Não uses estes ficheiros para referência técnica atual!**

Para documentação atualizada, consulta:
- `memory/CURRENT_STATE.md` - Estado atual do projeto
- `memory/DEV_SETUP.md` - Setup e desenvolvimento
- `memory/ARCHITECTURE.md` - Arquitetura do sistema
- `memory/DATABASE_SCHEMA.md` - Esquema da base de dados
- `README.md` (raiz) - Documentação principal

## 🗑️ Quando Apagar?

Este arquivo pode ser completamente removido se:
1. Nunca mais precisares de consultar o histórico de importação
2. Nunca mais precisares de referência aos guias de setup antigos
3. O projeto estiver estável e maduro (6+ meses em produção)

Por agora, mantém como referência histórica.

---

**Criado:** 09/11/2025
**Razão:** Limpeza do repositório - mover documentação histórica da raiz
