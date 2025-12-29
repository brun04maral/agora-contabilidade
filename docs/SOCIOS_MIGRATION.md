# Sócios Migration - Implementation Guide

**Date:** December 2025
**Status:** ✅ Complete
**Branch:** `claude/self-hosted-brainstorm-heo8m`

---

## Overview

Implementação do modelo `Socio` para substituir valores hardcoded 'BA' e 'RR' por entidades de database com ForeignKey relationships.

**Empresa:** Amaral & Reigota - Produção Audiovisual, Lda (NIPC: 518 351 190)
**Marca:** Agora Media Production
**Sócios:** Bruno Amaral (BA) e Rafael Reigota (RR)

### Goals
1. ✅ Criar modelo Socio com dados completos (nome, email, participação, etc.)
2. ✅ Adicionar FK relationships a Projeto, Boletim, Orcamento
3. ✅ Migrar dados existentes dos campos antigos para os novos FKs
4. ✅ Manter backward compatibility durante a transição

---

## Model Implementation

### File: `agora_web/core/models.py`

#### Socio Model
```python
class Socio(models.Model):
    """Sócio da Amaral & Reigota - Produção Audiovisual, Lda"""
    codigo = models.CharField(_('Código'), max_length=2, unique=True, primary_key=True)  # BA, RR
    nome_completo = models.CharField(_('Nome Completo'), max_length=100)
    nome_curto = models.CharField(_('Nome Curto'), max_length=50)
    email = models.EmailField(_('Email'))
    telefone = models.CharField(_('Telefone'), max_length=50, blank=True, null=True)
    percentagem_participacao = models.DecimalField(_('% Participação'), max_digits=5, decimal_places=2, default=50.00)
    ativo = models.BooleanField(_('Ativo'), default=True)
    cor_tema = models.CharField(_('Cor Tema'), max_length=7, default='#1976d2', blank=True, null=True)
    created_at = models.DateTimeField(_('Criado em'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Atualizado em'), auto_now=True)

    class Meta:
        verbose_name = _('Sócio')
        verbose_name_plural = _('Sócios')
        ordering = ['codigo']
        db_table = 'socios'

    def __str__(self):
        return self.codigo  # Returns "BA" or "RR" for clean display
```

**Design Decisions:**
- `codigo` is PK (CharField) for simplicity - values are 'BA' and 'RR'
- `__str__()` returns only codigo for clean dropdowns/lists
- `cor_tema` allows UI customization per partner
- `percentagem_participacao` defaults to 50.00 (equal split)

#### CodigoSocio Enum (renamed from Socio)
```python
class CodigoSocio(models.TextChoices):
    """DEPRECATED: Use Socio FK instead"""
    BRUNO_AMARAL = 'BA', 'Bruno Amaral'
    RAFAEL_REIGOTA = 'RR', 'Rafael Reigota'
```

**Why renamed?** To avoid naming conflict with the new Socio model.

#### ForeignKey Additions

**Projeto Model:**
```python
socio = models.ForeignKey(
    Socio,
    on_delete=models.RESTRICT,
    verbose_name=_('Sócio Responsável'),
    null=True, blank=True
)
# Keep old field for migration:
owner = models.CharField(max_length=2, choices=CodigoSocio.choices, null=True, blank=True)  # DEPRECATED
```

**Boletim Model:**
```python
socio = models.ForeignKey(
    Socio,
    on_delete=models.RESTRICT,
    verbose_name=_('Sócio'),
    null=True, blank=True
)
# Keep old field:
socio_codigo = models.CharField(max_length=2, choices=CodigoSocio.choices, null=True, blank=True)  # DEPRECATED
```

**Orcamento Model:**
```python
socio = models.ForeignKey(
    Socio,
    on_delete=models.RESTRICT,
    verbose_name=_('Sócio Responsável'),
    null=True, blank=True
)
```

**Important:** All FKs are `null=True, blank=True` to allow gradual migration.

---

## Initial Data

### File: `agora_web/core/fixtures/socios.json`

```json
[
  {
    "model": "core.socio",
    "pk": "BA",
    "fields": {
      "nome_completo": "Bruno Amaral",
      "nome_curto": "Bruno",
      "email": "bruno@agoramediaproduction.pt",
      "percentagem_participacao": "50.00",
      "ativo": true,
      "cor_tema": "#1976d2"
    }
  },
  {
    "model": "core.socio",
    "pk": "RR",
    "fields": {
      "nome_completo": "Rafael Reigota",
      "nome_curto": "Rafael",
      "email": "rafael@agoramediaproduction.pt",
      "percentagem_participacao": "50.00",
      "ativo": true,
      "cor_tema": "#f57c00"
    }
  }
]
```

**Load command:**
```bash
python manage.py loaddata socios
```

---

## Migration Issues & Solutions

### Issue 1: Migration 0004 Included Already-Existing Tables

**Problem:**
```
django.db.utils.ProgrammingError: relation "equipamento" already exists
```

Migration 0004 tried to create Equipamento and Orcamento tables that were already created in a previous session.

**Solution:**
```bash
python manage.py migrate core 0004 --fake
```

**Consequence:** This skipped creating the `socios` table! 🚨

---

### Issue 2: Socios Table Not Created

**Problem:**
```
django.db.utils.ProgrammingError: relation "socios" does not exist
```

After faking migration 0004, the socios table wasn't created.

**Solution:** Manual SQL script creation.

**See:** `docs/DATABASE_MANUAL_CHANGES.md` for complete SQL scripts.

---

## Data Migration

### Management Command: `migrate_socios`

**File:** `agora_web/core/management/commands/migrate_socios.py`

