#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extrair PNG embutido do logo.svg

O logo.svg contém um PNG base64 de alta resolução (3746x3748px).
Este script extrai esse PNG original para uso direto.
"""

import re
import base64
from pathlib import Path
from PIL import Image
from io import BytesIO

# Ler SVG
svg_path = Path("media/logos/logo.svg")
svg_content = svg_path.read_text()

# Encontrar base64 do PNG embutido
match = re.search(r'data:image/png;base64,([A-Za-z0-9+/=]+)', svg_content)

if match:
    base64_data = match.group(1)

    # Decodificar base64
    png_data = base64.b64decode(base64_data)

    # Abrir como PIL Image
    img = Image.open(BytesIO(png_data))

    print(f"✅ PNG extraído com sucesso!")
    print(f"   Dimensões: {img.size}")
    print(f"   Modo: {img.mode}")

    # Salvar PNG original
    output_path = Path("media/logos/logo_original.png")
    img.save(str(output_path), "PNG")

    print(f"   Salvo em: {output_path}")
    print(f"   Tamanho: {output_path.stat().st_size / 1024:.1f} KB")
else:
    print("❌ Erro: PNG base64 não encontrado no SVG")
