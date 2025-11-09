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
except ImportError:
    CAIROSVG_AVAILABLE = False
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
        print(f"❌ Erro: cairosvg não disponível. Não é possível carregar '{svg_filename}'")
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

# Ícones ainda não gerados. Execute convert_icons_to_base64.py para popular.

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
