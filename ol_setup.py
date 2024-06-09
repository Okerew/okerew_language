import os 
os.system("pip install pyinstaller")
os.system("pyinstaller --onefile interpreter.py")
os.system("sudo chmod +x ./dist/interpreter")
os.system("sudo cp ./dist/interpreter /usr/local/bin/")
