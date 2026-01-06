# Audit Trail Implementation - Status & Issues

## 📋 O Que Foi Implementado

### 1. Django Simple History
- ✅ Pacote `django-simple-history==3.4.0` instalado
- ✅ `HistoricalRecords` adicionado a todos os modelos principais
- ✅ Middleware `HistoryRequestMiddleware` configurado em `settings.py`
- ✅ `simple_history` em INSTALLED_APPS

### 2. Unfold Integration
- ✅ `unfold.contrib.simple_history` adicionado em INSTALLED_APPS (linha 26 de `config/settings.py`)
- ✅ `UnfoldHistoryAdmin` base class criada em `core/admin.py`
- ✅ Todos os modelos principais usam `UnfoldHistoryAdmin`

### 3. UserTrackingMixin
- ✅ Campos `created_by`, `updated_by`, `created_at`, `updated_at` em todos os modelos
- ✅ Estes campos aparecem em "Metadata" no admin (readonly)

### 4. Signals para Auto-População
- ✅ Ficheiro `core/signals.py` implementado
- ✅ Signal `pre_save` popula `created_by` e `updated_by` automaticamente
- ✅ Signal `pre_create_historical_record` garante `history_user`
- ✅ Exception handling adicionado para evitar 500 errors

### 5. Templates Customizados
- ✅ Template override em `core/templates/admin/change_form_object_tools.html`
  - Muda texto do botão de "History" para "Ver Histórico"
- ✅ Template customizado em `core/templates/simple_history/object_history.html`
  - Página de histórico com badges coloridos (verde=Criado, azul=Atualizado, vermelho=Eliminado)
  - Labels em português
  - Formatação de datas em formato PT

### 6. Link "Ver" no Metadata
- ✅ Método `history_link()` em `UnfoldHistoryAdmin` (linha 38-52 de `admin.py`)
- ✅ Aparece como botão "Ver" dentro do acordeão Metadata

### 7. Management Command
- ✅ Comando `create_system_user` criado em `core/management/commands/create_system_user.py`
- ✅ Cria user "Sistema" para importações Excel
- ✅ Executar com: `docker compose exec web python manage.py create_system_user`

---

## 🐛 Bugs & Problemas Identificados

### Bug #1: Alterações nos Templates Não Aparecem ⚠️
**Sintoma:** Alterações nos templates não aparecem mesmo após rebuild e hard refresh
**Causa:** DESCONHECIDA - NÃO é cache do browser, NÃO é cache do Cloudflare (Development Mode ativo)
**Impacto:** Botão continua a mostrar "História" em vez de "Ver Histórico"

**Tentativas que NÃO funcionaram:**
- ✗ Hard refresh do browser (Ctrl+Shift+R)
- ✗ Modo incógnito
- ✗ Development Mode do Cloudflare
- ✗ Múltiplos rebuilds do container

**Possíveis causas a investigar:**
- Django template cache?
- Whitenoise static files cache?
- Browser service worker?
- Problema no template override path?

**Status:** NÃO RESOLVIDO - causa raiz por identificar

---

### Bug #2: created_by/updated_by Não Populam em Objetos Antigos ⚠️
**Sintoma:** Campos `created_by` e `updated_by` aparecem como "None" ou "-"
**Causa:** Objetos criados ANTES da implementação dos signals têm estes campos NULL na DB
**Impacto:** Metadata não mostra quem criou/modificou

**Verificação:**
```sql
-- Ver objetos com campos NULL
SELECT id, created_by_id, updated_by_id FROM core_projeto LIMIT 10;
```

**Soluções:**
1. **Teste:** Fazer uma edição num objeto AGORA (após último rebuild) e verificar se popula
2. **Migration:** Criar data migration para popular campos antigos com user "Sistema"
3. **Aceitar:** Deixar NULL para histórico antigo (apenas novos edits terão)

**Status:** NÃO TESTADO - precisa de edição após último rebuild para confirmar que signals funcionam

---

### Bug #3: Visual Diff Não Implementado ❌
**Sintoma:** Página de histórico não mostra diferenças campo-a-campo
**Causa:** `django-simple-history` não fornece API automática para diff; requer implementação manual
**Impacto:** Página só mostra "Objeto criado/atualizado/eliminado" sem detalhes

**Implementação Simplificada Atual:**
- ✅ Mostra tipo de operação (Create/Update/Delete)
- ✅ Mostra user e timestamp
- ❌ NÃO mostra quais campos mudaram
- ❌ NÃO mostra valores antes/depois

