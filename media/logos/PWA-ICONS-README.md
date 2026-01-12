# 📱 Ícones PWA - Geração Necessária

## Status
⚠️ **PENDENTE**: Os ícones PWA precisam ser gerados a partir do `logo-pwa.svg`

## Ficheiros Necessários

Para a PWA funcionar completamente, precisamos:

### Ícones PWA
- `pwa-icon-192.png` - 192x192px (ícone padrão Android)
- `pwa-icon-512.png` - 512x512px (ícone splash screen)
- `pwa-icon-maskable-192.png` - 192x192px com safe zone (opcional)
- `pwa-icon-maskable-512.png` - 512x512px com safe zone (opcional)

### Favicon
- `favicon.ico` - 32x32px (fallback para browsers antigos)
- `favicon-16x16.png` - 16x16px
- `favicon-32x32.png` - 32x32px
- `apple-touch-icon.png` - 180x180px (iOS)

## Como Gerar

### Opção 1: Online (Rápido)
1. Ir a https://realfavicongenerator.net/
2. Upload do `logo-pwa.svg`
3. Configurar:
   - Background: Transparente ou #d4af37 (dourado Agora)
   - iOS: Safe zone para edges
   - Android: Maskable icon support
4. Download e extrair para `/media/logos/`

### Opção 2: ImageMagick (Local)
```bash
# Converter SVG para PNG em vários tamanhos
convert logo-pwa.svg -resize 192x192 pwa-icon-192.png
convert logo-pwa.svg -resize 512x512 pwa-icon-512.png
convert logo-pwa.svg -resize 180x180 apple-touch-icon.png
convert logo-pwa.svg -resize 32x32 favicon-32x32.png
convert logo-pwa.svg -resize 16x16 favicon-16x16.png

# Criar ICO multi-size
convert favicon-16x16.png favicon-32x32.png favicon.ico
```

### Opção 3: Inkscape (Melhor Qualidade)
```bash
inkscape logo-pwa.svg --export-type=png --export-width=192 --export-filename=pwa-icon-192.png
inkscape logo-pwa.svg --export-type=png --export-width=512 --export-filename=pwa-icon-512.png
inkscape logo-pwa.svg --export-type=png --export-width=180 --export-filename=apple-touch-icon.png
```

## Maskable Icons
Para criar ícones "maskable" (adaptativos Android 12+):
1. Adicionar padding de 20% em volta do logo
2. Garantir que conteúdo importante está na "safe zone" central (80%)
3. Usar fundo sólido ou transparente conforme design

## Após Gerar
1. Colocar todos os PNGs em `/media/logos/`
2. Verificar que `manifest.json` aponta para os ficheiros corretos
3. Testar PWA em Chrome DevTools > Application > Manifest
4. Testar instalação em dispositivo móvel

## Referências
- [PWA Icon Guidelines](https://web.dev/maskable-icon/)
- [Favicon Generator](https://realfavicongenerator.net/)
- [Maskable.app Editor](https://maskable.app/editor)
