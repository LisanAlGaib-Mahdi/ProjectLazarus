# 💻 Purpose of Use & Required Programs and Libraries

The purpose of this application is to **automatically pull champions to the bench from the shop** by performing a specified number of searches for the champions you input.

- The application has been tested extensively and rarely misses bench placements.
- In very rare cases, if your champion is **upgraded to 3-star**, there may be a minor chance of mismatch due to animations—though this is highly unlikely.

> ⚠️ This project was created for personal use with the **Turkish client**, so champion template images are based on the Turkish version of the game.  
> If you're using the **English client**, you must provide the appropriate champion template images in English. Ensure these images closely match the size and resolution of the original Turkish ones.

### ⚙️ System Requirements

- Install the **latest version of Python**.
- The game must be running in **windowed mode**.
- Your screen resolution must be **1920x1080**.
- The **window position must remain unchanged** during operation.
- Run the script as **Administrator** if you encounter any issues.
- The script looks for a window with a title containing **"League of Legends"**.

---

## 📦 1. Python Packages

Install all required packages listed in `requirements.txt` using:

```bash
pip install -r requirements.txt
```

### Required Libraries:

- `PyQt5`
- `opencv-python`
- `pytesseract`
- `numpy`
- `pyautogui`
- `keyboard`
- `pygetwindow`
- `Pillow`

---

## 🧠 2. Tesseract OCR

Used for **text recognition** in champion images.

### 🔗 Download Links:
- GitHub: [https://github.com/tesseract-ocr/tesseract](https://github.com/tesseract-ocr/tesseract)
- Windows Installer: [https://github.com/UB-Mannheim/tesseract/wiki](https://github.com/UB-Mannheim/tesseract/wiki)

### 📍 Installation Path

Install it in the default path:
```bash
C:\Users\Administrator\AppData\Local\Programs\Tesseract-OCR\tesseract.exe
```

If installed elsewhere, update this line in the code:
```python
pytesseract.pytesseract.tesseract_cmd = r"YOUR\NEW\TESSERACT\PATH\tesseract.exe"
```

---

## 🖼️ 3. Champion Template Images

Folder: `champions_templates/`  
These `.png` files are used to **match champions in the in-game shop**.

> File names **must match** the champion names you input into the program.

### Example:
```
champions_templates/
├── yasuo.png
├── aatrox.png
└── vex.png
```

---

## 🖱️ Hotkeys

- **Start Bot**: `Ctrl + 1`  
- **Pause / Resume Bot**: `Ctrl + 2`  
- **Stop Bot**: `Ctrl + 3`  
- **Show / Hide UI**: `Insert`

---

## 📁 Sample Project Structure

```
project_folder/
├── lazarus.py
├── requirements.txt
├── readme.md
└── champions_templates/
    ├── yasuo.png
    ├── vex.png
    └── aatrox.png
```
