@echo off
REM Script para executar a aplicacao no Windows
REM Agora Media Production - Sistema de Contabilidade

echo ========================================
echo   Agora Media - Iniciando Aplicacao
echo ========================================
echo.

REM Verificar se ambiente virtual existe
if not exist venv (
    echo ERRO: Ambiente virtual nao encontrado!
    echo Por favor execute setup_windows.bat primeiro.
    echo.
    pause
    exit /b 1
)

REM Ativar ambiente virtual
call venv\Scripts\activate.bat

REM Verificar se .env existe
if not exist .env (
    echo AVISO: Ficheiro .env nao encontrado!
    echo A criar .env a partir de .env.example...
    copy .env.example .env
    echo.
    echo Por favor edite o ficheiro .env com suas configuracoes.
    echo.
    pause
)

REM Executar aplicacao
echo Iniciando aplicacao...
python main.py

REM Se houver erro, manter janela aberta
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERRO: A aplicacao terminou com erro!
    pause
)
