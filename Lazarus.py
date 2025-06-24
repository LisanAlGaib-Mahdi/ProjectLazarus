import sys
import os
import time
import threading
import cv2
import pytesseract
import numpy as np
import pyautogui
import keyboard
import pygetwindow as gw
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QLineEdit, QSlider
from PyQt5.QtCore import Qt, QPoint, pyqtSignal, QObject, QTimer, QMetaObject, QThread
from PyQt5.QtGui import QFont, QColor, QPainter, QBrush, QPen
from PIL import ImageGrab

pytesseract.pytesseract.tesseract_cmd = r"C:\\Users\\Administrator\\AppData\\Local\\Programs\\Tesseract-OCR\\tesseract.exe"
champion_templates_dir = "champions_templates"
search_interval = 0.2
match_threshold = 13

running = False
paused = False
champion_templates = []
d_limit = 0
d_counter = 0

shop_boxes = [
    (480, 929, 668, 1066),
    (682, 929, 871, 1066),
    (885, 929, 1068, 1066),
    (1082, 929, 1271, 1066),
    (1285, 929, 1473, 1066)
]

box_centers = [((x1 + x2)//2, (y1 + y2)//2) for (x1, y1, x2, y2) in shop_boxes]

class Communicator(QObject):
    update_status_signal = pyqtSignal(str)

comm = Communicator()
start_time = time.time()

def grab_shop_region():
    try:
        return [np.array(ImageGrab.grab(bbox=box)) for box in shop_boxes]
    except Exception as e:
        comm.update_status_signal.emit(f"Mağaza görüntüsü alınamadı: {e}")
        return []

def crop_face(img):
    return img[22:105, 7:174]

def find_all_champions_in_shop(shop_imgs):
    matched = set()
    orb = cv2.ORB_create()
    for i, shop_img in enumerate(shop_imgs):
        cropped = crop_face(shop_img)
        kp1, des1 = orb.detectAndCompute(cropped, None)
        if des1 is None:
            continue
        best_match_count = 0
        best_distance_avg = float('inf')
        for tpl in champion_templates:
            tpl_face = crop_face(tpl)
            kp2, des2 = orb.detectAndCompute(tpl_face, None)
            if des2 is None:
                continue
            bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
            matches = bf.match(des1, des2)
            good_matches = [m for m in matches if m.distance < 45]
            if len(good_matches) >= match_threshold:
                avg_distance = sum(m.distance for m in good_matches) / len(good_matches)
                if len(good_matches) > best_match_count or (len(good_matches) == best_match_count and avg_distance < best_distance_avg):
                    best_match_count = len(good_matches)
                    best_distance_avg = avg_distance
        if best_match_count >= match_threshold:
            matched.add(i)
    return sorted(matched)

def focus_tft_window():
    windows = gw.getWindowsWithTitle('League of Legends')
    for w in windows:
        if 'League of Legends' in w.title:
            try:
                w.activate()
                return True
            except:
                return False
    return False

def press_d_key():
    if focus_tft_window():
        keyboard.press_and_release('d')

class BotThread(QThread):
    def run(self):
        global running, paused, d_counter
        d_counter = 0
        while running:
            if paused:
                time.sleep(0.05)
                continue
            if d_counter >= d_limit:
                comm.update_status_signal.emit("D limiti doldu; bot durdu.")
                break
            if not focus_tft_window():
                comm.update_status_signal.emit("TFT penceresi bulunamadı, bot durduruldu.")
                break
            shop_imgs = grab_shop_region()
            if not shop_imgs:
                time.sleep(search_interval)
                continue
            found = find_all_champions_in_shop(shop_imgs)
            if found:
                for i in found:
                    time.sleep(0.05)
                    pyautogui.moveTo(*box_centers[i], duration=0.1)
                    pyautogui.mouseDown()
                    time.sleep(0.05)
                    pyautogui.mouseUp()
                    time.sleep(0.05)
            else:
                press_d_key()
                d_counter += 1
                comm.update_status_signal.emit(f"D basıldı: {d_counter}/{d_limit}")
            time.sleep(search_interval)
        running = False

class OutlineButton(QPushButton):
    def __init__(self, text, bg_color, parent=None):
        super().__init__(text, parent)
        self.display_text = text
        self.bg_color = bg_color
        self.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.setStyleSheet(f"border-radius: 0px; padding: 6px;")
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.fillRect(self.rect(), self.bg_color)
        font = self.font()
        painter.setFont(font)
        pen = QPen(Qt.black)
        painter.setPen(pen)
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                painter.drawText(self.rect().adjusted(dx, dy, dx, dy), Qt.AlignCenter, self.display_text)
        painter.setPen(QPen(Qt.white))
        painter.drawText(self.rect(), Qt.AlignCenter, self.display_text)

class Overlay(QWidget):
    def __init__(self):
        super().__init__()
        self.offset = QPoint()
        self.timer = QTimer(self)
        self.initUI()
        comm.update_status_signal.connect(self.update_status)
        self.timer.timeout.connect(self.update_runtime)
        self.timer.start(1000)

    def initUI(self):
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setGeometry(100, 100, 360, 310)
        font = QFont("Segoe UI", 10)

        self.input_style = """
            color: white;
            background: rgba(0, 0, 0, 255);
            border: 1px solid #888;
            border-radius: 0px;
            padding-left: 6px;
        """

        self.close_button = QPushButton("X", self)
        self.close_button.setGeometry(320, 10, 25, 25)
        self.close_button.setStyleSheet("""
            QPushButton {
                background-color: red;
                color: white;
                border: none;
                border-radius: 0px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: darkred;
            }
        """)
        self.close_button.clicked.connect(self.safe_quit)

        self.champ_label = QLabel("Şampiyonlar :", self)
        self.champ_label.setFont(font)
        self.champ_label.setStyleSheet("color: white;")
        self.champ_label.setGeometry(15, 50, 330, 20)

        self.champ_input = QLineEdit(self)
        self.champ_input.setFont(font)
        self.champ_input.setGeometry(15, 75, 330, 28)
        self.champ_input.setStyleSheet(self.input_style)
        self.champ_input.setPlaceholderText("örn: yasuo,aatrox,vex")

        self.limit_label = QLabel("D Sayısı :", self)
        self.limit_label.setFont(font)
        self.limit_label.setStyleSheet("color: white;")
        self.limit_label.setGeometry(15, 110, 100, 20)

        self.limit_input = QLineEdit(self)
        self.limit_input.setFont(font)
        self.limit_input.setGeometry(15, 135, 100, 28)
        self.limit_input.setStyleSheet(self.input_style)
        self.limit_input.setPlaceholderText("örn: 20")
        self.limit_input.textChanged.connect(self.update_gold_value)

        self.gold_label = QLabel("0 Gold", self)
        self.gold_label.setFont(font)
        self.gold_label.setStyleSheet("color: yellow;")
        self.gold_label.setGeometry(160, 135, 80, 28)
        self.gold_label.setAlignment(Qt.AlignCenter)

        self.runtime_label = QLabel("0s", self)
        self.runtime_label.setFont(font)
        self.runtime_label.setStyleSheet("color: lightgreen;")
        self.runtime_label.setGeometry(253, 135, 120, 28)
        self.runtime_label.setAlignment(Qt.AlignCenter)

        self.opacity_label = QLabel("Opaklık:", self)
        self.opacity_label.setFont(font)
        self.opacity_label.setStyleSheet("color: white;")
        self.opacity_label.setGeometry(15, 175, 80, 20)

        self.opacity_slider = QSlider(Qt.Horizontal, self)
        self.opacity_slider.setGeometry(95, 175, 160, 20)
        self.opacity_slider.setMinimum(10)
        self.opacity_slider.setMaximum(100)
        self.opacity_slider.setValue(80)
        self.opacity_slider.valueChanged.connect(self.update_opacity)

        self.opacity_value = QLabel("80%", self)
        self.opacity_value.setFont(font)
        self.opacity_value.setStyleSheet("color: white;")
        self.opacity_value.setGeometry(265, 175, 60, 20)

        self.status_label = QLabel("Durum: Beklemede", self)
        self.status_label.setFont(font)
        self.status_label.setGeometry(15, 205, 330, 20)
        self.set_status_color("Beklemede")

        btn_w = 100
        btn_h = 32
        spacing = 10
        total_width = btn_w * 3 + spacing * 2
        start_x = (self.width() - total_width) // 2
        y_pos = 245

        self.start_button = OutlineButton("Başlat", QColor("#2e7d32"), self)
        self.start_button.setGeometry(start_x, y_pos, btn_w, btn_h)
        self.start_button.clicked.connect(start_bot)

        self.pause_button = OutlineButton("Duraklat", QColor("#f9a825"), self)
        self.pause_button.setGeometry(start_x + btn_w + spacing, y_pos, btn_w, btn_h)
        self.pause_button.clicked.connect(pause_bot)

        self.stop_button = OutlineButton("Durdur", QColor("#c62828"), self)
        self.stop_button.setGeometry(start_x + 2 * (btn_w + spacing), y_pos, btn_w, btn_h)
        self.stop_button.clicked.connect(stop_bot)

        self.update_gold_value()
        self.update_opacity(80)
        self.show()

    def safe_quit(self):
        QMetaObject.invokeMethod(self.timer, "stop", Qt.QueuedConnection)
        QTimer.singleShot(100, QApplication.quit)

    def update_opacity(self, value):
        opacity = value / 100
        self.setWindowOpacity(opacity)
        self.opacity_value.setText(f"{value}%")

    def update_gold_value(self):
        try:
            d_val = int(self.limit_input.text())
            self.gold_label.setText(f"{d_val * 2} Gold")
        except ValueError:
            self.gold_label.setText("0 Gold")

    def update_runtime(self):
        elapsed = int(time.time() - start_time)
        h, rem = divmod(elapsed, 3600)
        m, s = divmod(rem, 60)
        self.runtime_label.setText(f"{h}h {m}m {s}s")

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QBrush(QColor(0, 0, 0, 255)))
        painter.setPen(Qt.NoPen)
        painter.drawRect(self.rect())

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            self.offset = e.pos()

    def mouseMoveEvent(self, e):
        if e.buttons() & Qt.LeftButton:
            self.move(self.pos() + e.pos() - self.offset)

    def update_status(self, msg):
        self.status_label.setText(f"Durum: {msg}")
        self.set_status_color(msg)

    def set_status_color(self, msg):
        color = "lightgray"
        if "Beklemede" in msg or "Duraklatıldı" in msg:
            color = "yellow"
        elif "başlatıldı" in msg or "Devam ediyor" in msg:
            color = "lightgreen"
        elif "durduruldu" in msg or "D limiti doldu" in msg:
            color = "red"
        self.status_label.setStyleSheet(f"color: {color};")

bot_thread = None

def start_bot():
    global running, paused, champion_templates, d_limit, bot_thread
    if running:
        return

    champ_input = overlay.champ_input.text().strip().lower()
    names = [n.strip() for n in champ_input.split(',') if n.strip()]
    try:
        d_limit = int(overlay.limit_input.text())
    except ValueError:
        comm.update_status_signal.emit("Geçersiz D sayısı.")
        return

    champion_templates.clear()
    for nm in names:
        path = os.path.join(champion_templates_dir, f"{nm}.png")
        if not os.path.exists(path):
            comm.update_status_signal.emit(f"Bulunamadı: {nm}")
            continue
        img = cv2.imread(path)
        if img is None:
            comm.update_status_signal.emit(f"Okunamadı: {nm}")
            continue
        champion_templates.append(img)

    if not champion_templates:
        comm.update_status_signal.emit("En az bir şampiyon gerekli.")
        return

    running = True
    paused = False
    bot_thread = BotThread()
    bot_thread.start()
    comm.update_status_signal.emit("Bot başlatıldı.")

def pause_bot():
    global paused
    if running:
        paused = not paused
        comm.update_status_signal.emit("Duraklatıldı" if paused else "Devam ediyor")

def stop_bot():
    global running
    running = False
    comm.update_status_signal.emit("Bot durduruldu.")

def toggle_window():
    if overlay.isVisible():
        overlay.hide()
    else:
        overlay.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    overlay = Overlay()
    keyboard.add_hotkey('ctrl+1', start_bot)
    keyboard.add_hotkey('ctrl+2', pause_bot)
    keyboard.add_hotkey('ctrl+3', stop_bot)
    keyboard.add_hotkey('insert', toggle_window)
    sys.exit(app.exec_())