# Sistema de Importação de Dados

**Data:** 2026-01-03
**Status:** ✅ Implementado e Testado

---

## 📋 Visão Geral

Sistema web integrado no Django Admin que permite importar dados de ficheiros Excel (.xlsx) diretamente pela interface web, sem necessidade de acesso SSH ou linha de comandos.

## 🎯 Funcionalidades

### Upload Web
- Interface drag-and-drop para upload de ficheiros Excel
- Validação de formato (.xlsx apenas)
- Feedback visual em tempo real
- Mensagens de sucesso/erro detalhadas

### Processamento
- Reutiliza 100% da lógica do comando `import_from_excel`
- Processa 5 abas: FORNECEDORES, CLIENTES, PROJETOS, DESPESAS, BOLETINS
- Agrega prémios por projeto
- Agrega boletins por (sócio, mês, ano)
- Sistema de tags para despesas

### Segurança
- Ficheiros temporários são automaticamente eliminados após importação
- Validação de extensão de ficheiro
- Integração com sistema de permissões do Django Admin

---

## 🏗️ Arquitetura

### Componentes

```
ImportacaoDados (models.py)
  ↓
ImportacaoDadosAdmin (admin.py)
  ↓
changelist.html (template)
  ↓
import_from_excel (management command)
```

### 1. Modelo Proxy
**Ficheiro:** `agora_web/core/models.py` (linhas 993-1005)

```python
class ImportacaoDados(models.Model):
    """Proxy model para interface de upload - SEM tabela na BD"""
    class Meta:
        managed = False  # Django não cria tabela
        db_table = 'importacao_view'  # Tabela fictícia
```

**Por quê proxy?**
- Não precisamos armazenar dados de importação
- Apenas fornece entry point no admin
- Mantém código limpo e simples

### 2. Admin View
**Ficheiro:** `agora_web/core/admin.py` (linhas 565-636)

**Workflow:**
1. **GET Request:** Renderiza formulário de upload
2. **POST Request:**
   - Valida extensão do ficheiro
   - Guarda temporariamente em `/app/uploads/`
   - Executa `call_command('import_from_excel', file_path)`
   - Captura output do comando
   - Exibe mensagens de sucesso/erro
   - Remove ficheiro temporário

**Handlers:**
```python
def changelist_view(self, request):
    if request.method == 'POST':
        # Upload → Validação → Importação → Feedback
    else:
        # Renderizar formulário
```

### 3. Template
**Ficheiro:** `agora_web/core/templates/admin/core/importacaodados/changelist.html`

**Features:**
- Design consistente com tema Unfold
- Suporte a dark mode
- Drag-and-drop funcional
- Validação client-side
- Info cards com instruções

---

## 📖 Como Usar

### Via Admin Interface

1. **Aceder ao Admin:**
   ```
   https://app.agoramediaproduction.pt/admin/
   ```

2. **Navegar para Importação:**
   - No menu lateral: **Core → Importação de Dados**

3. **Upload do Ficheiro:**
   - Clicar na área de upload OU
   - Arrastar ficheiro .xlsx para a área

4. **Executar Importação:**
   - Clicar "📤 Importar Dados"
   - Aguardar processamento (pode demorar 10-30 segundos)

5. **Verificar Resultado:**
   - Mensagem verde = Sucesso ✅
   - Mensagem amarela = Avisos ⚠️
   - Mensagem vermelha = Erro ❌

### Via Linha de Comandos (ainda disponível)

```bash
# Continua a funcionar como antes
docker compose exec web python manage.py import_from_excel excel/CONTABILIDADE_FINAL_20251231.xlsx
```

---

## 🔧 Validações

### Formato do Ficheiro
- **Extensão:** Apenas `.xlsx` aceite
- **Abas obrigatórias:** FORNECEDORES, CLIENTES, PROJETOS, DESPESAS, BOLETINS
- **Estrutura:** Deve seguir formato definido (ver [EXCEL_IMPORT_ANALYSIS.md](EXCEL_IMPORT_ANALYSIS.md))

### Processamento
- Fornecedores e clientes: Update or create por `numero`
- Projetos: Update or create por `numero` (skip se vazio: sem descrição, cliente e valor=0)
- Despesas: Update or create por `numero` (skip se vazio: sem descrição, credor e valor=0)
- Prémios: Agregados por projeto (soma de todos os prémios)
- Boletins: Agregados por (socio, mes, ano)

