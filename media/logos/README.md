# 🎨 Logos PNG - Nomenclatura

Os logos PNG são mantidos **manualmente** nesta pasta para uso em produção Windows (sem Cairo).

## 📁 Ficheiros Necessários

Os seguintes PNGs devem estar presentes para a aplicação funcionar corretamente:

### Logo Principal

- `logo_sidebar.png` - Sidebar (100x60px)
- `logo_sidebar@2x.png` - Sidebar retina (200x120px)
- `logo_login.png` - Login (313x80px)
- `logo_login@2x.png` - Login retina (626x160px)

### Requisitos

- **Formato**: PNG com transparência (RGBA)
- **Fundo**: Transparente (sem fundo branco)
- **Qualidade**: Alta resolução, sem artefactos

## 🔄 Atualização

Quando atualizar os logos:

1. Gerar PNGs nos tamanhos especificados acima
2. Garantir transparência e qualidade
3. Substituir ficheiros nesta pasta
4. Fazer commit e push

## 💡 Fallback

Se os PNGs não estiverem disponíveis:
- **Desenvolvimento (com Cairo)**: Usa `logo.svg`
- **Produção (sem Cairo)**: Usa texto "AGORA" como fallback
