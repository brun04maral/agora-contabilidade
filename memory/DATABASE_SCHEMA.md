### `socios` - Sócios da Empresa (Migration 022)

**Campos principais:**
- `id` - PK
- `codigo` - "BA" ou "RR"
- `nome` - Nome completo
- `nif` - Número fiscal
- `iban` - Conta bancária
- `percentagem` - % da sociedade (50.0)
- `cargo` - Cargo profissional
- `data_nascimento` - Data de nascimento
- `niss` - Número de Segurança Social
- `morada` - Morada completo
- `salario_base` - Salário base mensal
- `subsidio_alimentacao` - Subsídio de alimentação mensal
- `created_at` / `updated_at` - datetimes de registo/modificação

**Enums:**
- Nenhum

**Relações:**
- `projetos` → Lista de projetos
- `despesas` → Lista de despesas
- `boletins` → Lista de boletins

**Notas sobre UI:**
- Página independente por sócio, acesso por seleção inicial
- Card único informativo/editável

---

### Migration 022: Expandir tabela `socios` (Adiciona campos acima)
- Criar/atualizar `database/models/socio.py`
- Migration script `022_expandir_socios.py` adiciona todos os campos
- Testado rollback, compatibilidade e persistência

---