@echo off
echo Creating virtual environment...
python -m venv .venv
call .venv\Scripts\activate.bat

echo Installing dependencies...
pip install -r requirements.txt
pip install pyinstaller

echo Building Windows executable...
:: PyInstaller needs the --add-data format as "source;dest" on Windows
pyinstaller --name="BetterNote" ^
            --windowed ^
            --onefile ^
            --add-data="resources;resources" ^
            --clean ^
            main.py

echo.
echo Build complete! Your Windows executable is located at dist\BetterNote.exe
pause

