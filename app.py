# ==========================================
# 🔧 Force imports to ensure PyInstaller bundles everything
# ==========================================
import requests
import urllib3
import idna
import chardet
import certifi
import pytesseract
import tkinter
from tkinter import filedialog
from PIL import Image

# ==========================================
# 📦 Standard imports
# ==========================================
import os
import sys
import json
import time
import uuid
import random
import threading
import subprocess
import platform
from pathlib import Path
from datetime import datetime, timezone

import eel
import pyautogui
import supabase
from seleniumwire import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from web.src_py.run_reg import RegistrationThread
from web.src_py.key import Check_key
# Initialize Eel
eel.init('web')

# Global variables
registration_running = False
registration_thread = None

def get_base_path():
    """Trả về đường dẫn gốc (khác nhau giữa dev và EXE)"""
    if getattr(sys, 'frozen', False):
        # Đang chạy từ EXE (PyInstaller)
        return sys._MEIPASS
    else:
        # Đang chạy từ Python script
        return os.path.dirname(os.path.abspath(__file__))

def get_tesseract_path():
    """Tự động tìm tesseract"""
    base_path = get_base_path()
    
    possible_paths = [
        os.path.join(base_path, "Tesseract-OCR", "tesseract.exe"),
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        os.path.join(base_path, "tesseract.exe"),
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            print(f"✓ Tìm thấy tesseract tại: {path}")
            return path
    
    print("❌ KHÔNG TÌM THẤY TESSERACT!")
    return ""

# def get_firefox_path():
#     """Tự động tìm Firefox"""
#     base_path = get_base_path()
    
#     possible_paths = [
#         r"C:\Program Files\Mozilla Firefox\firefox.exe",
#         r"C:\Program Files (x86)\Mozilla Firefox\firefox.exe",
#         os.path.join(base_path, "firefox", "firefox.exe"),
#         os.path.join(os.getenv('PROGRAMFILES', 'C:\\Program Files'), "Mozilla Firefox", "firefox.exe"),
#     ]
    
#     for path in possible_paths:
#         if os.path.exists(path):
#             print(f"✓ Tìm thấy Firefox tại: {path}")
#             return path
    
#     print("❌ KHÔNG TÌM THẤY FIREFOX!")
#     return ""

# def get_geckodriver_path():
#     """Tìm geckodriver trong EXE hoặc thư mục hiện tại"""
#     base_path = get_base_path()
    
#     # Các vị trí có thể có geckodriver
#     possible_paths = [
#         os.path.join(base_path, "geckodriver.exe"),
#         os.path.join(os.getcwd(), "geckodriver.exe"),
#         os.path.join(base_path, "drivers", "geckodriver.exe"),
#         "geckodriver.exe"  # Trong PATH
#     ]
    
#     for path in possible_paths:
#         if os.path.exists(path):
#             print(f"✓ Tìm thấy geckodriver tại: {path}")
#             return path
    
#     print("❌ KHÔNG TÌM THẤY GECKODRIVER!")
#     return None

@eel.expose
def select_file(file_type):
    """Mở dialog chọn file"""
    root = tk.Tk()
    root.withdraw()
    root.wm_attributes('-topmost', 1)
    
    if 'Tesseract' in file_type:
        # Trả về đường dẫn tự động tìm được hoặc cho chọn
        auto_path = get_tesseract_path()
        if auto_path:
            root.destroy()
            return auto_path
        
        file_path = filedialog.askopenfilename(
            title="Chọn tesseract.exe",
            filetypes=[("Executable", "tesseract.exe"), ("All files", "*.*")]
        )
    # elif 'Firefox' in file_type:
    #     # Trả về đường dẫn tự động tìm được hoặc cho chọn
    #     auto_path = get_firefox_path()
    #     if auto_path:
    #         root.destroy()
    #         return auto_path
        
    #     file_path = filedialog.askopenfilename(
    #         title="Chọn firefox.exe",
    #         filetypes=[("Executable", "firefox.exe"), ("All files", "*.*")]
    #     )
    # elif 'Geckodriver' in file_type:
    #     # Bắt buộc phải chọn geckodriver thủ công
    #     auto_path = get_geckodriver_path()
    #     initial_dir = os.path.dirname(auto_path) if auto_path else os.getcwd()
        
    #     file_path = filedialog.askopenfilename(
    #         title="Chọn geckodriver.exe",
    #         initialdir=initial_dir,
    #         filetypes=[("Executable", "geckodriver.exe"), ("All files", "*.*")]
    #     )
    else:
        file_path = filedialog.askopenfilename()
    
    root.destroy()
    return file_path if file_path else ""

@eel.expose
def save_path_config(config):
    """Lưu cấu hình đường dẫn vào file JSON"""
    try:
        # Tạo thư mục data nếu chưa có
        data_dir = os.path.join(get_base_path(), 'data')
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
        
        # Đường dẫn file config
        config_path = os.path.join(data_dir, 'path.json')
        
        # Lưu config
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
        
        print(f"✓ Đã lưu cấu hình tại: {config_path}")
        return {"status": "success", "message": "Đã lưu cấu hình!"}
    
    except Exception as e:
        print(f"❌ Lỗi khi lưu cấu hình: {e}")
        return {"status": "error", "message": str(e)}

@eel.expose
def load_path_config():
    """Đọc cấu hình đường dẫn từ file JSON"""
    try:
        config_path = os.path.join(get_base_path(), 'data', 'path.json')
        
        # Nếu file không tồn tại, tự động tìm đường dẫn
        if not os.path.exists(config_path):
            print("⚠ Không tìm thấy file config, tự động tìm đường dẫn...")
            auto_config = {
                "tesseractPath": get_tesseract_path(),
                # "firefoxPath": get_firefox_path(),
                # "geckodriverPath": get_geckodriver_path() or ""
            }
            return auto_config
        
        # Đọc config từ file
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        print(f"✓ Đã đọc cấu hình từ: {config_path}")
        return config
    
    except Exception as e:
        print(f"❌ Lỗi khi đọc cấu hình: {e}")
        # Trả về config mặc định nếu lỗi
        return {
            "tesseractPath": get_tesseract_path(),
            # "firefoxPath": get_firefox_path(),
            # "geckodriverPath": get_geckodriver_path() or ""
        }

@eel.expose
def start_registration(config):
    """Bắt đầu quá trình đăng ký"""
    global registration_running, registration_thread
    
    if registration_running:
        return {"status": "error", "message": "Đăng ký đang chạy!"}
    
    # In ra config nhận được
    RegistrationThread(config)
    
    return {"status": "success", "message": "Đã bắt đầu đăng ký!"}

@eel.expose
def stop_registration():
    """Dừng quá trình đăng ký"""
    global registration_running
    registration_running = False
    return {"status": "success", "message": "Đã dừng đăng ký!"}

# Main function
def main():
    """Khởi động ứng dụng"""
    try:
        # Tạo cửa sổ với kích thước tùy chỉnh
        eel.start('index.html', size=(1600, 900), port=8080)
    except (SystemExit, MemoryError, KeyboardInterrupt):
        print("Đóng ứng dụng...")

@eel.expose
def main_check_key(key):
    try:
        with open(r'data/version_client.json', 'r', encoding="utf-8-sig") as f:
            version = json.load(f)
        
        statuscheckkey = Check_key().check_update(key, version['version_client'])
        
        if statuscheckkey['data']:
            with open('data/key.json', "w", encoding="utf-8") as f:
                json.dump({'key': key}, f, ensure_ascii=False, indent=4)
            eel.start('index.html', size=(1200, 800))
        
        return statuscheckkey
    except Exception as e:
        print(f"Lỗi check key: {e}")
        return {'data': False, 'message': str(e)}


# === CHẠY ỨNG DỤNG ===
if __name__ == '__main__':
    try:
        # Tạo thư mục data nếu chưa có
        Path('data').mkdir(exist_ok=True)
        
        # Kiểm tra key
        try:
            with open(r'data/key.json', "r", encoding="utf-8") as f:
                key_data = json.load(f)
            
            with open(r'data/version_client.json', 'r', encoding="utf-8-sig") as versiondata:
                version = json.load(versiondata)
            
            status_checkkey = Check_key().check_update(key_data['key'], version)
            
            if status_checkkey['data'] == True:
                eel.start('index.html', size=(1200, 800), port=6060)
            else:
                os.remove('data/key.json')
                eel.start('key.html', size=(400, 600), port=6060)
        
        except FileNotFoundError:
            print("⚠️ Chưa có file key.json, mở màn hình nhập key")
            eel.start('key.html', size=(400, 600), port=6060)
        
        except Exception as e:
            print(f"❌ Lỗi: {e}")
            eel.start('key.html', size=(400, 600), port=6060)
    
    except Exception as e:
        print(f"❌ Lỗi nghiêm trọng: {e}")
        input("Nhấn Enter để thoát...")