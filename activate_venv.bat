@echo off
cd /d "%~dp0"
call .venv\Scripts\activate.bat
echo Virtual environment activated!
echo You can now run: python autoFormer.py
cmd /k
