@echo off
echo ========================================================
echo         Building BetterNote.exe with PyInstaller
echo ========================================================
echo.

if exist .venv\Scripts\pyinstaller.exe (
    set PYI=.venv\Scripts\pyinstaller.exe
) else (
    set PYI=pyinstaller
)

if exist BetterNote.spec (
    %PYI% BetterNote.spec --noconfirm
) else (
    %PYI% --noconfirm --onefile --windowed --name "BetterNote" --icon "resources/icons/app_icon.ico" --add-data "resources;resources" main.py
)

if %ERRORLEVEL% equ 0 (
    echo.
    echo ========================================================
    echo  SUCCESS! BetterNote.exe created in the "dist" folder!
    echo ========================================================
    echo Output: dist\BetterNote.exe
) else (
    echo.
    echo ========================================================
    echo  BUILD FAILED. Check errors above.
    echo ========================================================
)

pause

