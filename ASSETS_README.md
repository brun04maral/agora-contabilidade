# 🎨 Sistema de Assets - Logos e Ícones

Sistema completo de gestão de logos SVG e ícones PNG para a aplicação Agora Media Contabilidade.

## 📁 Estrutura de Pastas

```
agora-contabilidade/
├── media/
│   ├── logos/          # Logos em formato SVG (escaláveis)
│   └── icons/          # Ícones em formato PNG (convertidos para Base64)
├── assets/
│   ├── __init__.py
│   └── resources.py    # Funções e constantes de assets
└── convert_icons_to_base64.py  # Script de conversão
```

## 🚀 Início Rápido

### 1. Instalar Dependências

```bash
pip install -r requirements.txt
```

Isto instalará `cairosvg` necessário para conversão de SVG.

### 2. Adicionar Logos (SVG)

Coloque os ficheiros SVG em `media/logos/`:

```bash
cp seu_logo.svg media/logos/
```

### 3. Adicionar Ícones (PNG)

Coloque os ficheiros PNG em `media/icons/`:

```bash
cp dashboard.png media/icons/
cp settings.png media/icons/
```

### 4. Converter Ícones para Base64

Execute o script de conversão:

```bash
python convert_icons_to_base64.py
```

Isto irá:
- Ler todos os PNG de `media/icons/`
- Converter para Base64
- Atualizar `assets/resources.py` automaticamente
- Criar constantes como `DASHBOARD_ICON`, `SETTINGS_ICON`, etc.

## 💻 Uso no Código

### Importar Recursos

```python
from assets.resources import get_logo, get_icon, DASHBOARD_ICON
```

### Carregar Logo SVG

```python
# Carregar logo com tamanho específico
logo_img = get_logo("agora_logo.svg", size=(200, 100))

if logo_img:
    # Usar com CustomTkinter
    logo_ctk = ctk.CTkImage(
        light_image=logo_img,
        dark_image=logo_img,
        size=(200, 100)
    )
    label = ctk.CTkLabel(parent, image=logo_ctk, text="")
```

### Carregar Ícone PNG (Base64)

```python
# Carregar ícone com redimensionamento
icon_img = get_icon(DASHBOARD_ICON, size=(32, 32))

if icon_img:
    # Usar com CustomTkinter
    icon_ctk = ctk.CTkImage(
        light_image=icon_img,
        dark_image=icon_img,
        size=(32, 32)
    )
    button = ctk.CTkButton(parent, image=icon_ctk, text="Dashboard")
```

### Listar Logos Disponíveis

```python
from assets.resources import list_available_logos

logos = list_available_logos()
for logo in logos:
    print(f"Logo disponível: {logo}")
```

## 📋 Nomenclatura de Constantes

O script `convert_icons_to_base64.py` converte nomes de ficheiros automaticamente:

| Ficheiro PNG | Constante Python |
|--------------|------------------|
| `dashboard.png` | `DASHBOARD` |
| `dashboard_icon.png` | `DASHBOARD_ICON` |
| `my-icon.png` | `MY_ICON` |
| `ProjectIcon.png` | `PROJECT_ICON` |
| `icon.test.png` | `ICON_TEST` |

**Regras:**
- Extensão removida
- Hífens e pontos convertidos para underscore
- CamelCase convertido para snake_case
- Tudo em UPPERCASE

## 🔧 Exemplos Práticos

### Exemplo 1: Sidebar com Logo

```python
import customtkinter as ctk
from assets.resources import get_logo

class Sidebar(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)

        # Carregar logo
        logo_img = get_logo("agora_logo.svg", size=(150, 75))

        if logo_img:
            logo_ctk = ctk.CTkImage(
                light_image=logo_img,
                dark_image=logo_img,
                size=(150, 75)
            )
            logo_label = ctk.CTkLabel(
                self,
                image=logo_ctk,
                text=""
            )
            logo_label.pack(pady=20)
```

### Exemplo 2: Botão com Ícone

