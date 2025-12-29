# 📋 Plano de Implementação - Django + Unfold

**Migração:** Agora Contabilidade (CustomTkinter) → Django + Unfold
**Data:** 29/12/2024
**Timeline Estimada:** 2-3 semanas (~20-30h)

---

## 🎯 Objetivo

Migrar aplicação desktop para **web app Django** mantendo:
- ✅ 100% da lógica de negócio (especialmente Saldos 50/50)
- ✅ Todos os models (16 tabelas)
- ✅ Todas as features (CRUD + Relatórios)
- ✅ Precisão decimal nos cálculos

---

## 📊 Estado Atual vs Alvo

| Aspecto | Atual (CustomTkinter) | Alvo (Django) |
|---------|----------------------|---------------|
| **UI** | Desktop (800+ linhas/screen) | Web Admin (10-50 linhas) |
| **BD** | SQLite local | PostgreSQL partilhado |
| **ORM** | SQLAlchemy | Django ORM |
| **Acesso** | Local (1 PC) | Remoto (qualquer browser) |
| **Deploy** | .exe Windows | Docker container |
| **Lógica** | logic/ (8.000 linhas) | **REAPROVEITAR 60-70%** |

---

## 🗺️ Roadmap - 3 Semanas

### **SEMANA 1: Setup + Models + Core**
**Objetivo:** Base funcional com Saldos

#### **Dia 1-2: Setup Projeto**
- [ ] Criar projeto Django (`django-admin startproject agora_web`)
- [ ] Instalar Unfold theme
- [ ] Configurar PostgreSQL (Docker)
- [ ] Setup Docker Compose (web + db)
- [ ] Git branch: `feature/django-migration`

**Entregável:** Projeto Django vazio rodando em localhost

---

#### **Dia 3-4: Models Core (8 models)**
Migrar SQLAlchemy → Django ORM

**Prioridade ALTA (CORE):**
1. **User** - Autenticação
2. **Cliente** - Base de dados clientes
3. **Fornecedor** - Base de dados fornecedores
4. **Projeto** - CRÍTICO para saldos
5. **Despesa** - CRÍTICO para saldos
6. **DespesaTemplate** - Despesas recorrentes
7. **Boletim** - CRÍTICO para saldos
8. **BoletimLinha** - Linhas de deslocação

**Conversão exemplo:**
```python
# ANTES (SQLAlchemy):
class Projeto(Base):
    __tablename__ = "projetos"
    id = Column(Integer, primary_key=True)
    tipo = Column(Enum(TipoProjeto))
    owner = Column(String(2))
    valor_sem_iva = Column(Numeric(10, 2))

# DEPOIS (Django):
class Projeto(models.Model):
    tipo = models.CharField(max_length=20, choices=TipoProjeto.choices)
    owner = models.CharField(max_length=2, choices=[('BA', 'Bruno'), ('RR', 'Rafael')])
    valor_sem_iva = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = 'projetos'
        verbose_name = 'Projeto'
        verbose_name_plural = 'Projetos'
```

**Entregável:** 8 models Django + migrations aplicadas

---

#### **Dia 5-7: Lógica CORE - Saldos**
**CRÍTICO!** Adaptar `logic/saldos.py` (507 linhas)

**Abordagem:**
```python
# utils/saldos_calculator.py (Django)
class SaldosCalculator:
    def __init__(self, db=None):
        # Django não precisa de db injetada, usa ORM global
        pass

    def calcular_saldo_bruno(self, incluir_investimento=False, data_inicio=None, data_fim=None):
        # REAPROVEITAR lógica existente!
        # Trocar queries SQLAlchemy → Django ORM

        # ANTES:
        # projetos = db.query(Projeto).filter(...)

        # DEPOIS:
        projetos = Projeto.objects.filter(...)

        # Resto da lógica MANTÉM-SE IGUAL!
        return {
            'socio': 'BA',
            'saldo_total': saldo,
            'ins': {...},
            'outs': {...}
        }
```

**Entregável:** Cálculo de saldos funcionando em Django

---

### **SEMANA 2: Admin + Features Principais**
**Objetivo:** CRUD completo de entidades core

#### **Dia 8-9: Django Admin - Entidades Básicas**

