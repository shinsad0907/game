import eel
import threading
import time
from seleniumwire import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import os
import sys
import random
import pyautogui

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

import shbet
import new88ok1
import f8beta2
import mb663

class RegistrationThread:
    def __init__(self, config):
        self.config = config
        self.drivers = []
        self.threads = []
        self.running = True
        
        self._start_registration()
    
    def _get_game_module(self, port):
        """Mapping port -> game module"""
        port_mapping = {
            'new88ok1.com': new88ok1,
            'f8beta2.com': f8beta2,
            'shbet800.com': shbet,
            'mb663.pro': mb663,
        }
        return port_mapping.get(port)
    
    def _arrange_window(self, driver, index, total_windows):
        """Sắp xếp cửa sổ RỘNG và THẤP, xếp chồng offset"""
        try:
            # KÍCH THƯỚC RỘNG VÀ THẤP như trong ảnh
            window_width = 800   # Rộng
            window_height = 950  # Thấp
            
            # Offset để xếp chồng nhưng vẫn thấy được
            offset_x = 30  # Dịch sang phải mỗi cửa sổ
            offset_y = 60  # Dịch xuống dưới mỗi cửa sổ
            
            # Vị trí bắt đầu
            start_x = 10
            start_y = 10
            
            # Tính vị trí với offset
            x = start_x + (index * offset_x)
            y = start_y + (index * offset_y)
            
            # Lấy kích thước màn hình để wrap around nếu tràn
            screen_width, screen_height = pyautogui.size()
            
            # Nếu vị trí tràn màn hình, quay lại đầu với offset mới
            if x + window_width > screen_width:
                x = start_x + 200  # Bắt đầu cột mới
            if y + window_height > screen_height:
                y = start_y
            
            # Đặt vị trí và kích thước cửa sổ
            driver.set_window_position(x, y)
            driver.set_window_size(window_width, window_height)
            
            time.sleep(0.3)
            print(f"   ✓ Cửa sổ {index+1}/{total_windows}: Vị trí ({x}, {y}), Kích thước {window_width}x{window_height}")
        except Exception as e:
            print(f"   ⚠ Không thể sắp xếp cửa sổ {index+1}: {e}")
    
    def _init_driver(self, index, total_windows, proxy=None):
        """Khởi tạo Chrome driver với proxy VÀ ANTI-DETECTION"""
        
        chrome_opts = Options()
        
        chrome_opts.add_argument("--disable-notifications")
        chrome_opts.add_argument("--disable-infobars")
        chrome_opts.add_argument("--disable-extensions")
        chrome_opts.add_argument("--disable-blink-features=AutomationControlled")
        chrome_opts.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_opts.add_experimental_option('useAutomationExtension', False)

        seleniumwire_options = {}
        if proxy:
            parts = proxy.split(':')
            if len(parts) == 4:
                host, port, user, pwd = parts
                proxy_url = f"http://{user}:{pwd}@{host}:{port}"
                seleniumwire_options = {
                    'proxy': {
                        'http': proxy_url,
                        'https': proxy_url,
                        'no_proxy': 'localhost,127.0.0.1'
                    },
                    'verify_ssl': False
                }
        
        driver = webdriver.Chrome(seleniumwire_options=seleniumwire_options, options=chrome_opts)
        
        # SẮP XẾP CỬA SỔ (KHÔNG SCALE)
        self._arrange_window(driver, index, total_windows)
        
        return driver
    
    def _register_worker(self, port, account, index, stt, total_windows):
        """Worker thread cho từng tài khoản"""
        try:
            eel.addResultRow({
                'stt': stt,
                'port': port,
                'username': account['username'],
                'password': account['password'],
                'phone': account['phone'],
                'email': account['email'],
                'fullname': account['fullname'],
                'bankAccount': account['bankAccount'],
                'withdrawCode': account['withdrawCode'],
                'proxy': account['proxy'],
                'status': 'pending'
            })
            
            game_module = self._get_game_module(port)
            if not game_module:
                raise Exception(f"Không tìm thấy module cho port: {port}")
            
            driver = self._init_driver(index, total_windows, account['proxy'])
            self.drivers.append(driver)
            
            initial_delay = random.uniform(2, 5)
            time.sleep(initial_delay)
            
            game = game_module.Game()
            game.tesseract_path = self.config['tesseractPath']
            game.username = account['username']
            game.password = account['password']
            game.fullname = account['fullname']
            game.phone = account['phone']
            game.email = account['email']
            game.maruttien = account['withdrawCode']
            game.chon_tai_khoan = account['bankAccount']
            game.so_tai_khoan = account['accountNumber']
            
            success = game.run_register_process(driver)
            
            status = 'success' if success else 'error'
            eel.updateResultRow(stt, status)
            
        except Exception as e:
            print(f"❌ Lỗi tại worker {stt}: {str(e)}")
            eel.updateResultRow(stt, 'error')
        
        finally:
            pass
    
    def _start_registration(self):
        """Phân chia tài khoản và khởi động các thread"""
        ports = self.config['ports']
        accounts = self.config['accounts']
        
        total_windows = len(accounts)
        
        print(f"\n🚀 BẮT ĐẦU ĐĂNG KÝ:")
        print(f"   • Số cổng: {len(ports)}")
        print(f"   • Số tài khoản: {total_windows}")
        print(f"   • Sắp xếp: Lưới tự động ({total_windows} cửa sổ)\n")
        
        accounts_per_port = len(accounts) // len(ports)
        remainder = len(accounts) % len(ports)
        
        thread_index = 0
        stt = 1
        
        for port_idx, port in enumerate(ports):
            num_accounts = accounts_per_port + (1 if port_idx < remainder else 0)
            
            start_idx = port_idx * accounts_per_port + min(port_idx, remainder)
            end_idx = start_idx + num_accounts
            port_accounts = accounts[start_idx:end_idx]
            
            print(f"   • Port [{port}]: {len(port_accounts)} tài khoản")
            
            for account in port_accounts:
                if not self.running:
                    break
                
                thread = threading.Thread(
                    target=self._register_worker,
                    args=(port, account, thread_index, stt, total_windows)
                )
                thread.daemon = True
                thread.start()
                self.threads.append(thread)
                
                print(f"      → Thread {stt}: {account['username']}")
                
                thread_index += 1
                stt += 1
                
                time.sleep(random.uniform(5, 8))
        
        print(f"\n✓ Đã khởi động {len(self.threads)} threads!\n")
    
    def stop(self):
        """Dừng tất cả các thread"""
        self.running = False
        for driver in self.drivers:
            try:
                driver.quit()
            except:
                pass