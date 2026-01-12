# 🎨 Branding & PWA - Agora Contabilidade

## Status Implementação

✅ **Completo:**
- Manifest.json configurado
- Service Worker implementado
- Meta tags PWA no base template
- Login page customizada
- Footer personalizado
- Paleta de cores completa (Unfold)
- Environment badge (Development/Production)
- Templates customizados

⚠️ **Pendente:**
- Gerar ícones PWA em PNG (192x192, 512x512)
- Gerar apple-touch-icon.png (180x180)
- Gerar favicon.ico

## Assets Atuais

### Logos
- `logos/logo-pwa.svg` - Logo novo (amp logo) para PWA
- `logos/logo_sidebar.png` - Logo sidebar (100x60)
- `logos/logo_sidebar@2x.png` - Logo sidebar retina (200x120)
- `logos/logo_login.png` - Logo login (313x80)
- `logos/logo_login@2x.png` - Logo login retina (626x160)
- `logos/favicon.svg` - Favicon SVG (temporário, 'a' amarelo)

### PWA Files
- `/media/manifest.json` - PWA manifest
- `/media/sw.js` - Service Worker

## Como Gerar Ícones em Falta

### Opção Rápida: realfavicongenerator.net
1. Aceder a https://realfavicongenerator.net/
2. Upload `logos/logo-pwa.svg`
3. Configurar:
   - **iOS**: Safe zone, background transparente ou #d4af37
   - **Android**: Maskable icon com padding
   - **Favicon**: Multi-size ICO
4. Download ZIP
5. Copiar para `/media/logos/`:
   - `pwa-icon-192.png`
   - `pwa-icon-512.png`
   - `apple-touch-icon.png`
   - `favicon.ico`

### Verificar PWA

**Chrome DevTools:**
1. F12 → Application tab
2. Manifest: verificar ícones e configuração
3. Service Workers: verificar se registou
4. Lighthouse: audit PWA

**Testar Instalação:**
1. Chrome → três pontos → "Install Agora Contabilidade"
2. Ou no Android: "Add to Home Screen"

## Cores do Tema

**Primary (Dourado Agora):** `#d4af37` (RGB: 212, 175, 55)

Escala completa configurada em `settings.py`:
- 50: lightest
- 500: **brand color** (#d4af37)
- 950: darkest

## Templates Customizados

Criados em `/core/templates/unfold/`:

1. **layouts/base.html** - Meta tags PWA, Service Worker, install prompt
2. **login.html** - Login page com branding Agora
3. **layouts/base_simple.html** - Footer personalizado

## Funcionalidades PWA

✅ **Implementado:**
- Instalável (Add to Home Screen)
- Offline básico (Service Worker)
- Meta tags Apple/Android
- Theme color (#d4af37)
- Install prompt customizado
- Shortcuts (Projetos, Despesas, Saldos)

📝 **Próximos passos (opcional):**
- Push notifications
- Background sync
- Offline data caching
- App shortcuts icons

## Testar After Deploy

```bash
# 1. Rebuild Docker
docker compose down
docker compose up -d --build web

# 2. Verificar ficheiros servidos
curl -I https://app.agoramediaproduction.pt/media/manifest.json
curl -I https://app.agoramediaproduction.pt/media/sw.js

# 3. Testar no browser
# - Abrir https://app.agoramediaproduction.pt
# - F12 → Application → Manifest
# - F12 → Application → Service Workers
# - F12 → Lighthouse → PWA Audit
```

## Checklist Final

- [ ] Gerar ícones PWA (PNG 192, 512, apple-touch)
- [ ] Copiar ícones para `/media/logos/`
- [ ] Rebuild Docker
- [ ] Testar manifest.json
- [ ] Testar Service Worker
- [ ] Testar instalação PWA (Chrome Desktop + Android)
- [ ] Lighthouse audit (score PWA)
- [ ] Verificar login page branding
- [ ] Verificar footer em todas as páginas

## Links Úteis

- [PWA Guidelines](https://web.dev/progressive-web-apps/)
- [Manifest Generator](https://www.simicart.com/manifest-generator.html/)
- [Maskable Icon Editor](https://maskable.app/editor)
- [Favicon Generator](https://realfavicongenerator.net/)
- [PWA Builder](https://www.pwabuilder.com/)

---

**Última atualização:** 2026-01-12
**Versão:** 1.0.0
