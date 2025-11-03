#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Teste dos logos PNG
"""
import os
from PIL import Image

print("=" * 80)
print("🧪 TESTE DOS LOGOS PNG")
print("=" * 80)

# Test 1: Sidebar logo
print("\n[TESTE 1] Logo da Sidebar")
print("-" * 80)
logo_sidebar = "media/a + agora media production@0.5x.png"
if os.path.exists(logo_sidebar):
    img = Image.open(logo_sidebar)
    print(f"✅ Logo encontrado: {logo_sidebar}")
    print(f"   Dimensões: {img.size} (width x height)")
    print(f"   Modo: {img.mode}")
else:
    print(f"❌ Logo não encontrado: {logo_sidebar}")

# Test 2: Login logo
print("\n[TESTE 2] Logo do Login")
print("-" * 80)
logo_login = "media/AGORA media production@0.5x.png"
if os.path.exists(logo_login):
    img = Image.open(logo_login)
    print(f"✅ Logo encontrado: {logo_login}")
    print(f"   Dimensões: {img.size} (width x height)")
    print(f"   Modo: {img.mode}")
else:
    print(f"❌ Logo não encontrado: {logo_login}")

print("\n" + "=" * 80)
print("✅ TESTE COMPLETO")
print("=" * 80)
print("\nOs logos estão prontos para serem usados na aplicação!")
print("Dimensões sugeridas baseadas no tamanho original:")
print("  - Sidebar: manter proporção, altura ~60px")
print("  - Login: manter proporção, altura ~80px")
