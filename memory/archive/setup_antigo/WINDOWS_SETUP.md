# 🪟 Guia de Setup para Windows

## ⚠️ Versões Recomendadas

**Python:** 3.10, 3.11 ou 3.12 (recomendado: **3.12**)
- ❌ Python 3.13+ não é suportado (problemas de compatibilidade)
- ❌ Python 3.9 ou anterior não é suportado

## 🚀 Setup Rápido

### Opção 1: Automático (Recomendado)

1. **Execute o script de setup:**
   ```bash
   setup_windows.bat
   ```

2. **Execute a aplicação:**
   ```bash
   run_windows.bat
   ```

### Opção 2: Manual

1. **Criar ambiente virtual:**
   ```bash
   python -m venv venv
   ```

2. **Ativar ambiente virtual:**
   ```bash
   venv\Scripts\activate.bat
   ```

3. **Instalar dependências:**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Configurar variáveis de ambiente:**
   ```bash
   copy .env.example .env
   ```
   Edite o ficheiro `.env` com suas configurações.

5. **Executar aplicação:**
   ```bash
   python main.py
   ```

---

## 🔧 Troubleshooting

### Problema: "Python não encontrado"

**Solução:**
1. Instale Python de [python.org](https://www.python.org/downloads/)
2. Durante instalação, marque "Add Python to PATH"
3. Reinicie o terminal/PowerShell

### Problema: Erro ao instalar `psycopg2-binary`

**Causa:** Problemas com compilação em Windows

**Solução 1 - Usar versão binária:**
```bash
pip install psycopg2-binary --no-cache-dir
```

**Solução 2 - Instalar Microsoft C++ Build Tools:**
1. Baixe de: https://visualstudio.microsoft.com/visual-cpp-build-tools/
2. Instale "Desktop development with C++"
3. Tente novamente: `pip install -r requirements.txt`

### Problema: Erro ao instalar `bcrypt`

**Causa:** Falta de compilador C

**Solução:**
```bash
pip install --upgrade pip setuptools wheel
pip install bcrypt --no-cache-dir
```

### Problema: Erro "DLL load failed" ao importar `Pillow`

**Causa:** Falta de runtime do Visual C++

**Solução:**
1. Instale Microsoft Visual C++ Redistributable:
   - [Download x64](https://aka.ms/vs/17/release/vc_redist.x64.exe)
2. Reinicie o computador
3. Tente novamente

### Problema: `customtkinter` não funciona

**Causa:** Versão incompatível do Tcl/Tk

**Solução:**
```bash
pip uninstall customtkinter
pip install customtkinter==5.2.2 --no-cache-dir
```

### Problema: Erro "No module named 'tkinter'"

**Causa:** Python instalado sem Tcl/Tk

**Solução:**
1. Reinstale Python com opção "tcl/tk and IDLE"
2. Ou instale manualmente:
   ```bash
   # PowerShell como administrador
   choco install python --params "/InstallDir:C:\Python311"
   ```

### Problema: Performance lenta no Windows

**Solução:**
1. Adicione exceção do Windows Defender:
   - Abra Windows Security
   - Virus & threat protection → Settings → Add exclusion
   - Adicione a pasta do projeto

2. Desative modo de depuração do Python:
   - Não execute com `python -d main.py`
   - Use apenas `python main.py`

---

## 📦 Versões Testadas

| Componente | Versão Testada | Status |
|------------|----------------|--------|
| Python 3.10 | ✅ | Funcional |
| Python 3.11 | ✅ | Funcional |
| Python 3.12 | ✅ | Recomendado |
| Windows 10 | ✅ | Testado |
| Windows 11 | ✅ | Testado |

---

## 🐛 Erros Comuns e Soluções

### Erro: `ImportError: cannot import name 'Literal'`

**Causa:** Python muito antigo

**Solução:**
Atualize para Python 3.10+

### Erro: `ModuleNotFoundError: No module named 'database'`

**Causa:** Executando de diretório errado

**Solução:**
```bash
cd caminho\para\agora-contabilidade
python main.py
```

### Erro: Database connection failed

**Causa:** Ficheiro `.env` mal configurado

**Solução:**
1. Verifique se `.env` existe
2. Configure `DATABASE_URL` corretamente:
   ```
   DATABASE_URL=sqlite:///./agora_media.db
   ```

---

## 💡 Dicas para Windows

### Usar PowerShell em vez de CMD

PowerShell tem melhor suporte para Python:
```powershell
# Ativar ambiente virtual
.\venv\Scripts\Activate.ps1

# Se der erro de política de execução:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Criar atalho para executar

1. Crie ficheiro `Agora Media.bat`:
   ```bat
   @echo off
   cd /d "%~dp0"
   call venv\Scripts\activate.bat
   python main.py
   pause
   ```

2. Crie atalho para este ficheiro no Desktop

### Executar em background

Para não ver janela do terminal:
1. Renomeie `main.py` para `main.pyw`
2. Execute: `pythonw main.pyw`

---

## 🆘 Suporte

Se os problemas persistirem:

1. Verifique a versão do Python:
   ```bash
   python --version
   ```

2. Verifique as dependências instaladas:
   ```bash
   pip list
   ```

3. Reinstale tudo do zero:
   ```bash
   rmdir /s venv
   setup_windows.bat
   ```

4. Reporte o erro no GitHub Issues com:
   - Versão do Python
   - Versão do Windows
   - Mensagem de erro completa
   - Output de `pip list`
