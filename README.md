💻 Purpose of Use & REQUIRED PROGRAMS AND LIBRARIES
The purpose of the application is to automatically pull champions to the bench from the shop by performing the number of searches you specify for the champions you enter.
I have tested the application many times and have not encountered any missed bench placements. Very rarely, if your champion becomes 3-starred, there might be a chance it is not matched due to animations, but this is a very low probability.

I made it for myself so it uses Turkish client's champion templates(shop images of champions). So if you want use it on English client make sure you get all champions template on english client. Should be as soon as close to my templates size.
Make sure to install the latest version of Python.
The script looks for a window with the title containing “League of Legends”.
Make sure the game is running in windowed mode.
The bot scans the shop area by taking a screenshot. Your screen resolution must be 1920x1080, and the window position must remain unchanged.
Run as administrator if you get problems.



1. Python Packages (installed via pip)
The required Python libraries are listed in the requirements.txt file and can be installed via the terminal using the following command:

pip install -r requirements.txt

Required Python Packages:
- PyQt5
- opencv-python
- pytesseract
- numpy
- pyautogui
- keyboard
- pygetwindow
- Pillow



2. Tesseract OCR (Required for reading text from images)
Purpose: Provides OCR support to analyze and compare champion images.

Download Links:
- GitHub: https://github.com/tesseract-ocr/tesseract
- Or directly for Windows: https://github.com/UB-Mannheim/tesseract/wiki

Install it to the default installation path.
In the code, it is defined as follows:

C:\Users\Administrator\AppData\Local\Programs\Tesseract-OCR\tesseract.exe

Make sure it is installed in this folder. If you installed it elsewhere, update this line in the code accordingly:

pytesseract.pytesseract.tesseract_cmd = r"YOUR\NEW\TESSERACT\PATH\tesseract.exe"



3. Champion Template Images
Folder: champions_templates

Description: This folder should contain champion images in .png format. For example:

champions_templates/
├── yasuo.png
├── aatrox.png
└── vex.png

These images are used to match the champions shown in the in-game shop.
The file names must match the names of the champions you input into the program.



🖱️ HOTKEYS
- Start Bot: Ctrl + 1
- Pause / Resume Bot: Ctrl + 2
- Stop Bot: Ctrl + 3
- Show / Hide UI: Insert



📁 SAMPLE FILE STRUCTURE

project_folder/
├── lazarus.py
├── requirements.txt
├── readme.md
└── champions_templates/
    ├── yasuo.png
    ├── vex.png
    └── aatrox.png
