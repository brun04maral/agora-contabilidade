@echo off
REM Setup script para Windows
REM Agora Media Production - Sistema de Contabilidade

echo ========================================
echo   Agora Media - Setup Windows
echo ========================================
echo.

REM Verificar versão do Python
echo [1/5] Verificando versão do Python...

REM Tentar diferentes comandos Python
python --version >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    set PYTHON_CMD=python
    goto :python_found
)

py --version >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    set PYTHON_CMD=py
    goto :python_found
)

python3 --version >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    set PYTHON_CMD=python3
    goto :python_found
)

echo ERRO: Python nao encontrado!
echo.
echo Por favor instale Python de python.org OU:
echo - Reabra PowerShell como Administrador
echo - Execute: setx PATH "%PATH%;C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python314"
echo.
pause
exit /b 1

:python_found
%PYTHON_CMD% --version
echo Python encontrado: %PYTHON_CMD%
echo.

REM Criar ambiente virtual
echo [2/5] Criando ambiente virtual...
if exist venv (
    echo Ambiente virtual ja existe. A usar o existente.
) else (
    %PYTHON_CMD% -m venv venv
    if %ERRORLEVEL% NEQ 0 (
        echo ERRO: Falha ao criar ambiente virtual!
        pause
        exit /b 1
    )
    echo Ambiente virtual criado com sucesso.
)
echo.

REM Ativar ambiente virtual
echo [3/5] Ativando ambiente virtual...
call venv\Scripts\activate.bat
if %ERRORLEVEL% NEQ 0 (
    echo ERRO: Falha ao ativar ambiente virtual!
    pause
    exit /b 1
)
echo.

REM Atualizar pip
echo [4/5] Atualizando pip...
%PYTHON_CMD% -m pip install --upgrade pip
echo.

REM Instalar dependências
echo [5/5] Instalando dependencias...
pip install -r requirements.txt
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERRO: Falha ao instalar dependencias!
    echo.
    echo Tentando instalacao com --no-cache-dir...
    pip install --no-cache-dir -r requirements.txt
    if %ERRORLEVEL% NEQ 0 (
        echo.
        echo ERRO PERSISTENTE: Verifique sua conexao e tente novamente.
        pause
        exit /b 1
    )
)
echo.

echo ========================================
echo   Setup concluido com sucesso!
echo ========================================
echo.
echo Para iniciar a aplicacao:
echo   1. Ative o ambiente virtual: venv\Scripts\activate.bat
echo   2. Execute: python main.py
echo.
echo Ou simplesmente execute: run_windows.bat
echo.
pause
