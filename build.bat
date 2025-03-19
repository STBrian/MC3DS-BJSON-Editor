@ECHO OFF
if exist build\ (
    del /S /Q build\\*
    rmdir /S /Q build
)
if exist dist\ (
    del /S /Q dist\\*
    rmdir /S /Q dist
)
py -3.13 -m PyInstaller --name=BJSON-Editor --onefile  --windowed --icon icon.ico --add-data icon.ico:. --add-data assets:assets --add-data icon.png:. main.py
del "BJSON-Editor.spec"