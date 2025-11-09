# 🎨 Logos e Assets - Guia Completo

## 📋 O Que São Assets?

Assets são os recursos visuais da aplicação:
- **Logos PNG**: Imagens pré-geradas para produção (mantidos **manualmente**)
- **Logo SVG**: Ficheiro vetorial para desenvolvimento (apenas referência)
- **Ícones Base64**: Ícones embutidos no código

## 🔄 Sistema de Fallback Inteligente

A aplicação usa um sistema de 3 níveis de fallback para logos:

```
1. SVG (Cairo) → 2. PNG pré-gerado → 3. Texto
```

### Desenvolvimento (Linux/Mac com Cairo)
- ✅ Usa SVG diretamente
- ✅ Qualidade perfeita em qualquer tamanho
- ✅ Sem necessidade de PNGs

### Produção (Windows/Sem Cairo)
- ✅ Usa PNG pré-gerado
- ✅ Excelente qualidade (2x retina ready)
- ✅ Funciona sem instalação de Cairo

### Fallback Final
- ✅ Texto "AGORA" e "AGORA Media Production"
- ✅ Sempre funciona

## 🎨 Manutenção dos Logos PNG (Manual)

Os logos PNG são **mantidos manualmente** no repositório.

### 📁 Nomenclatura Obrigatória

Os seguintes ficheiros devem estar em `media/logos/`:

- `logo_sidebar.png` - Sidebar (100x60px)
- `logo_sidebar@2x.png` - Sidebar retina (200x120px)
- `logo_login.png` - Login (313x80px)
- `logo_login@2x.png` - Login retina (626x160px)

### ✅ Requisitos de Qualidade

- **Formato**: PNG com canal alpha (RGBA)
- **Fundo**: Completamente transparente
- **Qualidade**: Alta resolução, sem artefactos ou "pixelização"
- **Anti-aliasing**: Bordas suaves

### 🔄 Como Atualizar

1. **Gerar PNGs** nos tamanhos especificados (usar Photoshop, GIMP, etc.)
2. **Garantir transparência** e qualidade
3. **Substituir ficheiros** em `media/logos/`
4. **Commit e push**:

```bash
git add media/logos/*.png
git commit -m "🎨 Atualizar logos PNG"
git push
```

## 🔧 Como Funciona Internamente

### Código da Aplicação

```python
from assets.resources import get_logo_with_fallback

# Sidebar
logo = get_logo_with_fallback("logo", size=(100, 60), suffix="sidebar")
# Tenta: logo.svg → logo_sidebar.png → None

# Login
logo = get_logo_with_fallback("logo", size=(313, 80), suffix="login")
# Tenta: logo.svg → logo_login.png → None
```

### Lógica de Fallback

1. **Cairo disponível?**
   - ✅ Sim → Converte SVG para PNG em memória
   - ❌ Não → Vai para passo 2

2. **PNG pré-gerado existe?**
   - ✅ Sim → Carrega PNG
   - ❌ Não → Retorna None

3. **Logo é None?**
   - UI usa fallback de texto

## 📦 Compilação com PyInstaller

### Adicionar Assets ao Build

```bash
# Incluir logos PNG no executável
pyinstaller --add-data "media/logos/*.png;media/logos" main.py
```

### Verificar Build

```bash
# O executável deve conter:
# - media/logos/logo_sidebar.png
# - media/logos/logo_sidebar@2x.png
# - media/logos/logo_login.png
# - media/logos/logo_login@2x.png
```

## ➕ Adicionar Novos Logos

### 1. Adicionar SVG

```bash
cp novo_logo.svg media/logos/
```

### 2. Configurar Tamanhos

Editar `build_assets.py`:

```python
LOGO_SIZES = {
    "logo": [
        (100, 60, "sidebar"),
        (313, 80, "login"),
    ],
    "novo_logo": [  # ← Adicionar aqui
        (200, 100, "dashboard"),
        (150, 75, "header"),
    ]
}
```

### 3. Gerar PNGs

```bash
python3 build_assets.py
```

### 4. Usar no Código

```python
from assets.resources import get_logo_with_fallback

logo = get_logo_with_fallback("novo_logo", size=(200, 100), suffix="dashboard")
```

## 🧪 Testes

### Testar com Cairo (Development)

```bash
python3 -c "
from assets.resources import get_logo_with_fallback, CAIROSVG_AVAILABLE

print(f'Cairo: {CAIROSVG_AVAILABLE}')

logo = get_logo_with_fallback('logo', size=(100, 60), suffix='sidebar')
print(f'Logo: {logo.size if logo else None}')
"
```

### Testar sem Cairo (Windows Simulado)

```bash
python3 -c "
import sys
sys.modules['cairosvg'] = None

from assets.resources import get_logo_with_fallback

logo = get_logo_with_fallback('logo', size=(100, 60), suffix='sidebar')
print(f'Logo PNG: {logo.size if logo else None}')
"
```

## ❓ FAQ

### Preciso gerar PNGs toda vez?

**Não!** Só quando:
- Atualizar logo SVG
- Adicionar novo tamanho
- Preparar build para distribuição

### E se não tiver Cairo?

Podes:
1. Executar `build_assets.py` num sistema com Cairo
2. Copiar PNGs gerados para Windows
3. Ou usar fallback de texto (funciona sempre)

### Os PNGs ocupam muito espaço?

Não! No total:
- 4 PNGs ≈ 12KB
- Muito pequeno, sem impacto

### Posso usar só PNGs sempre?

Sim! Mas:
- SVG mantém qualidade perfeita
- Melhor para desenvolvimento
- PNG é só para produção/Windows

## 📊 Resumo de Ficheiros

| Ficheiro | Propósito |
|----------|-----------|
| `build_assets.py` | Script para gerar PNGs |
| `assets/resources.py` | Funções de carregamento |
| `media/logos/*.svg` | Logos originais (vetoriais) |
| `media/logos/*.png` | Logos pré-gerados (produção) |
| `ui/*/sidebar.py` | Usa `get_logo_with_fallback()` |
| `ui/*/login.py` | Usa `get_logo_with_fallback()` |

## ✅ Checklist de Build

Antes de fazer release:

- [ ] Executar `python3 build_assets.py`
- [ ] Verificar PNGs gerados em `media/logos/`
- [ ] Fazer commit dos PNGs
- [ ] Testar aplicação sem Cairo
- [ ] Compilar com PyInstaller
- [ ] Testar executável em Windows

---

💡 **Dica**: Execute `build_assets.py` sempre que atualizar logos SVG!
