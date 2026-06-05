@echo off
chcp 65001 >nul
title Primeiro push - salvar credencial do GitHub
cd /d "%~dp0"
echo.
echo ============================================================
echo   Primeiro push - autorizar e salvar a credencial GitHub
echo ============================================================
echo.
echo Vai abrir uma janela do navegador para voce autorizar.
echo Apos autorizar, a credencial fica salva no Windows e o
echo publicar.bat passa a funcionar sozinho.
echo.
pause

REM Limpa qualquer credencial antiga problematica
"C:\Program Files\Git\cmd\git.exe" config --global credential.helper manager

REM Tira o __pycache__ que entrou indevidamente no commit anterior
"C:\Program Files\Git\cmd\git.exe" rm -r --cached __pycache__ 2>nul

REM Re-adiciona com o .gitignore atualizado
"C:\Program Files\Git\cmd\git.exe" add .
"C:\Program Files\Git\cmd\git.exe" commit -m "Limpa __pycache__ e atualiza .gitignore" 2>nul

REM Push - vai abrir o browser para autorizar
"C:\Program Files\Git\cmd\git.exe" push -u origin main

echo.
echo ============================================================
echo  Se viu "Writing objects" + "main -> main" acima, deu certo.
echo  Daqui pra frente, use o publicar.bat normalmente.
echo ============================================================
pause
