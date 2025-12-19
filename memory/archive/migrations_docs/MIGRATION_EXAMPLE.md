# 🔄 Migração para o Novo Sistema de Assets

Este documento mostra como migrar código existente que usa logos/ícones PNG diretamente para o novo sistema com SVG e Base64.

## ✅ Benefícios da Migração

- ✨ Logos SVG escaláveis sem perda de qualidade
- 📦 Ícones embutidos (sem ficheiros externos)
- 🚀 Melhor compatibilidade com PyInstaller
- 🎯 API consistente e fácil de usar

## 📝 Exemplo: Sidebar

### ❌ ANTES (código antigo)

```python
# ui/components/sidebar.py - ANTIGO
import os
from PIL import Image
import customtkinter as ctk

class Sidebar(ctk.CTkFrame):
    def create_widgets(self):
        # Logo hardcoded como PNG
        logo_path = os.path.join(
            os.path.dirname(__file__),
            "..", "..",
            "media",
            "a + agora media production@0.5x.png"
        )

        if os.path.exists(logo_path):
            logo_image = Image.open(logo_path)
            logo_ctk = ctk.CTkImage(
                light_image=logo_image,
                dark_image=logo_image,
                size=(100, 60)
            )
            logo_label = ctk.CTkLabel(
                logo_frame,
                image=logo_ctk,
                text=""
            )
            logo_label.pack(pady=(0, 10))
```

**Problemas:**
- Caminho relativo complexo
- PNG fixo (não escalável)
- Ficheiro externo necessário para distribuição
- Erro silencioso se ficheiro não existir

### ✅ DEPOIS (código novo)

```python
# ui/components/sidebar.py - NOVO
import customtkinter as ctk
from assets.resources import get_logo

class Sidebar(ctk.CTkFrame):
    def create_widgets(self):
        # Logo SVG escalável
        logo_image = get_logo("agora_logo.svg", size=(100, 60))

        if logo_image:
            logo_ctk = ctk.CTkImage(
                light_image=logo_image,
                dark_image=logo_image,
                size=(100, 60)
            )
            logo_label = ctk.CTkLabel(
                logo_frame,
                image=logo_ctk,
                text=""
            )
            logo_label.pack(pady=(0, 10))
        else:
            # Fallback se logo não carregar
            logo_label = ctk.CTkLabel(
                logo_frame,
                text="AGORA",
                font=ctk.CTkFont(size=20, weight="bold")
            )
            logo_label.pack(pady=(0, 10))
```

**Melhorias:**
- ✅ Caminho simplificado
- ✅ SVG escalável
- ✅ Erro tratado com fallback
- ✅ Código mais limpo

## 📝 Exemplo: Login Screen

### ❌ ANTES

```python
# ui/screens/login.py - ANTIGO
import os
from PIL import Image
import customtkinter as ctk

class LoginScreen(ctk.CTkFrame):
    def create_widgets(self):
        logo_path = os.path.join(
            os.path.dirname(__file__),
            "..", "..",
            "media",
            "AGORA media production@0.5x.png"
        )

        if os.path.exists(logo_path):
            logo_image = Image.open(logo_path)
            logo_ctk = ctk.CTkImage(
                light_image=logo_image,
                dark_image=logo_image,
                size=(313, 80)
            )
            title_label = ctk.CTkLabel(
                login_container,
                image=logo_ctk,
                text=""
            )
            title_label.grid(row=0, column=0, pady=(100, 20))
```

### ✅ DEPOIS

```python
# ui/screens/login.py - NOVO
import customtkinter as ctk
from assets.resources import get_logo

class LoginScreen(ctk.CTkFrame):
    def create_widgets(self):
        logo_image = get_logo("agora_logo.svg", size=(313, 80))

        if logo_image:
            logo_ctk = ctk.CTkImage(
                light_image=logo_image,
                dark_image=logo_image,
                size=(313, 80)
            )
            title_label = ctk.CTkLabel(
                login_container,
                image=logo_ctk,
                text=""
            )
            title_label.grid(row=0, column=0, pady=(100, 20))
        else:
            # Fallback para texto
            title_label = ctk.CTkLabel(
                login_container,
                text="AGORA Media Production",
                font=ctk.CTkFont(size=24, weight="bold")
            )
            title_label.grid(row=0, column=0, pady=(100, 20))
```

## 📝 Exemplo: Menu com Ícones

### ✅ NOVO (não existia antes)

