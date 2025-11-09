#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Build de Assets - Gerar PNGs a partir de SVGs

Este script deve ser executado ANTES de compilar a aplicação com PyInstaller.
Gera versões PNG de alta qualidade dos logos SVG para uso em produção Windows.

USO:
    python build_assets.py

QUANDO EXECUTAR:
    - Antes de criar build com PyInstaller
    - Depois de atualizar logos SVG
    - Quando preparar para distribuição

O QUE FAZ:
    - Lê todos os SVGs de media/logos/
    - Converte para PNG nos tamanhos usados pela aplicação
    - Salva em media/logos/ com nome padrão
    - Esses PNGs são usados automaticamente quando Cairo não está disponível
"""

import os
import sys
from pathlib import Path
from PIL import Image
import numpy as np

# Adicionar diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from assets.resources import get_logo, CAIROSVG_AVAILABLE


# Configuração dos assets a gerar
LOGO_SIZES = {
    "logo": [
        (100, 60, "sidebar"),    # Sidebar (1x)
        (200, 120, "sidebar@2x"), # Sidebar (2x retina)
        (313, 80, "login"),       # Login (1x)
        (626, 160, "login@2x"),   # Login (2x retina)
    ]
}


def ensure_cairo_available():
    """Verifica se Cairo está disponível"""
    if not CAIROSVG_AVAILABLE:
        print("=" * 70)
        print("❌ ERRO: Cairo não disponível")
        print("=" * 70)
        print()
        print("Para gerar assets PNG a partir de SVG, é necessário ter Cairo instalado.")
        print()
        print("OPÇÕES:")
        print()
        print("1. Instalar Cairo no Linux/Mac:")
        print("   pip install cairosvg")
        print()
        print("2. Usar os PNGs já existentes (se houver)")
        print()
        print("3. Executar este script num sistema com Cairo instalado")
        print()
        print("=" * 70)
        return False
    return True


def build_logo_pngs():
    """Gera PNGs dos logos em diferentes tamanhos"""

    print("=" * 70)
    print("🎨 BUILD DE ASSETS - Geração de PNGs")
    print("=" * 70)
    print()

    if not ensure_cairo_available():
        sys.exit(1)

    # Diretório de logos
    logos_dir = Path("media") / "logos"

    if not logos_dir.exists():
        print(f"❌ Erro: Diretório {logos_dir} não existe")
        sys.exit(1)

    total_generated = 0
    total_failed = 0

    # Processar cada logo
    for logo_name, sizes in LOGO_SIZES.items():
        svg_filename = f"{logo_name}.svg"
        svg_path = logos_dir / svg_filename

        if not svg_path.exists():
            print(f"⚠️  Aviso: {svg_filename} não encontrado, pulando...")
            continue

        print(f"📄 Processando: {svg_filename}")
        print()

        # Gerar cada tamanho
        for width, height, suffix in sizes:
            output_name = f"{logo_name}_{suffix}.png"
            output_path = logos_dir / output_name

            try:
                # NOTA: logo.svg contém PNG embutido, não é vetorial
                # Estratégia: carregar em 2x resolução, depois reduzir com LANCZOS = melhor qualidade
                logo_img = get_logo(svg_filename, size=(width * 2, height * 2))

                if logo_img:
                    # Converter para RGBA se necessário
                    if logo_img.mode != 'RGBA':
                        logo_img = logo_img.convert('RGBA')

                    # Reduzir para tamanho final com LANCZOS (alta qualidade)
                    logo_img = logo_img.resize((width, height), Image.Resampling.LANCZOS)

                    # Remover fundo branco com threshold agressivo
                    data = np.array(logo_img)

                    # Pixels muito claros (quase brancos) tornam-se transparentes
                    # Threshold: RGB > 250 (quase branco)
                    near_white = (
                        (data[:, :, 0] > 250) &
                        (data[:, :, 1] > 250) &
                        (data[:, :, 2] > 250)
                    )

                    # Tornar pixels quase brancos completamente transparentes
                    data[near_white, 3] = 0

                    # Suavizar bordas para remover artefactos
                    low_alpha = data[:, :, 3] < 128
                    data[low_alpha, 3] = data[low_alpha, 3] // 2

                    logo_img = Image.fromarray(data)

                    # Salvar PNG com alta qualidade
                    logo_img.save(str(output_path), "PNG", optimize=True, compress_level=6)

                    # Verificar tamanho do arquivo
                    file_size = output_path.stat().st_size / 1024  # KB

                    print(f"   ✅ {output_name:30s} ({width}x{height}) - {file_size:.1f} KB")
                    total_generated += 1
                else:
                    print(f"   ❌ {output_name:30s} - Falha ao converter")
                    total_failed += 1

            except Exception as e:
                print(f"   ❌ {output_name:30s} - Erro: {e}")
                total_failed += 1

        print()

    # Resumo
    print("=" * 70)
    print("📊 RESUMO")
    print("=" * 70)
    print(f"✅ Gerados com sucesso: {total_generated}")
    if total_failed > 0:
        print(f"❌ Falhas: {total_failed}")
    print()

    if total_generated > 0:
        print("🎉 Assets gerados com sucesso!")
        print()
        print("PRÓXIMOS PASSOS:")
        print("  1. Verificar os PNGs gerados em media/logos/")
        print("  2. Fazer commit dos novos PNGs")
        print("  3. Compilar aplicação com PyInstaller")
        print()
    else:
        print("⚠️  Nenhum asset foi gerado")
        sys.exit(1)


def list_generated_assets():
    """Lista todos os PNGs gerados"""
    logos_dir = Path("media") / "logos"

    print("📁 Assets PNG disponíveis:")
    print()

    png_files = sorted(logos_dir.glob("*.png"))

    if not png_files:
        print("   (nenhum PNG encontrado)")
    else:
        for png_file in png_files:
            size = png_file.stat().st_size / 1024  # KB
            print(f"   - {png_file.name:40s} {size:>8.1f} KB")

    print()


def main():
    """Função principal"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Gera PNGs dos logos SVG para distribuição"
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="Listar assets PNG já gerados"
    )

    args = parser.parse_args()

    if args.list:
        list_generated_assets()
    else:
        build_logo_pngs()


if __name__ == "__main__":
    main()
