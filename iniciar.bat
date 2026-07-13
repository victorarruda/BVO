@echo off
title BVO - Baixador de Videos Online (OldSchool) V2.0

cls
echo =======================================
echo Iniciando BVO...
echo =======================================
python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo [ERRO] Python nao encontrado!
    echo Baixe e instale o Python em: https://www.python.org/downloads/
    echo Certifique-se de marcar a opcao "Add Python to PATH" durante a instalacao.
    pause
    exit /b
)

python baixar_vod.py
pause
