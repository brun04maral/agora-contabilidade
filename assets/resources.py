# -*- coding: utf-8 -*-
"""
Assets Resources - Logo and Icon Management

Este módulo fornece funções para carregar logos SVG e ícones PNG para uso na aplicação.

LOGOS (SVG):
    - Armazenados em media/logos/
    - Convertidos dinamicamente para PNG em runtime
    - Escaláveis sem perda de qualidade
    - Uso: get_logo(svg_name, size=(width, height))

ÍCONES (PNG):
    - Armazenados como Base64 neste ficheiro
    - Embutidos no código para distribuição
    - Gerados automaticamente pelo script convert_icons_to_base64.py
    - Uso: get_icon(ICON_CONSTANT, size=(width, height))

EXEMPLOS DE USO:

    # Importar funções e constantes
    from assets.resources import get_logo, get_icon, DASHBOARD_ICON

    # Carregar logo SVG com tamanho específico
    logo_img = get_logo("agora_logo.svg", size=(200, 100))

    # Carregar ícone PNG embutido
    icon_img = get_icon(DASHBOARD_ICON, size=(32, 32))

    # Usar com CustomTkinter
    logo_ctk = ctk.CTkImage(light_image=logo_img, dark_image=logo_img, size=(200, 100))
    label = ctk.CTkLabel(parent, image=logo_ctk, text="")

COMPATIBILIDADE PYINSTALLER:
    - Logos SVG: Adicionar --add-data "media/logos;media/logos" ao comando PyInstaller
    - Ícones Base64: Funcionam automaticamente sem configuração extra

NOTA SOBRE WINDOWS:
    - No Windows, logos SVG requerem a biblioteca Cairo nativa (DLL)
    - Se Cairo não estiver disponível, a aplicação usará fallback de texto automaticamente
    - Para instalar Cairo no Windows: consulte WINDOWS_CAIRO.md
    - Ícones Base64 funcionam em todos os sistemas sem dependências extras
"""

import os
import sys
import base64
from io import BytesIO
from typing import Tuple, Optional
from PIL import Image

try:
    import cairosvg
    CAIROSVG_AVAILABLE = True
except (ImportError, OSError) as e:
    CAIROSVG_AVAILABLE = False
    if isinstance(e, OSError):
        # Cairo biblioteca nativa não está instalada (comum no Windows)
        pass  # Silenciar - mostraremos aviso apenas quando tentar usar
    else:
        print("⚠️  AVISO: cairosvg não instalado. Logos SVG não estarão disponíveis.")
        print("   Instale com: pip install cairosvg")


# =============================================================================
# FUNÇÕES DE CARREGAMENTO
# =============================================================================

def get_logo(svg_filename: str, size: Tuple[int, int] = (200, 100)) -> Optional[Image.Image]:
    """
    Carrega um logo SVG da pasta media/logos/ e converte para PIL.Image.

    Args:
        svg_filename: Nome do ficheiro SVG (ex: "agora_logo.svg")
        size: Tuplo (width, height) para o tamanho final da imagem

    Returns:
        PIL.Image object ou None se houver erro

    Exemplo:
        logo = get_logo("agora_logo.svg", size=(300, 150))
        if logo:
            ctk_image = ctk.CTkImage(light_image=logo, size=(300, 150))
    """
    if not CAIROSVG_AVAILABLE:
        # Silenciar - fallback será usado automaticamente
        return None

    # Determinar o caminho correto (dev vs PyInstaller)
    if getattr(sys, 'frozen', False):
        # Executável empacotado com PyInstaller
        base_path = sys._MEIPASS
    else:
        # Modo de desenvolvimento
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    svg_path = os.path.join(base_path, "media", "logos", svg_filename)

    if not os.path.exists(svg_path):
        print(f"❌ Erro: Logo SVG não encontrado: {svg_path}")
        return None

    try:
        # Converter SVG para PNG em memória
        png_data = cairosvg.svg2png(
            url=svg_path,
            output_width=size[0],
            output_height=size[1]
        )

        # Criar PIL.Image a partir dos dados PNG
        image = Image.open(BytesIO(png_data))
        return image

    except Exception as e:
        print(f"❌ Erro ao carregar logo '{svg_filename}': {e}")
        return None


