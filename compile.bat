del ./dist/Kovaaks_Tool.exe
pyinstaller --noconfirm --onefile --windowed --name Kovaaks_Tool --clean ./src/Kovaaks_Tool.py
robocopy ./src/assets/ ./dist/assets/ /E
pause