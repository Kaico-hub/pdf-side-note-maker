@echo off
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

python -m pip install -r "%SCRIPT_DIR%requirements.txt"
if errorlevel 1 goto error

python -m pip install pyinstaller
if errorlevel 1 goto error

python -m PyInstaller --clean --noconfirm "%SCRIPT_DIR%pdf_note_margin_maker.spec"
if errorlevel 1 goto error

if not exist "%SCRIPT_DIR%release" mkdir "%SCRIPT_DIR%release"
copy /Y "%SCRIPT_DIR%dist\PDF Note Margin Maker.exe" "%SCRIPT_DIR%release\PDF Note Margin Maker.exe" >nul
if errorlevel 1 goto error

echo.
echo Build finished.
echo EXE: release\PDF Note Margin Maker.exe
pause
exit /b 0

:error
echo.
echo Build failed.
pause
exit /b 1