```python
import customtkinter as ctk
from assets.resources import get_icon, SETTINGS_ICON

class SettingsButton(ctk.CTkButton):
    def __init__(self, parent, **kwargs):
        # Carregar ícone
        icon_img = get_icon(SETTINGS_ICON, size=(24, 24))

        if icon_img:
            icon_ctk = ctk.CTkImage(
                light_image=icon_img,
                dark_image=icon_img,
                size=(24, 24)
            )
            super().__init__(
                parent,
                image=icon_ctk,
                text="Definições",
                compound="left",
                **kwargs
            )
        else:
            super().__init__(
                parent,
                text="⚙️ Definições",
                **kwargs
            )
```

### Exemplo 3: Menu com Múltiplos Ícones

```python
import customtkinter as ctk
from assets.resources import get_icon, DASHBOARD_ICON, PROJECTS_ICON, REPORTS_ICON

class MenuBar(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)

        # Definir ícones e labels
        menu_items = [
            ("Dashboard", DASHBOARD_ICON),
            ("Projetos", PROJECTS_ICON),
            ("Relatórios", REPORTS_ICON),
        ]

        # Criar botões
        for text, icon_constant in menu_items:
            icon_img = get_icon(icon_constant, size=(20, 20))

            if icon_img:
                icon_ctk = ctk.CTkImage(
                    light_image=icon_img,
                    size=(20, 20)
                )
                btn = ctk.CTkButton(
                    self,
                    image=icon_ctk,
                    text=text,
                    compound="left"
                )
            else:
                btn = ctk.CTkButton(self, text=text)

            btn.pack(pady=5, padx=10)
```

## 📦 Compatibilidade com PyInstaller

### Para Logos SVG

Adicionar ao comando PyInstaller:

```bash
pyinstaller --add-data "media/logos;media/logos" main.py
```

Ou no ficheiro `.spec`:

```python
a = Analysis(
    ['main.py'],
    datas=[('media/logos', 'media/logos')],
    ...
)
```

### Para Ícones PNG (Base64)

✅ **Funcionam automaticamente!** Não é necessária configuração extra pois os ícones estão embutidos como strings Base64 no código.

## 🛠️ Manutenção

### Atualizar Ícones

1. Adicione/substitua ficheiros PNG em `media/icons/`
2. Execute: `python convert_icons_to_base64.py`
3. As constantes em `assets/resources.py` serão atualizadas automaticamente

### Adicionar Novos Logos

1. Coloque o ficheiro SVG em `media/logos/`
2. Use imediatamente: `get_logo("novo_logo.svg", size=(200, 100))`

### Verificar Assets Disponíveis

```python
python assets/resources.py
```

Isto irá:
- Listar todos os logos SVG disponíveis
- Testar carregamento de um logo
- Verificar se cairosvg está instalado

## ❓ Troubleshooting

### Erro: "cairosvg não instalado"

```bash
pip install cairosvg
```

### Logo SVG não carrega

1. Verifique se o ficheiro existe em `media/logos/`
2. Verifique se o nome está correto (case-sensitive)
3. Execute `python assets/resources.py` para diagnóstico

### Ícone não aparece

1. Verifique se executou `convert_icons_to_base64.py`
2. Verifique se o ficheiro PNG estava em `media/icons/`
3. Confirme que a constante foi importada corretamente

### Imagem borrada/pixelizada

**Para logos SVG:**
- Use tamanhos adequados na função `get_logo()`
- SVG é vetorial, não perde qualidade ao redimensionar

**Para ícones PNG:**
- Forneça ícones em alta resolução (pelo menos 2x o tamanho de uso)
- Use `size` apropriado em `get_icon()`

## 🎯 Boas Práticas

1. **Use SVG para logos** - Escalável, perfeito para diferentes tamanhos
2. **Use PNG para ícones pequenos** - Mais rápido, embutido no código
3. **Nomenclatura consistente** - Use snake_case ou hífens nos nomes de ficheiros
4. **Tamanhos apropriados** - Forneça ícones PNG em 2x resolução (ex: 64x64 para uso em 32x32)
5. **Teste após conversão** - Execute `python assets/resources.py` para verificar
6. **Commit os assets** - Não esqueça de fazer commit de `assets/resources.py` após converter ícones

## 📚 Referências

- [cairosvg Documentation](https://cairosvg.org/)
- [Pillow (PIL) Documentation](https://pillow.readthedocs.io/)
- [CustomTkinter Documentation](https://customtkinter.tomschimansky.com/)

---

💡 **Dica:** Execute `python convert_icons_to_base64.py` sempre que adicionar ou atualizar ícones!