```python
# ui/components/menu.py - NOVO
import customtkinter as ctk
from assets.resources import get_icon, DASHBOARD_ICON, PROJECTS_ICON, REPORTS_ICON

class NavigationMenu(ctk.CTkFrame):
    def __init__(self, parent, on_menu_select):
        super().__init__(parent)
        self.on_menu_select = on_menu_select

        # Definir itens do menu com ícones
        self.menu_items = [
            ("Dashboard", "dashboard", DASHBOARD_ICON),
            ("Projetos", "projetos", PROJECTS_ICON),
            ("Relatórios", "relatorios", REPORTS_ICON),
        ]

        self.create_menu_buttons()

    def create_menu_buttons(self):
        for label, key, icon_constant in self.menu_items:
            # Carregar ícone
            icon_img = get_icon(icon_constant, size=(24, 24))

            if icon_img:
                icon_ctk = ctk.CTkImage(
                    light_image=icon_img,
                    dark_image=icon_img,
                    size=(24, 24)
                )
                btn = ctk.CTkButton(
                    self,
                    image=icon_ctk,
                    text=label,
                    compound="left",
                    command=lambda k=key: self.on_menu_select(k),
                    anchor="w",
                    height=40
                )
            else:
                # Fallback sem ícone
                btn = ctk.CTkButton(
                    self,
                    text=label,
                    command=lambda k=key: self.on_menu_select(k),
                    anchor="w",
                    height=40
                )

            btn.pack(fill="x", padx=10, pady=5)
```

## 🔄 Passos para Migrar Ficheiro Existente

### 1. Preparar Logos SVG

```bash
# Mover logos SVG para pasta correta
cp "media/AGORA media production (yellow).svg" media/logos/agora_logo.svg
```

### 2. Preparar Ícones PNG (se necessário)

```bash
# Mover ícones para pasta correta
cp dashboard.png media/icons/
cp projects.png media/icons/
cp reports.png media/icons/

# Converter para Base64
python convert_icons_to_base64.py
```

### 3. Atualizar Imports

```python
# ANTES
import os
from PIL import Image

# DEPOIS
from assets.resources import get_logo, get_icon, ICON_NAME
```

### 4. Substituir Código de Carregamento

```python
# ANTES
logo_path = os.path.join(os.path.dirname(__file__), "..", "..", "media", "logo.png")
if os.path.exists(logo_path):
    logo_image = Image.open(logo_path)

# DEPOIS
logo_image = get_logo("logo.svg", size=(200, 100))
if logo_image:
    # usar logo_image
```

### 5. Adicionar Fallbacks

```python
# Sempre adicione fallback para melhor UX
logo_image = get_logo("logo.svg", size=(200, 100))

if logo_image:
    # Usar imagem
    logo_ctk = ctk.CTkImage(light_image=logo_image, size=(200, 100))
    label = ctk.CTkLabel(parent, image=logo_ctk, text="")
else:
    # Fallback para texto
    label = ctk.CTkLabel(parent, text="AGORA", font=("bold", 20))
```

## 📊 Checklist de Migração

- [ ] Identificar todos os logos usados na aplicação
- [ ] Converter logos para SVG (se necessário)
- [ ] Mover logos SVG para `media/logos/`
- [ ] Identificar todos os ícones usados
- [ ] Mover ícones PNG para `media/icons/`
- [ ] Executar `python convert_icons_to_base64.py`
- [ ] Atualizar imports nos ficheiros Python
- [ ] Substituir código de carregamento direto por `get_logo()` / `get_icon()`
- [ ] Adicionar fallbacks apropriados
- [ ] Testar aplicação
- [ ] Remover ficheiros PNG antigos de `media/` (opcional)
- [ ] Atualizar `.gitignore` se necessário
- [ ] Commit das alterações

## 🎯 Ficheiros a Atualizar

Com base no código existente:

1. **ui/components/sidebar.py** - Logo principal
2. **ui/screens/login.py** - Logo de login
3. Qualquer outro componente que use imagens

## ⚠️ Notas Importantes

1. **Compatibilidade:** Código antigo continuará a funcionar, migração é opcional mas recomendada
2. **Performance:** SVG tem conversão inicial, mas resultados são cached pelo PIL
3. **Fallbacks:** Sempre forneça fallback para melhor experiência de utilizador
4. **Testing:** Teste em ambiente dev antes de distribuir com PyInstaller

## 🚀 Próximos Passos

Após a migração:

1. Teste a aplicação completamente
2. Verifique se todos os logos/ícones aparecem corretamente
3. Teste diferentes tamanhos de janela (logos SVG devem escalar bem)
4. Crie build com PyInstaller e teste executável
5. Remova ficheiros PNG antigos se tudo funcionar

---

💡 **Dica:** Faça a migração gradualmente, um componente de cada vez, para facilitar debugging!
