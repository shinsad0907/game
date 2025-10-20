import base64
import requests
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import random
import time
import os
import pytesseract
from PIL import Image


class Game:
    def __init__(self):
        self.name = "shbet"
        self.tesseract_path = ""
        self.username = ""
        self.password = ""
        self.fullname = ""
        self.phone = ""
        self.email = ""
        self.maruttien = ""
        self.chon_tai_khoan = ""
        self.so_tai_khoan = ""
        self.driver = None

    def save_bytes(self, b, path):
        with open(path, "wb") as f:
            f.write(b)

    def download_via_requests(self, url, out_path):
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        self.save_bytes(resp.content, out_path)

    def decode_data_url(self, data_url, out_path):
        header, b64 = data_url.split(",", 1)
        data = base64.b64decode(b64)
        if "image/" in header:
            ext = header.split("image/")[1].split(";")[0]
            if ext == "jpeg":
                ext = "jpg"
        else:
            ext = "png"
        if not out_path.lower().endswith(ext):
            out_path = out_path + "." + ext
        self.save_bytes(data, out_path)
        return out_path

    def fetch_blob_via_browser(self, driver, blob_url):
        script = """
        var url = arguments[0];
        var callback = arguments[arguments.length - 1];
        fetch(url).then(r => r.blob()).then(blob => {
            var reader = new FileReader();
            reader.onloadend = () => callback(reader.result);
            reader.onerror = () => callback(null);
            reader.readAsDataURL(blob);
        }).catch(() => callback(null));
        """
        try:
            return driver.execute_async_script(script, blob_url)
        except:
            return None

    def extract_digits_from_image(self, img_path):
        try:
            if self.tesseract_path:
                pytesseract.pytesseract.tesseract_cmd = self.tesseract_path
            img = Image.open(img_path)
            config = "--psm 7 -c tessedit_char_whitelist=0123456789"
            text = pytesseract.image_to_string(img, config=config)
            digits = ''.join([c for c in text if c.isdigit()])
            return digits
        except:
            return None

    def wait_and_click(self, locator, locator_type="xpath", timeout=60, driver=None, use_js=False):
        """Click trực tiếp bằng Selenium hoặc JavaScript"""
        driver = driver or self.driver
        
        if locator_type.lower() == "xpath":
            by = By.XPATH
        elif locator_type.lower() == "id":
            by = By.ID
        elif locator_type.lower() == "name":
            by = By.NAME
        elif locator_type.lower() == "css":
            by = By.CSS_SELECTOR
        else:
            raise ValueError("Unsupported locator type")

        element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((by, locator))
        )
        
        if use_js:
            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
            time.sleep(0.5)
            driver.execute_script("arguments[0].click();", element)
        else:
            element.click()
        
        time.sleep(random.uniform(1.0, 2.0))

    def wait_and_send_keys(self, locator, keys, locator_type="xpath", timeout=60, driver=None):
        """Gõ text"""
        driver = driver or self.driver

        def human_typing(element, text, delay_range=(0.1, 0.3)):
            for char in text:
                element.send_keys(char)
                time.sleep(random.uniform(*delay_range))

        if locator_type.lower() == "xpath":
            by = By.XPATH
        elif locator_type.lower() == "id":
            by = By.ID
        elif locator_type.lower() == "name":
            by = By.NAME
        elif locator_type.lower() == "css":
            by = By.CSS_SELECTOR
        else:
            raise ValueError("Unsupported locator type")

        element = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((by, locator))
        )
        
        element.clear()
        time.sleep(0.5)
        human_typing(element, keys)
        time.sleep(random.uniform(1.0, 2.0))

    def run_register_process(self, driver):
        """Thuật toán đăng ký với error handling đầy đủ"""
        self.driver = driver
        
        try:
            print("📝 Đang mở trang đăng ký...")
            driver.get("https://new88ok1.com/Register")
            time.sleep(random.uniform(10, 15))

            # ĐÓNG POPUP
            try:
                self.wait_and_click('/html/body/div[1]/div/div/gupw-dialog-marquee/aside/div[2]/span')
                print("✓ Đã đóng popup")
                time.sleep(random.uniform(1, 2))
            except:
                try:
                    self.wait_and_click('gupw-dialog-marquee aside div span', locator_type="css")
                    print("✓ Đã đóng popup (CSS)")
                    time.sleep(random.uniform(1, 2))
                except:
                    print("ℹ Không có popup cần đóng")

            # ĐIỀN FORM
            print("⌨️ Đang điền form đăng ký...")
            
            try:
                self.wait_and_send_keys('/html/body/div[1]/div/div/gupw-register/div[2]/div[2]/gupw-register-form/div/form/fieldset[1]/div[1]/div[1]/input', self.username)
                print(f"✓ Đã điền username: {self.username}")
                time.sleep(random.uniform(1, 3))
            except Exception as e:
                print(f"❌ THẤT BẠI: Không thể điền username - {str(e)}")
                driver.quit()
                return False

            try:
                self.wait_and_send_keys('/html/body/div[1]/div/div/gupw-register/div[2]/div[2]/gupw-register-form/div/form/fieldset[1]/div[2]/div[1]/div[2]/input', self.password)
                print("✓ Đã điền password")
                time.sleep(random.uniform(1, 3))
            except Exception as e:
                print(f"❌ THẤT BẠI: Không thể điền password - {str(e)}")
                driver.quit()
                return False

            try:
                self.wait_and_send_keys('/html/body/div[1]/div/div/gupw-register/div[2]/div[2]/gupw-register-form/div/form/fieldset[1]/div[3]/div[1]/div[2]/input', self.password)
                print("✓ Đã điền confirm password")
                time.sleep(random.uniform(1, 3))
            except Exception as e:
                print(f"❌ THẤT BẠI: Không thể điền confirm password - {str(e)}")
                driver.quit()
                return False

            try:
                self.wait_and_send_keys('/html/body/div[1]/div/div/gupw-register/div[2]/div[2]/gupw-register-form/div/form/fieldset[1]/div[4]/div[1]/input', self.fullname)
                print(f"✓ Đã điền fullname: {self.fullname}")
                time.sleep(random.uniform(1, 3))
            except Exception as e:
                print(f"❌ THẤT BẠI: Không thể điền fullname - {str(e)}")
                driver.quit()
                return False

            try:
                self.wait_and_send_keys('/html/body/div[1]/div/div/gupw-register/div[2]/div[2]/gupw-register-form/div/form/fieldset[1]/div[5]/div[1]/input', self.phone)
                print(f"✓ Đã điền phone: {self.phone}")
                time.sleep(random.uniform(1, 3))
            except Exception as e:
                print(f"❌ THẤT BẠI: Không thể điền phone - {str(e)}")
                driver.quit()
                return False

            try:
                self.wait_and_send_keys('/html/body/div[1]/div/div/gupw-register/div[2]/div[2]/gupw-register-form/div/form/fieldset[1]/div[6]/div[1]/input', self.email)
                print(f"✓ Đã điền email: {self.email}")
                time.sleep(random.uniform(2, 4))
            except Exception as e:
                print(f"❌ THẤT BẠI: Không thể điền email - {str(e)}")
                driver.quit()
                return False

            # XỬ LÝ CAPTCHA VÀ SUBMIT
            print("🔐 Đang xử lý captcha...")
            max_attempts = 3
            attempt = 0

            while attempt < max_attempts:
                attempt += 1
                print(f"\n{'='*50}")
                print(f"🔄 LẦN THỬ {attempt}/{max_attempts}")
                print(f"{'='*50}\n")
                
                try:
                    # XỬ LÝ CAPTCHA
                    print("🔐 Đang xử lý captcha...")
                    try:
                        captcha_img_xpath = '/html/body/div[1]/div/div/gupw-register/div[2]/div[2]/gupw-register-form/div/form/fieldset[1]/div[7]/div[1]/gupw-captcha-register-box/img'
                        captcha_input_xpath = '/html/body/div[1]/div/div/gupw-register/div[2]/div[2]/gupw-register-form/div/form/fieldset[1]/div[7]/div[1]/gupw-captcha-register-box/input'
                        
                        try:
                            self.wait_and_click(captcha_input_xpath)
                        except:
                            pass

                        img_elem = driver.find_element(By.XPATH, captcha_img_xpath)
                        src = img_elem.get_attribute("src")
                        current_src = img_elem.get_attribute("currentSrc")
                        if current_src and current_src != src:
                            src = current_src
                        
                        img_path = None
                        
                        if src and src.startswith("http"):
                            try:
                                cookies = driver.get_cookies()
                                session = requests.Session()
                                for cookie in cookies:
                                    session.cookies.set(cookie['name'], cookie['value'])
                                
                                session.headers.update({
                                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                                    'Referer': 'https://new88ok1.com/Register',
                                    'Accept': 'image/avif,image/webp,image/apng,image/*,*/*;q=0.8'
                                })
                                
                                resp = session.get(src, timeout=15)
                                resp.raise_for_status()
                                self.save_bytes(resp.content, "captcha_http.png")
                                img_path = "captcha_http.png"
                                print("✓ Đã tải captcha qua HTTP")
                            except Exception as e:
                                print(f"⚠ Tải HTTP thất bại: {e}")

                        elif src and src.startswith("data:"):
                            try:
                                img_path = self.decode_data_url(src, "captcha_dataurl")
                                print("✓ Đã decode data URL")
                            except Exception as e:
                                print(f"⚠ Decode data URL thất bại: {e}")
                        
                        elif src and src.startswith("blob:"):
                            try:
                                data_url = self.fetch_blob_via_browser(driver, src)
                                if data_url:
                                    img_path = self.decode_data_url(data_url, "captcha_blob")
                                    print("✓ Đã lấy blob URL")
                            except Exception as e:
                                print(f"⚠ Fetch blob thất bại: {e}")
                        
                        if not img_path or not os.path.exists(img_path):
                            try:
                                img_elem.screenshot("captcha_screenshot.png")
                                img_path = "captcha_screenshot.png"
                                print("✓ Đã screenshot captcha")
                            except Exception as e:
                                print(f"⚠ Screenshot thất bại: {e}")

                        code = None
                        if img_path and os.path.exists(img_path):
                            code = self.extract_digits_from_image(img_path)
                            if code:
                                print(f"✓ OCR đọc được: {code}")
                            else:
                                print(f"⚠ OCR không đọc được số")

                        if code:
                            try:
                                captcha_input = driver.find_element(By.XPATH, captcha_input_xpath)
                                captcha_input.clear()
                                time.sleep(0.5)
                                self.wait_and_send_keys(captcha_input_xpath, code)
                                print(f"✓ Đã điền captcha: {code}")
                            except Exception as e:
                                print(f"✗ Không thể điền captcha: {e}")
                        else:
                            print("⚠ Không đọc được mã captcha")
                            
                    except Exception as e:
                        print(f"✗ Lỗi xử lý captcha: {e}")

                    time.sleep(random.uniform(2, 4))

                    # SUBMIT FORM
                    print("📤 Đang gửi form đăng ký...")
                    try:
    # Thử click kiểu thông thường (có chờ hiển thị)
                        xpath_btn = '/html/body/div[1]/div/div/gupw-register/div[2]/div[2]/gupw-register-form/div/form/fieldset[2]/div[2]/div/button[1]'
                        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, xpath_btn)))
                        button = driver.find_element(By.XPATH, xpath_btn)

                        try:
                            # Cuộn đến nút rồi click
                            driver.execute_script("arguments[0].scrollIntoView(true);", button)
                            button.click()
                            print("✓ Đã click nút đăng ký (normal click)")
                        except:
                            # Ép click bằng JavaScript nếu Selenium không tương tác được
                            driver.execute_script("arguments[0].click();", button)
                            print("✓ Đã click nút đăng ký (JS click fallback)")

                    except Exception as e1:
                        # Nếu thất bại, thử Shadow DOM
                        try:
                            shadow_button = driver.execute_script('''
                                let outer = document.querySelector("gupw-register");
                                if (!outer) return null;
                                let outerShadow = outer.shadowRoot || outer;
                                let inner = outerShadow.querySelector("gupw-register-form");
                                if (!inner) return null;
                                let innerShadow = inner.shadowRoot || inner;
                                return innerShadow.querySelector("form fieldset:nth-of-type(2) div div button");
                            ''')
                            if shadow_button:
                                driver.execute_script("arguments[0].scrollIntoView(true);", shadow_button)
                                driver.execute_script("arguments[0].click();", shadow_button)
                                print("✓ Đã click nút đăng ký (shadow DOM)")
                            else:
                                raise Exception("Không tìm thấy nút trong shadow-root")
                        except Exception as e2:
                            # Fallback cuối cùng: click đại nút cuối cùng trong form
                            try:
                                form_btns = driver.find_elements(By.TAG_NAME, "button")
                                if form_btns:
                                    driver.execute_script("arguments[0].scrollIntoView(true);", form_btns[-1])
                                    driver.execute_script("arguments[0].click();", form_btns[-1])
                                    print("✓ Đã click nút đăng ký (fallback cuối)")
                                else:
                                    raise Exception("Không tìm thấy button nào trong trang.")
                            except Exception as e3:
                                print(f"❌ THẤT BẠI: Không thể click nút đăng ký - {e1} | {e2} | {e3}")
                                driver.quit()
                                return False


                    print("⏳ Đang chờ 5 giây kiểm tra kết quả...")
                    time.sleep(5)
                    
                    # KIỂM TRA ALERT
                    try:
                        alert_element = driver.find_element(By.XPATH, '/html/body/div[1]/div/div/gupw-dialog-alert/div[2]/div')
                        if alert_element and alert_element.is_displayed():
                            print("⚠️ PHÁT HIỆN ALERT - Đăng ký thất bại!")
                            
                            try:
                                alert_text = alert_element.text
                                print(f"📝 Nội dung lỗi: {alert_text}")
                            except:
                                pass
                            
                            try:
                                self.wait_and_click('/html/body/div[1]/div/div/gupw-dialog-alert/div[3]/div/div/button', timeout=10)
                                print("✓ Đã click nút đóng alert")
                                time.sleep(random.uniform(2, 3))
                            except Exception as e:
                                print(f"✗ Không thể click nút đóng alert: {e}")
                            
                            if attempt < max_attempts:
                                print(f"\n🔄 Chuẩn bị thử lại lần {attempt + 1}...")
                                time.sleep(random.uniform(2, 3))
                                continue
                            else:
                                print(f"\n❌ THẤT BẠI: ĐÃ HẾT {max_attempts} LẦN THỬ - ĐĂNG KÝ THẤT BẠI!")
                                driver.quit()
                                return False
                        else:
                            print("✅ KHÔNG CÓ ALERT - ĐĂNG KÝ THÀNH CÔNG!")
                            break
                            
                    except:
                        print("✅ KHÔNG CÓ ALERT - ĐĂNG KÝ THÀNH CÔNG!")
                        break
                        
                except Exception as e:
                    print(f"❌ LỖI NGHIÊM TRỌNG: {e}")
                    if attempt < max_attempts:
                        print(f"🔄 Thử lại sau 3 giây...")
                        time.sleep(3)
                        continue
                    else:
                        print(f"❌ THẤT BẠI: Đã hết {max_attempts} lần thử")
                        driver.quit()
                        return False

            time.sleep(random.uniform(3, 5))

            # ĐỔI MÃ RÚT TIỀN
            print("\n🔐 Đang đổi mã rút tiền...")
            try:
                driver.get('https://new88ok1.com/Account/ChangeMoneyPassword')
                time.sleep(random.uniform(3, 5))
                driver.get('https://new88ok1.com/Account/ChangeMoneyPassword')
                time.sleep(random.uniform(3, 5))
                try:
                    self.wait_and_click('/html/body/div[1]/div/div/gupw-dialog-marquee/aside/div[2]/span')
                    print("✓ Đã đóng popup")
                    time.sleep(random.uniform(1, 2))
                except:
                    try:
                        self.wait_and_click('gupw-dialog-marquee aside div span', locator_type="css")
                        print("✓ Đã đóng popup (CSS)")
                        time.sleep(random.uniform(1, 2))
                    except:
                        print("ℹ Không có popup cần đóng")
                
                self.wait_and_send_keys('/html/body/div/ui-view/gupw-app/ui-view/gupw-sample-layout/div[2]/div/ui-view/gupw-member-center-layout/div/div/div[2]/ui-view/gupw-change-money-password/div/div[2]/div/div/section/form/div[1]/div/div/input', self.maruttien)
                time.sleep(random.uniform(1, 2))
                
                self.wait_and_send_keys('/html/body/div/ui-view/gupw-app/ui-view/gupw-sample-layout/div[2]/div/ui-view/gupw-member-center-layout/div/div/div[2]/ui-view/gupw-change-money-password/div/div[2]/div/div/section/form/div[2]/div/div/input', self.maruttien)
                time.sleep(random.uniform(1, 2))
                
                wait = WebDriverWait(driver, 60)
                button = wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div/ui-view/gupw-app/ui-view/gupw-sample-layout/div[2]/div/ui-view/gupw-member-center-layout/div/div/div[2]/ui-view/gupw-change-money-password/div/div[2]/div/div/section/form/div[3]/div/button[1]')))
                driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", button)
                time.sleep(1)
                driver.execute_script("arguments[0].click();", button)
                print("✓ Đã đổi mã rút tiền")
                time.sleep(random.uniform(3, 5))
                
            except Exception as e:
                print(f"❌ THẤT BẠI: Không thể đổi mã rút tiền - {str(e)}")
                import traceback
                traceback.print_exc()
                driver.quit()
                return False

            # THÊM THÔNG TIN RÚT TIỀN
            print("\n🏦 Đang thêm thông tin ngân hàng...")
            try:
                driver.get('https://new88ok1.com/WithdrawApplication')
                time.sleep(random.uniform(3, 5))
                try:
                    self.wait_and_click('/html/body/div[1]/div/div/gupw-dialog-marquee/aside/div[2]/span')
                    print("✓ Đã đóng popup")
                    time.sleep(random.uniform(1, 2))
                except:
                    try:
                        self.wait_and_click('gupw-dialog-marquee aside div span', locator_type="css")
                        print("✓ Đã đóng popup (CSS)")
                        time.sleep(random.uniform(1, 2))
                    except:
                        print("ℹ Không có popup cần đóng")
                    
                try:
                    driver.execute_script("""
                        var images = document.querySelectorAll('img[src*="ActivityEntranceImage"]');
                        images.forEach(function(img) {
                            img.style.display = 'none';
                            if (img.parentElement) img.parentElement.style.display = 'none';
                        });
                        var carousels = document.querySelectorAll('.slick-list, [class*="slick"]');
                        carousels.forEach(function(el) { el.style.display = 'none'; });
                    """)
                    print("✓ Đã ẩn banner quảng cáo")
                    time.sleep(1)
                except:
                    pass
                
                self.wait_and_click('/html/body/div/ui-view/gupw-app/ui-view/gupw-sample-layout/div[2]/div/ui-view/gupw-member-center-layout/div/div/div[2]/ui-view/gupw-withdraw-application/div/div/section[2]/div/section/form/section/div[1]/div/button', use_js=True)
                time.sleep(random.uniform(1, 2))
                
                self.wait_and_send_keys('/html/body/div/ui-view/gupw-app/ui-view/gupw-sample-layout/div[2]/div/ui-view/gupw-member-center-layout/div/div/div[2]/ui-view/gupw-withdraw-application/div/div/section[2]/div/section/form/section/div[1]/div/ul/li/input', self.chon_tai_khoan)
                time.sleep(random.uniform(1, 2))
                
                self.wait_and_click('/html/body/div/ui-view/gupw-app/ui-view/gupw-sample-layout/div[2]/div/ui-view/gupw-member-center-layout/div/div/div[2]/ui-view/gupw-withdraw-application/div/div/section[2]/div/section/form/section/div[1]/div/ul/div/li/a', use_js=True)
                time.sleep(random.uniform(1, 2))
                
                self.wait_and_send_keys('/html/body/div/ui-view/gupw-app/ui-view/gupw-sample-layout/div[2]/div/ui-view/gupw-member-center-layout/div/div/div[2]/ui-view/gupw-withdraw-application/div/div/section[2]/div/section/form/section/div[2]/input', "dak lak")
                time.sleep(random.uniform(1, 2))
                
                self.wait_and_send_keys('/html/body/div/ui-view/gupw-app/ui-view/gupw-sample-layout/div[2]/div/ui-view/gupw-member-center-layout/div/div/div[2]/ui-view/gupw-withdraw-application/div/div/section[2]/div/section/form/section/div[3]/input', self.so_tai_khoan)
                time.sleep(random.uniform(1, 2))
                
                self.wait_and_click('/html/body/div/ui-view/gupw-app/ui-view/gupw-sample-layout/div[2]/div/ui-view/gupw-member-center-layout/div/div/div[2]/ui-view/gupw-withdraw-application/div/div/section[2]/div/section/form/div/button', use_js=True)
                print("✓ Đã thêm thông tin rút tiền")
                time.sleep(random.uniform(3, 5))
                
            except Exception as e:
                print(f"❌ THẤT BẠI: Không thể thêm thông tin ngân hàng - {str(e)}")
                import traceback
                traceback.print_exc()
                driver.quit()
                return False

            # CHUYỂN ĐẾN TRANG NẠP TIỀN
            print("\n💰 Đang chuyển đến trang nạp tiền...")
            try:
                driver.get('https://new88ok1.com/Deposit')
                time.sleep(random.uniform(3, 5))
                try:
                    self.wait_and_click('/html/body/div[1]/div/div/gupw-dialog-marquee/aside/div[2]/span')
                    print("✓ Đã đóng popup")
                    time.sleep(random.uniform(1, 2))
                except:
                    try:
                        self.wait_and_click('gupw-dialog-marquee aside div span', locator_type="css")
                        print("✓ Đã đóng popup (CSS)")
                        time.sleep(random.uniform(1, 2))
                    except:
                        print("ℹ Không có popup cần đóng")
                print("✓ Đã chuyển đến trang nạp tiền")
            except Exception as e:
                print(f"❌ THẤT BẠI: Không thể chuyển trang nạp tiền - {str(e)}")
                return False

            print("\n✅ HOÀN TẤT QUY TRÌNH ĐĂNG KÝ!")
            return True
            
        except Exception as e:
            print(f"\n❌ LỖI TỔNG QUÁT: {str(e)}")
            import traceback
            traceback.print_exc()
            return False