```python
from django.core.management.base import BaseCommand
from core.models import Socio, Projeto, Boletim, Orcamento

class Command(BaseCommand):
    help = 'Migra dados de owner/socio_codigo para FK Socio'

    def handle(self, *args, **options):
        # Get Socio instances
        ba = Socio.objects.get(codigo='BA')
        rr = Socio.objects.get(codigo='RR')

        # Migrate Projetos
        projetos_ba = Projeto.objects.filter(owner='BA', socio__isnull=True)
        projetos_ba.update(socio=ba)

        projetos_rr = Projeto.objects.filter(owner='RR', socio__isnull=True)
        projetos_rr.update(socio=rr)

        # Migrate Boletins
        boletins_ba = Boletim.objects.filter(socio_codigo='BA', socio__isnull=True)
        boletins_ba.update(socio=ba)

        boletins_rr = Boletim.objects.filter(socio_codigo='RR', socio__isnull=True)
        boletins_rr.update(socio=rr)

        # Migrate Orcamentos
        orcamentos_ba = Orcamento.objects.filter(socio_codigo='BA', socio__isnull=True)
        orcamentos_ba.update(socio=ba)

        # ... etc
```

**Execution:**
```bash
docker compose -f docker-compose.cloudflare.yml exec web python manage.py migrate_socios
```

**Results:**
- ✅ Migrated 81 projects
- ✅ Migrated 37 bulletins
- ✅ Migrated 1 budget

---

## Admin Customizations

### File: `agora_web/core/admin.py`

#### SocioAdmin
```python
@admin.register(Socio)
class SocioAdmin(ModelAdmin):
    list_display = ['codigo', 'nome_completo', 'nome_curto', 'email',
                    'percentagem_participacao', 'ativo', 'created_at']
    list_filter = ['ativo']
    search_fields = ['codigo', 'nome_completo', 'nome_curto', 'email']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['codigo']

    fieldsets = (
        ('Identificação', {
            'fields': ('codigo', 'nome_completo', 'nome_curto')
        }),
        ('Contactos', {
            'fields': ('email', 'telefone')
        }),
        ('Participação', {
            'fields': ('percentagem_participacao', 'ativo')
        }),
        ('UI', {
            'fields': ('cor_tema',),
            'classes': ['collapse']
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ['collapse']
        }),
    )
```

#### Updated Admins
- `ProjetoAdmin` - changed from `owner` to `socio` field
- `OrcamentoAdmin` - changed from `socio_codigo` to `socio` field
- `BoletimAdmin` - changed from `socio_codigo` to `socio` field

**Display:** All lists show only `codigo` (BA/RR) instead of full names for clean UI.

---

## Sidebar Navigation

**File:** `agora_web/config/settings.py`

Added to `UNFOLD` configuration:
```python
{
    "title": "Sócios",
    "icon": "group",
    "link": "/admin/core/socio/",
}
```

---

## Code Changes in SaldosCalculator

### File: `agora_web/core/utils/saldos.py`

**Issue:** Code referenced `Socio.BA` and `Socio.RR` which no longer exist (enum was renamed to CodigoSocio).

**Solution:** Replace with string literals.

**Changes (8 occurrences):**
```python
# Before:
projetos_ba = Projeto.objects.filter(tipo=TipoProjeto.PESSOAL_BRUNO, socio=Socio.BA, ...)

# After:
projetos_ba = Projeto.objects.filter(tipo=TipoProjeto.PESSOAL_BRUNO, socio='BA', ...)
```

**Why string literals?** Simpler, avoids import issues, works directly with CharField PK.

---

## Testing & Verification

### Shell Testing
```python
from core.models import Socio, Projeto, Boletim

# Verify Socios exist
Socio.objects.all()
# <QuerySet [<Socio: BA>, <Socio: RR>]>

# Check projects with FK
Projeto.objects.filter(socio='BA').count()
# 45

# Check bulletins
Boletim.objects.filter(socio='RR').count()
# 18

# Test SaldosCalculator
from core.utils.saldos import SaldosCalculator
calc = SaldosCalculator()
saldo = calc.calcular_saldo_bruno(incluir_investimento=True)
print(f"Bruno's balance: €{saldo['saldo_total']:.2f}")
# Bruno's balance: €13,390.16
```

---

## Rollback Plan

If needed, rollback is simple:

1. **Drop FK columns:**
   ```sql
   ALTER TABLE projetos DROP COLUMN socio_id;
   ALTER TABLE boletins DROP COLUMN socio_id;
   ALTER TABLE orcamentos DROP COLUMN socio_id;
   ```

2. **Drop socios table:**
   ```sql
   DROP TABLE socios;
   ```

3. **Revert code:** `git revert <commit>`

4. **Use old fields:** Change admin.py to use `owner`/`socio_codigo` again

---

## Future Improvements

1. **Remove deprecated fields** (`owner`, `socio_codigo`) after verifying migration success
2. **Add data validation** to ensure every Projeto/Boletim/Orcamento has a socio
3. **Add Socio permissions** if needed (currently all admins can manage)
4. **Extend Socio model** with more fields if needed (address, tax ID, etc.)

---

## Lessons Learned

1. ⚠️ **Always check existing tables** before running migrations
2. ⚠️ **Faking migrations** can skip important steps - verify manually
3. ✅ **Manual SQL** is sometimes necessary in production
4. ✅ **Gradual migration** (keeping old fields) reduces risk
5. ✅ **String literals** can be simpler than enums for FKs
6. ✅ **PostgreSQL uses RESTRICT** not PROTECT for ON DELETE

---

**Documentation by:** Claude Code
**Last Updated:** 2025-12-29
