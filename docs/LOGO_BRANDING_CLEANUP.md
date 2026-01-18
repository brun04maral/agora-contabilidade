# Logo & Branding Cleanup - v0.2.45

**Data:** 17 Janeiro 2026
**Versão:** v0.2.45

---

## 📋 Resumo

Limpeza completa do sistema de logos e favicons, consolidando para apenas 3 ficheiros essenciais e implementando colorização dinâmica via CSS.

---

## 🎯 Objetivos Alcançados

1. ✅ Remover logos antigos e duplicados
2. ✅ Simplificar estrutura de ficheiros media
3. ✅ Corrigir serving de media files via Gunicorn
4. ✅ Implementar colorização dinâmica do logo via CSS
5. ✅ Garantir favicon correto em todas as páginas

---

## 📁 Estrutura Final de Ficheiros

### Antes
```
media/logos/
├── favicon.svg                 (MANTER)
├── app_logo_sidebar.svg        (MANTER)
├── logo.svg                    (REMOVER)
├── logo-pwa.svg                (REMOVER)
├── logo_login.png              (REMOVER)
├── logo_login@2x.png           (REMOVER)
├── logo_sidebar.png            (REMOVER)
├── logo_sidebar@2x.png         (REMOVER)
├── ._app_logo_sidebar.svg      (REMOVER - macOS)
├── ._favicon.svg               (REMOVER - macOS)
└── ._apple-touch-icon.png.png  (REMOVER - macOS)
```

### Depois
```
media/logos/
├── favicon.svg                 (3.0 KB)
├── app_logo_sidebar.svg        (26 KB)
├── apple-touch-icon.png        (4.6 KB)
├── PWA-ICONS-README.md
└── README.md
```

---

## ⚙️ Configurações Atualizadas

### 1. Settings.py - UNFOLD Configuration

**Antes:**
```python
"SITE_LOGO": {
    "light": lambda request: "/media/logos/amp_logo_sidebar.svg",
    "dark": lambda request: "/media/logos/amp_logo_sidebar.svg",
},
"SITE_ICON": {
    "light": lambda request: "/media/logos/amp_logo.svg",
    "dark": lambda request: "/media/logos/amp_logo.svg",
},
```

**Depois:**
```python
"SITE_LOGO": {
    "light": lambda request: "/media/logos/app_logo_sidebar.svg",
    "dark": lambda request: "/media/logos/app_logo_sidebar.svg",
},
"SITE_ICON": {
    "light": lambda request: "/media/logos/app_logo_sidebar.svg",
    "dark": lambda request: "/media/logos/app_logo_sidebar.svg",
},
```

### 2. URLs.py - Media Files Serving

**Adicionado:**
```python
# Serve media files (works with Gunicorn)
from django.views.static import serve

urlpatterns += [
    path('media/<path:path>', serve, {'document_root': settings.MEDIA_ROOT}),
]
```

**Porquê?**
- Gunicorn não serve ficheiros media automaticamente
- `static()` helper não funciona bem com Gunicorn
- Solução: usar `serve` view diretamente

### 3. URLs.py - Favicon Redirect

**Adicionado:**
```python
# Favicon redirect to ensure correct one is served
path('favicon.ico', RedirectView.as_view(url='/media/logos/favicon.svg', permanent=True)),
```

**Porquê?**
- Browser faz pedido automático a `/favicon.ico`
- Django Rest Framework tinha favicon antigo em staticfiles
- Redirect permanente (301) resolve o conflito

---

## 🎨 Colorização Dinâmica do Logo

### admin_custom.css - Logo Sidebar

```css
/* Aplicar cor dourada ao logo da sidebar */
.sidebar-logo img,
.sidebar-logo svg,
[class*="sidebar"] img[src*="logo"],
[class*="sidebar"] svg,
img[src*="app_logo_sidebar"],
/* Unfold specific selectors */
.bg-primary-600 img,
.bg-primary-600 svg,
aside img[src*="logo"],
aside svg {
    filter: brightness(0) saturate(100%) invert(60%) sepia(42%) saturate(806%) hue-rotate(7deg) brightness(95%) contrast(87%);
}

/* Alternativa: usar currentColor se o SVG suportar */
.sidebar-logo svg path,
aside svg path {
    fill: #D4AF37 !important;
}

/* Para garantir que funciona em modo claro e escuro */
.dark .sidebar-logo svg path,
.dark aside svg path {
    fill: #D4AF37 !important;
}
```

**Cor Usada:** `#D4AF37` (Dourado Agora - primary-500)

---

## 🔧 Processo de Deploy

### Passo 1: Rebuild do Container
```bash
docker compose build web
```
**Necessário porque:** settings.py foi alterado (copiado durante build)

### Passo 2: Restart do Container
```bash
docker compose up -d web
```

### Passo 3: Collectstatic (se CSS alterado)
```bash
docker exec agora_web python manage.py collectstatic --noinput
```

### Passo 4: Verificação
```bash
# Testar media files
curl -I https://app.agoramediaproduction.pt/media/logos/favicon.svg

# Deve retornar: HTTP/2 200
```

---

## 📊 Resultados

### Antes
- ❌ Logos não apareciam (404)
- ❌ 6 ficheiros de logo duplicados
- ❌ Favicon antigo do DRF
- ❌ Media files não servidos via Gunicorn
- ❌ Logo com cor hardcoded no SVG

### Depois
- ✅ Todos os logos aparecem corretamente
- ✅ Apenas 3 ficheiros essenciais
- ✅ Favicon correto em todas as páginas
- ✅ Media files servidos via HTTPS
- ✅ Logo colorido dinamicamente via CSS (#D4AF37)

---

## 🔍 Troubleshooting

### Logo não aparece após alterações

**Causa:** Browser cache
**Solução:** Hard refresh (Ctrl+Shift+R) ou modo privado

### Alterações em settings.py não aplicadas

**Causa:** Container não foi rebuilded
**Solução:** `docker compose build web && docker compose up -d web`

### CSS não atualiza

**Causa:** Staticfiles não foram collected
**Solução:** `docker exec agora_web python manage.py collectstatic --noinput`

### Media files retornam 404

**Causa:** URL pattern não registado
**Solução:** Verificar que `urls.py` tem `path('media/<path:path>', serve, ...)`

---

## 📝 Notas Importantes

1. **Volume Mount:** `./media:/app/media` permite alterações imediatas em ficheiros media
2. **Settings Changes:** Requerem rebuild do container
3. **CSS Changes:** Requerem collectstatic
4. **Logo SVG:** Usar `currentColor` ou paths sem fill para permitir CSS styling

---

## 🔗 Referências

- [settings.py:175-195](../agora_web/config/settings.py#L175-L195) - Configuração UNFOLD
- [urls.py:27-30](../agora_web/config/urls.py#L27-L30) - Media serving
- [admin_custom.css:118-146](../agora_web/static/css/admin_custom.css#L118-L146) - Logo styling
- [CHANGELOG.md](../CHANGELOG.md#0245---2026-01-17) - Detalhes da versão

---

**Last Updated:** 2026-01-17
