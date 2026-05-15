@echo off
title Atualizador do Site

echo.
echo Enviando atualizacao para o GitHub...
echo.

git add .

git commit -m "Atualizacao do site"

git push

echo.
echo Site atualizado com sucesso!
echo.

pause