def get_logo_with_fallback(logo_name: str, size: Tuple[int, int], suffix: str = "") -> Optional[Image.Image]:
    """
    Carrega logo com fallback inteligente: SVG → PNG → None

    Esta é a função RECOMENDADA para usar na aplicação.
    Funciona em desenvolvimento (SVG) e produção Windows (PNG pré-gerado).

    Args:
        logo_name: Nome base do logo sem extensão (ex: "logo")
        size: Tuplo (width, height) para o tamanho final
        suffix: Sufixo opcional para identificar o tamanho (ex: "sidebar", "login")

    Returns:
        PIL.Image object ou None se nenhum logo for encontrado

    Comportamento:
        1. Tenta carregar SVG (se Cairo disponível)
        2. Tenta carregar PNG pré-gerado (media/logos/{logo_name}_{suffix}.png)
        3. Retorna None (UI usará fallback de texto)

    Exemplo:
        # Sidebar (tenta logo.svg → logo_sidebar.png → None)
        logo = get_logo_with_fallback("logo", size=(100, 60), suffix="sidebar")

        # Login (tenta logo.svg → logo_login.png → None)
        logo = get_logo_with_fallback("logo", size=(313, 80), suffix="login")
    """
    # 1. Tentar SVG primeiro (desenvolvimento)
    if CAIROSVG_AVAILABLE:
        svg_logo = get_logo(f"{logo_name}.svg", size=size)
        if svg_logo:
            return svg_logo

    # 2. Tentar PNG pré-gerado (produção/Windows)
    if suffix:
        png_filename = f"{logo_name}_{suffix}.png"
    else:
        png_filename = f"{logo_name}_{size[0]}x{size[1]}.png"

    # Determinar caminho
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    png_path = os.path.join(base_path, "media", "logos", png_filename)

    if os.path.exists(png_path):
        try:
            image = Image.open(png_path)
            # Garantir que está no tamanho correto
            if image.size != size:
                image = image.resize(size, Image.Resampling.LANCZOS)
            return image
        except Exception as e:
            pass  # Silenciar e seguir para fallback None

    # 3. Fallback final: None (UI usará texto)
    return None


def get_icon(base64_string: str, size: Optional[Tuple[int, int]] = None) -> Optional[Image.Image]:
    """
    Descodifica um ícone Base64 e retorna como PIL.Image.

    Args:
        base64_string: String Base64 do ícone (use as constantes deste módulo)
        size: Tuplo (width, height) opcional para redimensionar. Se None, usa tamanho original

    Returns:
        PIL.Image object ou None se houver erro

    Exemplo:
        icon = get_icon(DASHBOARD_ICON, size=(32, 32))
        if icon:
            ctk_image = ctk.CTkImage(light_image=icon, size=(32, 32))
    """
    if not base64_string:
        print("❌ Erro: String Base64 vazia")
        return None

    try:
        # Descodificar Base64
        image_data = base64.b64decode(base64_string)

        # Criar PIL.Image
        image = Image.open(BytesIO(image_data))

        # Redimensionar se necessário
        if size:
            image = image.resize(size, Image.Resampling.LANCZOS)

        return image

    except Exception as e:
        print(f"❌ Erro ao descodificar ícone: {e}")
        return None


# =============================================================================
# CONSTANTES DE ÍCONES (BASE64)
# =============================================================================
#
# NOTA: Estas constantes são geradas automaticamente pelo script
# convert_icons_to_base64.py
#
# Para atualizar os ícones:
#   1. Coloque os ficheiros PNG em media/icons/
#   2. Execute: python convert_icons_to_base64.py
#   3. O script irá atualizar esta secção automaticamente
#
# =============================================================================

# --- INÍCIO DA SECÇÃO AUTO-GERADA ---
# NÃO EDITAR MANUALMENTE - Este conteúdo é gerado por convert_icons_to_base64.py