**Clientes + Fornecedores:**
```python
# admin.py
from unfold.admin import ModelAdmin

@admin.register(Cliente)
class ClienteAdmin(ModelAdmin):
    list_display = ['numero', 'nome', 'nome_formal', 'nif', 'ativo']
    list_filter = ['ativo', 'pais']
    search_fields = ['nome', 'nome_formal', 'nif']

    fieldsets = (
        ('Informação Básica', {
            'fields': ('numero', 'nome', 'nome_formal', 'nif', 'ativo')
        }),
        ('Contactos', {
            'fields': ('email', 'telefone', 'morada', 'pais')
        }),
    )
```

**Entregável:** CRUD Clientes + Fornecedores funcionando

---

#### **Dia 10-11: Django Admin - Projetos**

**Features:**
- Lista com cliente, tipo, estado, valores, prémios
- Filtros: tipo, estado, cliente
- Inline para despesas do projeto (futuro)
- Actions: "Marcar como Pago", "Duplicar"
- Validação: valores >= 0

```python
@admin.register(Projeto)
class ProjetoAdmin(ModelAdmin):
    list_display = ['numero', 'cliente', 'tipo', 'owner', 'valor_display', 'estado']
    list_filter = ['tipo', 'estado', 'owner']
    search_fields = ['numero', 'descricao', 'cliente__nome']

    @admin.display(description='Valor')
    def valor_display(self, obj):
        return f"€{obj.valor_sem_iva:,.2f}"

    actions = ['marcar_como_pago', 'duplicar_projeto']

    def marcar_como_pago(self, request, queryset):
        queryset.update(estado='PAGO', data_pagamento=date.today())
```

**Entregável:** CRUD Projetos funcionando

---

#### **Dia 12-13: Django Admin - Despesas**

**Features:**
- Lista com data, tipo, credor, valores, estado
- Filtros: tipo, estado, credor
- Link para template (se gerada)
- Actions: "Marcar como Pago", "Gerar Recorrentes"

**Geração Automática de Recorrentes:**
```python
# management/commands/gerar_recorrentes.py
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    def handle(self, *args, **options):
        # Lógica existente em logic/despesas.py
        # gerar_despesas_recorrentes_mes()
        ...
```

**Entregável:** CRUD Despesas + Templates funcionando

---

#### **Dia 14: Django Admin - Boletins**

**Features:**
- Lista com sócio, mês/ano, totais, estado
- Filtros: sócio, ano, estado
- Inline para linhas de deslocação
- Actions: "Marcar como Pago", "Duplicar"
- Recalcular totais automático (signal)

```python
# signals.py
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

@receiver([post_save, post_delete], sender=BoletimLinha)
def recalcular_totais_boletim(sender, instance, **kwargs):
    boletim = instance.boletim
    # Recalcular totais
    boletim.recalcular_totais()
    boletim.save()
```

**Entregável:** CRUD Boletins funcionando

---

### **SEMANA 3: Features Avançadas + Deploy**
**Objetivo:** Orçamentos, Relatórios, Produção

#### **Dia 15-16: Models Avançados (8 models)**

**Prioridade MÉDIA:**
1. **Orcamento** - Sistema dual CLIENTE/EMPRESA
2. **OrcamentoSecao** - Hierarquia
3. **OrcamentoItem** - 5 tipos
4. **OrcamentoReparticao** - Beneficiários
5. **Equipamento** - Inventário
6. **EquipamentoAluguer** - Histórico
7. **ValorReferenciaAnual** - Valores boletins
8. **Freelancer + FreelancerTrabalho** - Multi-entidade
9. **FornecedorCompra** - Rastreabilidade

**Entregável:** Todos models migrados + Admin básico

---

#### **Dia 17-18: Dashboard Custom**

**NÃO usar default admin index!**

Criar dashboard custom:
```python
# views.py
from django.views.generic import TemplateView

class DashboardView(TemplateView):
    template_name = 'admin/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Calcular saldos
        calculator = SaldosCalculator()
        context['saldo_bruno'] = calculator.calcular_saldo_bruno()
        context['saldo_rafael'] = calculator.calcular_saldo_rafael()

        # Estatísticas
        context['projetos_ativos'] = Projeto.objects.filter(estado='ATIVO').count()
        context['despesas_pendentes'] = Despesa.objects.filter(estado='PENDENTE').count()

        return context
```

