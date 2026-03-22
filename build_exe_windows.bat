@echo off
setlocal

where python >nul 2>nul
if errorlevel 1 (
  echo [ERRO] Python nao encontrado no PATH.
  exit /b 1
)

python -m pip install --upgrade pip
if errorlevel 1 exit /b 1

if exist requirements.txt (
  python -m pip install -r requirements.txt
  if errorlevel 1 exit /b 1
)

python -m pip install -r requirements-build.txt
if errorlevel 1 exit /b 1

if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist HVACCargaTermica.spec del /q HVACCargaTermica.spec

python -m PyInstaller ^
  --noconfirm ^
  --clean ^
  --windowed ^
  --onefile ^
  --name HVACCargaTermica ^
  --add-data "data;data" ^
  main.py

if errorlevel 1 (
  echo [ERRO] Falha ao gerar executavel.
  exit /b 1
)

echo.
echo [OK] Executavel gerado em: dist\HVACCargaTermica.exe
endlocal