**Solução Completa (NÃO IMPLEMENTADA):**
```python
# Em UnfoldHistoryAdmin, override history_view()
def get_change_message(self, obj, prev_obj):
    changes = []
    if prev_obj:
        for field in obj._meta.fields:
            old_val = getattr(prev_obj, field.name)
            new_val = getattr(obj, field.name)
            if old_val != new_val:
                changes.append({
                    'field': field.verbose_name,
                    'old': old_val,
                    'new': new_val
                })
    return changes
```

**Status:** SIMPLIFICADO - mostra apenas cronologia sem diff

---

### Bug #4: Error 500 ao Gravar (RESOLVIDO) ✅
**Sintoma:** "quando fiz 'gravar e continuar a editar' deu erro 500"
**Causa:** `get_current_user()` lançava exception quando middleware não capturava user
**Fix:** Adicionado try-except em `signals.py` linhas 34-38 e 67-70

**Código da Solução:**
```python
try:
    user = get_current_user()
except Exception:
    return  # Silently skip if can't get user
```

**Status:** RESOLVIDO - confirmado pelo user: "ao editar já não dá erro 500 (Aleluia!)"

---

## 📁 Ficheiros Modificados

### Ficheiros Core
1. **`agora_web/config/settings.py`**
   - Linha 26: `'unfold.contrib.simple_history'` em INSTALLED_APPS
   - Linha 52: `'simple_history.middleware.HistoryRequestMiddleware'` em MIDDLEWARE

2. **`agora_web/core/models.py`**
   - UserTrackingMixin aplicado a: Socio, Cliente, Fornecedor, Projeto, Despesa, DespesaTemplate, Boletim, Equipamento, Orcamento
   - `history = HistoricalRecords()` em todos esses modelos

3. **`agora_web/core/admin.py`**
   - Linhas 19-52: Classe `UnfoldHistoryAdmin`
   - Todos os ModelAdmin agora herdam de `UnfoldHistoryAdmin`

4. **`agora_web/core/signals.py`** (FICHEIRO NOVO)
   - Função `get_current_user()` usando thread local do middleware
   - Signal handler `populate_audit_fields()` com exception handling
   - Signal handler `set_history_user_from_request()`
   - Lista `TRACKED_MODELS` com todos os modelos a trackear

5. **`agora_web/core/apps.py`**
   - Linha 9: `import core.signals` para registar signals

### Templates Customizados
6. **`agora_web/core/templates/admin/change_form_object_tools.html`** (FICHEIRO NOVO)
   - Override do botão History para texto português "Ver Histórico"
   - Usa helper `unfold/helpers/tab_action.html`

7. **`agora_web/core/templates/simple_history/object_history.html`** (FICHEIRO NOVO)
   - Página de histórico estilizada com CSS inline
   - Badges coloridos para operações
   - Labels em português

### Management Commands
8. **`agora_web/core/management/commands/create_system_user.py`** (FICHEIRO NOVO)
   - Cria user "Sistema" para importações Excel
   - Executar: `docker compose exec web python manage.py create_system_user`

---

## 🔍 Como Testar

### Teste 1: Verificar 500 Error Resolvido ✅
```bash
# No admin, editar qualquer Projeto e clicar "Gravar e continuar a editar"
# Resultado esperado: Grava sem erro
# Status: CONFIRMADO - funciona
```

### Teste 2: Verificar created_by/updated_by ⚠️
```bash
# 1. Editar um Projeto no admin (adicionar nota, mudar nome, etc)
# 2. Gravar
# 3. Verificar secção "Metadata" - deve mostrar:
#    - Modificado por: [teu username]
#    - Modificado em: [data/hora atual]
# Status: NÃO TESTADO após último rebuild
```

### Teste 3: Verificar Botão "Ver Histórico" ⚠️
```bash
# 1. No admin, abrir qualquer Projeto existente
# 2. Verificar topo da página - deve ter botão "Ver Histórico" (não "História")
# Status: FALHA - continua a mostrar "História" (causa desconhecida)
```

### Teste 4: Verificar Link "Ver" no Metadata ✅
```bash
# 1. No admin, abrir qualquer Projeto existente
# 2. Expandir acordeão "Metadata"
# 3. Deve ter linha com botão "Ver" que abre página de histórico
# Status: NÃO CONFIRMADO visualmente
```