**Template Unfold:**
```html
{% extends "unfold/base.html" %}

{% block content %}
<div class="grid grid-cols-2 gap-4">
    <!-- Card Saldo Bruno -->
    <div class="card">
        <h2>Saldo Bruno (BA)</h2>
        <p class="text-3xl {% if saldo_bruno.saldo_total >= 0 %}text-green{% else %}text-red{% endif %}">
            €{{ saldo_bruno.saldo_total|floatformat:2 }}
        </p>
    </div>

    <!-- Card Saldo Rafael -->
    ...
</div>
{% endblock %}
```

**Entregável:** Dashboard funcional com Saldos

---

#### **Dia 19: Orçamentos V2**

**Sistema Dual:**
- Admin inline para Items CLIENTE
- Admin inline para Reparticoes EMPRESA
- Validação: total_cliente == total_empresa
- Action: "Aprovar" → cria Projeto

```python
class OrcamentoItemInline(admin.TabularInline):
    model = OrcamentoItem
    extra = 1
    fields = ['tipo', 'descricao', 'quantidade', 'dias', 'preco_unitario', 'total']
    readonly_fields = ['total']

class OrcamentoReparticaoInline(admin.TabularInline):
    model = OrcamentoReparticao
    extra = 1
    fields = ['tipo', 'beneficiario', 'descricao', 'valor_unitario', 'total']
    readonly_fields = ['total']

@admin.register(Orcamento)
class OrcamentoAdmin(ModelAdmin):
    inlines = [OrcamentoItemInline, OrcamentoReparticaoInline]

    def save_model(self, request, obj, form, change):
        # Validar totais
        if obj.validar_totais():
            super().save_model(request, obj, form, change)
        else:
            messages.error(request, "Totais CLIENTE e EMPRESA não batem!")
```

**Entregável:** Orçamentos V2 funcionando

---

#### **Dia 20: Relatórios + Exports**

**Relatórios Django:**
```python
# admin.py - Custom action
@admin.action(description='Exportar para Excel')
def exportar_excel(modeladmin, request, queryset):
    # Reaproveitar logic/relatorios.py
    from utils.relatorios import RelatoriosManager

    manager = RelatoriosManager()
    filepath = manager.exportar_para_excel(queryset, 'export.xlsx')

    # Return file download
    return FileResponse(open(filepath, 'rb'), as_attachment=True)
```

**Entregável:** Exports Excel funcionando

---

#### **Dia 21: Deploy Produção**

**Docker Compose (produção):**
```yaml
version: '3.8'

services:
  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: agora_prod
      POSTGRES_USER: agora
      POSTGRES_PASSWORD: ${DB_PASSWORD}  # .env
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backups:/backups  # Backups automáticos
    restart: always

  web:
    build: .
    command: gunicorn agora_web.wsgi:application --bind 0.0.0.0:8000 --workers 3
    volumes:
      - ./staticfiles:/app/staticfiles
      - ./media:/app/media
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://agora:${DB_PASSWORD}@db:5432/agora_prod
      DJANGO_SECRET_KEY: ${SECRET_KEY}
      DJANGO_DEBUG: False
      DJANGO_ALLOWED_HOSTS: ${ALLOWED_HOSTS}
    depends_on:
      - db
    restart: always

  nginx:
    image: nginx:alpine
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./staticfiles:/var/www/staticfiles
      - ./media:/var/www/media
      - /etc/letsencrypt:/etc/letsencrypt  # HTTPS
    ports:
      - "80:80"
      - "443:443"
    depends_on:
      - web
    restart: always

volumes:
  postgres_data:
```

**Backup automático:**
```bash
# scripts/backup.sh (cronjob diário)
#!/bin/bash
docker exec agora-db pg_dump -U agora agora_prod > /backups/agora_$(date +%Y%m%d).sql
# Manter apenas últimos 30 dias
find /backups -name "agora_*.sql" -mtime +30 -delete
```

**HTTPS (Caddy ou Certbot):**
```
# Caddyfile
agora.teudominio.com {
    reverse_proxy web:8000
}
```

**Entregável:** App rodando em produção (teu servidor)

---

## ✅ Checklist de Migração

### **Models (16/16)**
- [ ] User
- [ ] Cliente
- [ ] Fornecedor
- [ ] Projeto ⭐ CORE
- [ ] Despesa ⭐ CORE
- [ ] DespesaTemplate
- [ ] Boletim ⭐ CORE
- [ ] BoletimLinha
- [ ] Orcamento
- [ ] OrcamentoSecao
- [ ] OrcamentoItem
- [ ] OrcamentoReparticao
- [ ] Equipamento
- [ ] EquipamentoAluguer
- [ ] ValorReferenciaAnual
- [ ] Freelancer + FreelancerTrabalho + FornecedorCompra

