#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import os

# Adicionar diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Executar o setup_completo
exec(open('scripts/setup_completo.py').read())
