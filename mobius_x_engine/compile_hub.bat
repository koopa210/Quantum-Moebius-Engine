@echo off
echo ===================================================
echo   MOBIUS-X GAME HUB COMPILER (PORTABLE EDITION)
echo ===================================================
echo.
echo [1] Checking dependencies...
pip install customtkinter numpy pillow pyinstaller scipy

echo.
echo [2] Building Portable Executable...
echo This will create a single 'mobius_hub.exe' in the 'dist' folder.
pyinstaller --noconfirm --onefile --windowed --name "Mobius-X_Launcher" --add-data "steam_discovery.py;." --add-data "bit_transposer.py;." --collect-all customtkinter --hidden-import tkinter --icon=NONE "mobius_hub.py"

echo.
echo [3] Cleanup...
echo Done! Transfer the file in 'dist/Möbius Game Hub.exe' to your USB drive.
pause