### **Admin (16/16)**
- [ ] ClienteAdmin (CRUD completo)
- [ ] FornecedorAdmin (CRUD completo)
- [ ] ProjetoAdmin (CRUD + Actions)
- [ ] DespesaAdmin (CRUD + Actions + Recorrentes)
- [ ] BoletimAdmin (CRUD + Inlines + Recalcular)
- [ ] OrcamentoAdmin (Dual Inlines + Validação + Aprovar)
- [ ] EquipamentoAdmin
- [ ] FreelancerAdmin
- [ ] (outros...)

### **Lógica Core**
- [ ] SaldosCalculator ⭐ CRÍTICO
- [ ] Geração despesas recorrentes
- [ ] Transições automáticas de estado (signals)
- [ ] Recalcular totais boletins (signals)
- [ ] Validação totais orçamentos
- [ ] Conversão orçamento → projeto

### **Features**
- [ ] Dashboard custom com Saldos
- [ ] Relatórios Excel
- [ ] Exports PDF (orçamentos)
- [ ] Auth/Login
- [ ] Permissões por role (admin/socio/viewer)

### **Deploy**
- [ ] Docker Compose produção
- [ ] PostgreSQL configurado
- [ ] HTTPS (Caddy/Certbot)
- [ ] Backup automático (cronjob)
- [ ] Monitorização (logs)

---

## 🎯 Decisões Necessárias

Preciso de tua confirmação em:

### **1. Nome do Domínio**
Exemplo: `agora.teudominio.com` ou `contabilidade.agoramedia.pt`

**Escolha:**  _____________

---

### **2. Servidor**
Onde vais hospedar?
- [ ] VPS próprio (qual?)
- [ ] Cloud (AWS/DigitalOcean/Hetzner)
- [ ] Servidor local (IP fixo?)

**Escolha:** _____________

---

### **3. Dados Existentes**
Tens ~20 clientes, 45 fornecedores, 75 projetos, etc. já criados.

**Opções:**
- [ ] **A) Importar tudo** (script de migração SQLite → PostgreSQL)
- [ ] **B) Começar do zero** (recomeçar BD limpa)
- [ ] **C) Importar apenas Master Data** (clientes/fornecedores, sem histórico)

**Escolha:** _____________

---

### **4. Acesso Durante Migração**
Durante as 2-3 semanas de dev:

- [ ] **A) Continuo a usar app desktop** (desktop + Django em paralelo)
- [ ] **B) Paro de usar app** (espero Django ficar pronta)
- [ ] **C) Híbrido** (uso desktop, mas importo dados manualmente depois)

**Escolha:** _____________

---

### **5. Features Nice-to-Have**
Queres implementar já ou deixar para depois?

**Sistema Fiscal (IVA, IRS, SS):**
- [ ] Implementar já (+1 semana)
- [ ] Deixar para depois

**Freelancers/Fornecedores (UI gestão trabalhos/compras):**
- [ ] Implementar já (+2-3 dias)
- [ ] Deixar para depois

**Relatórios avançados (gráficos, charts):**
- [ ] Implementar já (+2-3 dias)
- [ ] Deixar para depois

---

## 📅 Timeline Final

### **Cenário BASE (2-3 semanas):**
- Semana 1: Setup + Models Core + Saldos
- Semana 2: Admin CRUD + Features principais
- Semana 3: Features avançadas + Deploy

**Entrega:** App funcional em produção

---

### **Cenário COMPLETO (+extras):**
- Semanas 1-3: BASE
- Semana 4: Sistema Fiscal + Freelancers UI + Relatórios

**Entrega:** App 100% completa (todas features)

---

## 🚀 Próximos Passos Imediatos

**Agora:**
1. **Tu decides** as 5 questões acima
2. **Eu crio** branch `feature/django-migration`
3. **Começamos** desenvolvimento

**Opções:**

**A) Começar JÁ** (crio setup Django agora)

**B) Agendar** (quando começamos? Ex: 02/01/2025)

**C) Rever plano** (queres mudar algo?)

---

**O que preferes?** 😊
