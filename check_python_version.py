#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar compatibilidade da versão do Python
"""
import sys
import platform

def check_python_version():
    """Verifica se a versão do Python é compatível"""

    version = sys.version_info
    version_str = f"{version.major}.{version.minor}.{version.micro}"

    print("=" * 70)
    print("🐍 VERIFICAÇÃO DE COMPATIBILIDADE DO PYTHON")
    print("=" * 70)
    print(f"\nVersão do Python: {version_str}")
    print(f"Sistema Operacional: {platform.system()} {platform.release()}")
    print(f"Arquitetura: {platform.machine()}")
    print()

    # Verificar versão
    if version.major < 3:
        print("❌ ERRO CRÍTICO: Python 2 não é suportado!")
        print("   Por favor instale Python 3.10, 3.11 ou 3.12")
        return False

    if version.minor < 10:
        print("❌ ERRO: Python 3.9 ou anterior não é suportado!")
        print("   Versão mínima: Python 3.10")
        print("   Versão recomendada: Python 3.11 ou 3.12")
        return False

    if version.minor == 10:
        print("⚠️  AVISO: Python 3.10 está próximo do fim de vida")
        print("   Considere atualizar para Python 3.11 ou 3.12")
        print("   Status: COMPATÍVEL (com ressalvas)")
        return True

    if version.minor == 11:
        print("✅ EXCELENTE: Python 3.11 - Versão recomendada!")
        print("   Todas as bibliotecas testadas e funcionais")
        return True

    if version.minor == 12:
        print("✅ BOM: Python 3.12 - Versão compatível")
        print("   Todas as bibliotecas devem funcionar")
        return True

    if version.minor == 13:
        print("⚠️  AVISO: Python 3.13 - Versão muito recente!")
        print("   Algumas bibliotecas podem ter problemas de compatibilidade")
        print("   Especialmente: psycopg2-binary, bcrypt, Pillow")
        print("   ")
        print("   RECOMENDAÇÃO: Use Python 3.11 ou 3.12 para melhor estabilidade")
        return True

    if version.minor >= 14:
        print("✅ Python 3.14+ detectado!")
        print("   Versão muito recente - a maioria das bibliotecas deve funcionar.")
        print("   ")
        print("   ⚠️  NOTA: Se encontrar problemas de compatibilidade:")
        print("   - Tente instalar com: pip install --upgrade --force-reinstall")
        print("   - Algumas bibliotecas C podem precisar de recompilação")
        print("   ")
        return True

    return True


def check_modules():
    """Tenta importar módulos críticos"""
    print()
    print("-" * 70)
    print("🔍 VERIFICANDO MÓDULOS CRÍTICOS")
    print("-" * 70)

    modules = [
        ("tkinter", "Interface gráfica (built-in)"),
        ("customtkinter", "Framework UI customizado"),
        ("sqlalchemy", "ORM para base de dados"),
        ("pandas", "Manipulação de dados Excel"),
        ("PIL", "Processamento de imagens"),
    ]

    all_ok = True

    for module_name, description in modules:
        try:
            __import__(module_name)
            print(f"  ✅ {module_name:20s} - {description}")
        except ImportError as e:
            print(f"  ❌ {module_name:20s} - FALHOU: {str(e)}")
            all_ok = False
        except Exception as e:
            print(f"  ⚠️  {module_name:20s} - ERRO: {str(e)}")
            all_ok = False

    return all_ok


if __name__ == "__main__":
    print()
    version_ok = check_python_version()

    if version_ok:
        modules_ok = check_modules()

        print()
        print("=" * 70)
        if modules_ok:
            print("✅ SISTEMA COMPATÍVEL")
            print("=" * 70)
            print("\nPode executar a aplicação com: python main.py")
        else:
            print("⚠️  MÓDULOS EM FALTA")
            print("=" * 70)
            print("\nExecute: pip install -r requirements.txt")
    else:
        print()
        print("=" * 70)
        print("❌ SISTEMA INCOMPATÍVEL")
        print("=" * 70)
        print("\nPor favor instale uma versão compatível do Python.")
        sys.exit(1)

    print()