### Proteção contra Linhas Vazias (IMPORTANTE!)
O sistema **não importa** linhas vazias do Excel:
- **Projetos vazios:** Linhas que só têm número (#P0001) mas sem descrição, cliente ou valor
- **Despesas vazias:** Linhas que só têm número (#D0001) mas sem descrição, credor ou valor

Isto previne poluição da BD com 1000+ registos vazios!

---

## 🗂️ Estrutura de Ficheiros

```
agora_web/
├── core/
│   ├── models.py                    # ImportacaoDados model
│   ├── admin.py                     # ImportacaoDadosAdmin view
│   ├── templates/
│   │   └── admin/
│   │       └── core/
│   │           └── importacaodados/
│   │               └── changelist.html   # Upload template
│   └── management/
│       └── commands/
│           └── import_from_excel.py      # Command reutilizado
└── uploads/                         # Ficheiros temporários (auto-criado)
```

---

## ⚠️ Limitações & Notas

### Performance
- Upload de ficheiros grandes (>5MB) pode demorar
- Processamento pode levar 10-30 segundos dependendo do volume de dados
- Interface não tem barra de progresso (aguardar até ver mensagem)

### Segurança
- Apenas admins com acesso ao Django Admin podem importar
- Ficheiros temporários são eliminados após processamento
- Validação de extensão impede upload de ficheiros perigosos

### Dados
- **Não duplica:** Atualiza registos existentes com base no `numero`
- **Prémios:** Soma TODOS os prémios do projeto (não substitui)
- **Boletins:** Agrega por (sócio, mês, ano) - soma valores

---

## 🐛 Troubleshooting

### Erro: "Ficheiro inválido"
**Causa:** Extensão não é `.xlsx`
**Solução:** Converter ficheiro para formato Excel 2007+ (.xlsx)

### Erro: "Aba X não encontrada"
**Causa:** Ficheiro não tem as abas obrigatórias
**Solução:** Verificar que Excel tem: FORNECEDORES, CLIENTES, PROJETOS, DESPESAS, BOLETINS

### Erro: "Erro na importação: ..."
**Causa:** Dados inválidos ou formato incorreto
**Solução:**
1. Verificar logs: `docker compose logs web`
2. Executar comando diretamente para ver erro detalhado:
   ```bash
   docker compose exec web python manage.py import_from_excel /path/to/file.xlsx
   ```

### Importação nunca termina
**Causa:** Ficheiro muito grande ou problema no servidor
**Solução:**
1. Verificar logs: `docker compose logs -f web`
2. Aumentar timeout no gunicorn (settings.py)
3. Usar comando de linha para ficheiros >10MB

---

## 📊 Comandos Úteis

```bash
# Ver logs durante importação
docker compose logs -f web

# Executar importação via CLI
docker compose exec web python manage.py import_from_excel excel/file.xlsx

# Limpar uploads antigos (se necessário)
docker compose exec web rm -rf uploads/*

# Verificar tamanho de ficheiros
docker compose exec web ls -lh uploads/
```

---

## 🔄 Workflow Típico

1. **Preparar Excel:**
   - Atualizar dados no Excel habitual
   - Garantir formato correto
   - Guardar como `.xlsx`

2. **Upload via Admin:**
   - Aceder a https://app.agoramediaproduction.pt/admin/
   - Core → Importação de Dados
   - Upload do ficheiro

3. **Verificar Resultados:**
   - Verificar mensagem de sucesso
   - Navegar para Projetos/Despesas/etc para confirmar dados

4. **Validação (opcional):**
   ```bash
   # Auditar importação
   docker compose exec web python manage.py auditar_importacao excel/file.xlsx
   ```

---

## 📝 Notas de Implementação

### Por que proxy model?
- Não precisamos armazenar histórico de importações
- Admin view funciona sem tabela na BD
- Código mais limpo e simples
- Evita complexidade desnecessária

### Por que reutilizar import_from_excel?
- Evita duplicação de lógica
- Mantém consistência
- Facilita manutenção
- 100% testado e funcional

### Por que não streaming/preview?
- Importação é rápida (<30s)
- Frequência de uso é baixa ("raramente")
- Simplicidade > Features complexas
- Preview adicionaria complexidade sem ganho real

---

## ✅ Status

| Feature | Status | Notas |
|---------|--------|-------|
| Upload Web | ✅ | Drag-and-drop funcional |
| Validação | ✅ | Extensão + formato |
| Importação | ✅ | Reutiliza comando existente |
| Feedback | ✅ | Mensagens de sucesso/erro |
| Dark Mode | ✅ | Tema Unfold integrado |
| Docs | ✅ | Este ficheiro |
| Testes | ✅ | Testado com ficheiros reais |

---

## 🚀 Próximos Passos (Opcional)

Se no futuro for necessário:

1. **Histórico de Importações:**
   - Criar modelo real com log de importações
   - Guardar: data, user, ficheiro, resultado

2. **Preview Antes de Importar:**
   - Mostrar primeiras linhas do Excel
   - Permitir confirmar antes de executar

3. **Barra de Progresso:**
   - WebSockets para feedback em tempo real
   - Indicador de % de progresso

4. **Agendamento:**
   - Celery task para importações agendadas
   - Integração com Google Drive API

**Mas para o caso de uso atual ("raramente"), o sistema está perfeito!**

---

**Última Atualização:** 2026-01-03
**Versão:** 2.1
