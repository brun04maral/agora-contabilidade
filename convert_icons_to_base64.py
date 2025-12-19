#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Conversão de Ícones para Base64

Este script converte todos os ícones PNG da pasta media/icons/ para Base64
e atualiza automaticamente o ficheiro assets/resources.py com as constantes.

COMO USAR:
    1. Coloque os ficheiros PNG em media/icons/
    2. Execute: python convert_icons_to_base64.py
    3. As constantes serão geradas automaticamente em assets/resources.py

NOMENCLATURA:
    - Ficheiro: dashboard_icon.png → Constante: DASHBOARD_ICON
    - Ficheiro: my-icon.png → Constante: MY_ICON
    - Ficheiro: ProjectIcon.png → Constante: PROJECT_ICON

NOTA:
    - Apenas ficheiros PNG são processados
    - Nomes são convertidos para UPPER_SNAKE_CASE
    - O ficheiro assets/resources.py é modificado in-place
"""

import os
import base64
import re
from pathlib import Path


def png_to_base64(png_path: str) -> str:
    """
    Converte um ficheiro PNG para string Base64

    Args:
        png_path: Caminho para o ficheiro PNG

    Returns:
        String Base64 do ficheiro
    """
    with open(png_path, 'rb') as f:
        png_data = f.read()
        base64_string = base64.b64encode(png_data).decode('utf-8')
        return base64_string


def filename_to_constant_name(filename: str) -> str:
    """
    Converte nome de ficheiro para nome de constante Python

    Args:
        filename: Nome do ficheiro (ex: "dashboard_icon.png")

    Returns:
        Nome da constante (ex: "DASHBOARD_ICON")

    Exemplos:
        dashboard_icon.png → DASHBOARD_ICON
        my-icon.png → MY_ICON
        ProjectIcon.png → PROJECT_ICON
        icon.test.png → ICON_TEST
    """
    # Remover extensão
    name = Path(filename).stem

    # Substituir hífens e pontos por underscore
    name = name.replace('-', '_').replace('.', '_')

    # Converter CamelCase para snake_case
    name = re.sub('([a-z0-9])([A-Z])', r'\1_\2', name)

    # Converter para uppercase
    name = name.upper()

    return name


def generate_constants_code(icons_dir: str) -> str:
    """
    Gera o código Python com todas as constantes Base64

    Args:
        icons_dir: Caminho para a pasta media/icons/

    Returns:
        String com o código Python gerado
    """
    if not os.path.exists(icons_dir):
        return "# Pasta media/icons/ não encontrada. Nenhum ícone disponível.\n"

    png_files = [f for f in os.listdir(icons_dir) if f.lower().endswith('.png')]

    if not png_files:
        return "# Nenhum ficheiro PNG encontrado em media/icons/\n"

    # Ordenar alfabeticamente
    png_files.sort()

    code_lines = []
    code_lines.append("# Ícones disponíveis:")

    for png_file in png_files:
        constant_name = filename_to_constant_name(png_file)
        code_lines.append(f"# - {constant_name} ({png_file})")

    code_lines.append("")

    # Gerar constantes
    for png_file in png_files:
        png_path = os.path.join(icons_dir, png_file)
        constant_name = filename_to_constant_name(png_file)

        try:
            base64_string = png_to_base64(png_path)

            code_lines.append(f"# Ícone: {png_file}")
            code_lines.append(f"{constant_name} = (")

            # Quebrar a string Base64 em linhas de 80 caracteres para melhor legibilidade
            chunk_size = 80
            for i in range(0, len(base64_string), chunk_size):
                chunk = base64_string[i:i+chunk_size]
                code_lines.append(f'    "{chunk}"')

            code_lines.append(")")
            code_lines.append("")

        except Exception as e:
            code_lines.append(f"# ERRO ao processar {png_file}: {e}")
            code_lines.append("")

    return "\n".join(code_lines)


def update_resources_file(resources_path: str, new_constants_code: str) -> bool:
    """
    Atualiza o ficheiro assets/resources.py com as novas constantes

    Args:
        resources_path: Caminho para assets/resources.py
        new_constants_code: Código gerado com as constantes

    Returns:
        True se bem-sucedido, False caso contrário
    """
    if not os.path.exists(resources_path):
        print(f"❌ Erro: Ficheiro {resources_path} não encontrado")
        return False

    try:
        # Ler ficheiro existente
        with open(resources_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Encontrar marcadores
        start_marker = "# --- INÍCIO DA SECÇÃO AUTO-GERADA ---"
        end_marker = "# --- FIM DA SECÇÃO AUTO-GERADA ---"

        start_idx = content.find(start_marker)
        end_idx = content.find(end_marker)

        if start_idx == -1 or end_idx == -1:
            print("❌ Erro: Marcadores não encontrados em resources.py")
            print("   Certifique-se que o ficheiro contém:")
            print(f"   {start_marker}")
            print(f"   {end_marker}")
            return False

        # Construir novo conteúdo
        before = content[:start_idx + len(start_marker)]
        after = content[end_idx:]

        new_content = (
            before + "\n"
            "# NÃO EDITAR MANUALMENTE - Este conteúdo é gerado por convert_icons_to_base64.py\n\n"
            + new_constants_code + "\n"
            + after
        )

        # Escrever ficheiro atualizado
        with open(resources_path, 'w', encoding='utf-8') as f:
            f.write(new_content)

        return True

    except Exception as e:
        print(f"❌ Erro ao atualizar {resources_path}: {e}")
        return False


def main():
    """
    Função principal do script
    """
    print("=" * 70)
    print("CONVERSÃO DE ÍCONES PNG PARA BASE64")
    print("=" * 70)
    print()

    # Determinar caminhos
    script_dir = os.path.dirname(os.path.abspath(__file__))
    icons_dir = os.path.join(script_dir, "media", "icons")
    resources_path = os.path.join(script_dir, "assets", "resources.py")

    print(f"📁 Pasta de ícones: {icons_dir}")
    print(f"📄 Ficheiro de destino: {resources_path}")
    print()

    # Verificar se pasta existe
    if not os.path.exists(icons_dir):
        print(f"⚠️  Pasta {icons_dir} não existe.")
        print(f"   A criar pasta...")
        os.makedirs(icons_dir, exist_ok=True)
        print(f"   ✅ Pasta criada!")
        print()
        print("ℹ️  Coloque os ficheiros PNG em media/icons/ e execute novamente.")
        return

    # Listar ficheiros PNG
    png_files = [f for f in os.listdir(icons_dir) if f.lower().endswith('.png')]

    if not png_files:
        print("⚠️  Nenhum ficheiro PNG encontrado em media/icons/")
        print()
        print("ℹ️  Coloque os ficheiros PNG em media/icons/ e execute novamente.")
        return

    print(f"🔍 Encontrados {len(png_files)} ficheiros PNG:")
    for png_file in sorted(png_files):
        constant_name = filename_to_constant_name(png_file)
        print(f"   - {png_file} → {constant_name}")
    print()

    # Gerar código
    print("⚙️  Gerando constantes Base64...")
    constants_code = generate_constants_code(icons_dir)
    print("   ✅ Código gerado!")
    print()

    # Atualizar ficheiro
    print("💾 Atualizando assets/resources.py...")
    success = update_resources_file(resources_path, constants_code)

    if success:
        print("   ✅ Ficheiro atualizado com sucesso!")
        print()
        print("=" * 70)
        print("✅ CONVERSÃO CONCLUÍDA")
        print("=" * 70)
        print()
        print("📋 Próximos passos:")
        print("   1. Importe as constantes: from assets.resources import ICON_NAME")
        print("   2. Use get_icon(ICON_NAME, size=(32, 32)) para carregar")
        print()
    else:
        print("   ❌ Falha ao atualizar ficheiro")
        print()


if __name__ == "__main__":
    main()