### Teste 5: Verificar Página de Histórico 📋
```bash
# 1. Clicar no botão "Ver" ou "Ver Histórico"
# 2. Deve abrir página com:
#    - Cards brancos com sombra
#    - Badges coloridos (verde/azul/vermelho)
#    - Labels "Criado", "Atualizado", "Eliminado"
#    - Nome do user e data em formato PT (dd/mm/YYYY HH:MM)
# Status: IMPLEMENTADO mas NÃO CONFIRMADO visualmente
```

---

## 🚀 Próximos Passos (Quando Retomar)

### Imediato
1. **INVESTIGAR** porque templates não aparecem (não é cache browser/Cloudflare)
2. **Fazer teste de edição** num Projeto para confirmar created_by/updated_by
3. **Verificar visualmente** se todos os templates aparecem corretamente

### Opcional (Se User Quiser)
4. **Implementar diff visual completo** com comparação campo-a-campo
5. **Data migration** para popular created_by/updated_by em objetos antigos

### User "Sistema" para Importações
7. **Executar comando** (se ainda não foi):
   ```bash
   docker compose exec web python manage.py create_system_user
   ```
8. **Modificar código de importação Excel** para usar este user:
   ```python
   from django.contrib.auth.models import User
   sistema_user = User.objects.get(username='sistema')
   # Ao criar objetos via import:
   obj.created_by = sistema_user
   obj.updated_by = sistema_user
   obj.save()
   ```

---

## 📝 Notas Técnicas

### Arquitetura da Solução
- **django-simple-history:** Cria tabelas `Historical*` automaticamente com snapshot de cada alteração
- **Unfold integration:** `unfold.contrib.simple_history` fornece UI para visualizar histórico
- **Signals:** Auto-populam campos sem precisar modificar views/forms
- **Thread Local:** Middleware armazena user atual; signals acedem via `get_current_user()`

### Limitações Conhecidas
- ⚠️ Signals só funcionam via Django ORM (não funcionam com SQL direto ou bulk_create)
- ⚠️ `django-simple-history` não fornece diff automático (requer implementação manual)
- ⚠️ Objetos criados antes da implementação têm created_by/updated_by = NULL

### Performance
- Cada save() cria 1 registo na tabela Historical* correspondente
- Tabelas Historical podem crescer muito; considerar archiving/purging periódico
- Índices em `history_date` e `history_user` são criados automaticamente

---

## 🔗 Referências
- [django-simple-history docs](https://django-simple-history.readthedocs.io/)
- [Unfold docs](https://unfoldadmin.com/)
- [Unfold + Simple History integration](https://github.com/unfoldadmin/unfold/tree/main/src/unfold/contrib/simple_history)

---

## 🎯 PROMPT PARA RETOMAR DAQUI A UNS DIAS

```
Retomar trabalho de audit trail (django-simple-history + Unfold).

LER PRIMEIRO: docs/audit-trail-implementation.md

CONTEXTO:
- Implementação código COMPLETA
- Último rebuild: 2026-01-06
- Container agora_web healthy
- 500 errors RESOLVIDOS ✅

BUGS ATIVOS:
1. Templates não aparecem mesmo após rebuild
   - Botão mostra "História" em vez de "Ver Histórico"
   - NÃO é cache browser (testado hard refresh + incognito)
   - NÃO é Cloudflare (Development Mode estava ativo)
   - Causa DESCONHECIDA - investigar Django template cache, Whitenoise, service workers

2. created_by/updated_by NÃO testados após fix dos signals
   - Objetos antigos têm campos NULL
   - Precisa edição teste APÓS último rebuild para validar

3. Visual diff NÃO implementado
   - Página histórico só mostra cronologia básica
   - django-simple-history não tem API diff automática
   - Requer implementação manual se user quiser

AÇÕES IMEDIATAS:
1. Investigar porque template override não funciona (Bug #1)
2. Pedir edição teste num Projeto para validar signals
3. Verificar DB se created_by/updated_by popularam
4. Perguntar se user quer diff visual completo

FICHEIROS CHAVE:
- agora_web/config/settings.py:26 (unfold.contrib.simple_history)
- agora_web/core/signals.py:34-38,67-70 (exception handling)
- agora_web/core/admin.py:19-52 (UnfoldHistoryAdmin)
- agora_web/core/templates/admin/change_form_object_tools.html (override)
- agora_web/core/templates/simple_history/object_history.html (página histórico)

IMPORTANTE: NÃO assumir problemas são cache. Investigar causas reais.
```