# Ícones disponíveis:
# - BOLETINS (boletins.png)
# - CLIENTES (clientes.png)
# - DASHBOARD (dashboard.png)
# - DESPESAS (despesas.png)
# - EQUIPAMENTO (equipamento.png)
# - FORNECEDORES (fornecedores.png)
# - INFO (info.png)
# - INS (ins.png)
# - ORCAMENTOS (orcamentos.png)
# - OUTS (outs.png)
# - PROJETOS (projetos.png)
# - RELATORIOS (relatorios.png)
# - SALDOSPESSOAIS (saldospessoais.png)

# Ícone: boletins.png
BOLETINS = (
    "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"
)

# Ícone: clientes.png
CLIENTES = (
    "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"
)

# Ícone: dashboard.png
DASHBOARD = (
    "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"
    "F1100YXp8v93BmSQ3ev5YQAAAABJRU5ErkJggg=="
)

# Ícone: despesas.png
DESPESAS = (
    "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"
    "gg=="
)

# Ícone: equipamento.png
EQUIPAMENTO = (
    "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"
)

# Ícone: fornecedores.png
FORNECEDORES = (
    "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"
)

# Ícone: info.png
INFO = (
    "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"
)

# Ícone: ins.png
INS = (
    "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"
)

# Ícone: orcamentos.png
ORCAMENTOS = (
    "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"
    "TGEKU5gggf8DtwfxJE66doMAAAAASUVORK5CYII="
)

# Ícone: outs.png
OUTS = (
    "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"
    "dowd/gYAAAAASUVORK5CYII="
)

# Ícone: projetos.png
PROJETOS = (
    "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"
)

# Ícone: relatorios.png
RELATORIOS = (
    "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"
)

# Ícone: saldospessoais.png
SALDOSPESSOAIS = (
    "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"
)

# --- FIM DA SECÇÃO AUTO-GERADA ---


# =============================================================================
# FUNÇÕES HELPER ADICIONAIS
# =============================================================================

def list_available_logos() -> list:
    """
    Lista todos os logos SVG disponíveis na pasta media/logos/

    Returns:
        Lista de nomes de ficheiros SVG
    """
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    logos_path = os.path.join(base_path, "media", "logos")

    if not os.path.exists(logos_path):
        return []

    return [f for f in os.listdir(logos_path) if f.endswith('.svg')]


def get_logo_path(svg_filename: str) -> Optional[str]:
    """
    Retorna o caminho completo para um logo SVG.
    Útil para debug ou uso direto.

    Args:
        svg_filename: Nome do ficheiro SVG

    Returns:
        Caminho completo ou None se não existir
    """
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    svg_path = os.path.join(base_path, "media", "logos", svg_filename)

    return svg_path if os.path.exists(svg_path) else None


# =============================================================================
# EXEMPLOS DE USO E TESTES
# =============================================================================

if __name__ == "__main__":
    """
    Exemplos de uso e testes das funções
    """
    print("=" * 70)
    print("ASSETS RESOURCES - Testes e Exemplos")
    print("=" * 70)
    print()

    # Listar logos disponíveis
    print("📁 Logos SVG disponíveis:")
    logos = list_available_logos()
    if logos:
        for logo in logos:
            print(f"   - {logo}")
    else:
        print("   Nenhum logo encontrado em media/logos/")
    print()

    # Testar carregamento de logo (se existir)
    if logos:
        test_logo = logos[0]
        print(f"🔄 Testando carregamento: {test_logo}")
        logo_img = get_logo(test_logo, size=(200, 100))
        if logo_img:
            print(f"   ✅ Logo carregado com sucesso: {logo_img.size}")
        else:
            print(f"   ❌ Falha ao carregar logo")
    print()

    # Informação sobre cairosvg
    print(f"📦 cairosvg disponível: {CAIROSVG_AVAILABLE}")
    if not CAIROSVG_AVAILABLE:
        print("   ⚠️  Instale com: pip install cairosvg")
    print()

    print("=" * 70)
    print("Para mais exemplos, consulte a documentação no topo deste ficheiro")
    print("=" * 70)
