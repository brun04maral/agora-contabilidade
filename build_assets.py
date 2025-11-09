#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Build de Assets - Gerar PNGs a partir do logo original

Este script deve ser executado ANTES de compilar a aplicação com PyInstaller.
Gera versões PNG de alta qualidade do logo original para uso em produção Windows.

USO:
    python build_assets.py

QUANDO EXECUTAR:
    - Antes de criar build com PyInstaller
    - Depois de atualizar logo
    - Quando preparar para distribuição

O QUE FAZ:
    - Carrega logo_original.png (extraído do SVG, 3746x3748px)
    - Redimensiona para os tamanhos necessários com LANCZOS (máxima qualidade)
    - Aplica transparência removendo fundo branco
    - Salva em media/logos/ com nomes padronizados
    - Esses PNGs são usados automaticamente quando Cairo não está disponível
"""

import os
import sys
from pathlib import Path
from PIL import Image
import numpy as np


# Configuração dos assets a gerar
LOGO_SIZES = {
    "logo": [
        (100, 60, "sidebar"),    # Sidebar (1x)
        (200, 120, "sidebar@2x"), # Sidebar (2x retina)
        (313, 80, "login"),       # Login (1x)
        (626, 160, "login@2x"),   # Login (2x retina)
    ]
}


def load_original_logo():
    """
    Carrega o logo original de alta resolução

    Returns:
        PIL.Image ou None se não encontrar
    """
    logos_dir = Path("media") / "logos"
    original_path = logos_dir / "logo_original.png"

    if not original_path.exists():
        print("=" * 70)
        print("❌ ERRO: logo_original.png não encontrado")
        print("=" * 70)
        print()
        print("Execute primeiro: python3 extract_logo_png.py")
        print()
        print("Isso vai extrair o PNG original de alta resolução do logo.svg")
        print()
        print("=" * 70)
        return None

    try:
        img = Image.open(str(original_path))
        print(f"✅ Logo original carregado: {img.size[0]}x{img.size[1]}px")
        return img
    except Exception as e:
        print(f"❌ Erro ao carregar logo original: {e}")
        return None


def build_logo_pngs():
    """Gera PNGs dos logos em diferentes tamanhos"""

    print("=" * 70)
    print("🎨 BUILD DE ASSETS - Geração de PNGs de Alta Qualidade")
    print("=" * 70)
    print()

    # Carregar logo original de alta resolução
    original_logo = load_original_logo()
    if not original_logo:
        sys.exit(1)

    print()

    # Diretório de logos
    logos_dir = Path("media") / "logos"

    if not logos_dir.exists():
        print(f"❌ Erro: Diretório {logos_dir} não existe")
        sys.exit(1)

    total_generated = 0
    total_failed = 0

    # Processar cada logo
    for logo_name, sizes in LOGO_SIZES.items():
        print(f"📄 Gerando versões do logo:")
        print()

        # Gerar cada tamanho
        for width, height, suffix in sizes:
            output_name = f"{logo_name}_{suffix}.png"
            output_path = logos_dir / output_name

            try:
                # Fazer cópia do original para não modificar
                logo_img = original_logo.copy()

                # Garantir RGBA
                if logo_img.mode != 'RGBA':
                    logo_img = logo_img.convert('RGBA')

                # Redimensionar com LANCZOS (máxima qualidade)
                # LANCZOS é o melhor algoritmo para redução de tamanho
                logo_img = logo_img.resize((width, height), Image.Resampling.LANCZOS)

                # Processar transparência
                data = np.array(logo_img)

                # Remover fundo branco: pixels RGB > 245 tornam-se transparentes
                # Threshold mais conservador para preservar detalhes
                white_mask = (
                    (data[:, :, 0] > 245) &
                    (data[:, :, 1] > 245) &
                    (data[:, :, 2] > 245)
                )
                data[white_mask, 3] = 0

                logo_img = Image.fromarray(data)

                # Salvar com máxima qualidade
                logo_img.save(str(output_path), "PNG", optimize=False)

                # Verificar tamanho do arquivo
                file_size = output_path.stat().st_size / 1024  # KB

                print(f"   ✅ {output_name:30s} ({width}x{height}) - {file_size:.1f} KB")
                total_generated += 1

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
