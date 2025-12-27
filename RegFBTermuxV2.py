import time, random, string, re, traceback, os, requests

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
os.system("clear")
# ================= PATH =================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
#SAVE_IMG = os.path.join(BASE_DIR, "Img")
SAVE_TXT = os.path.join(BASE_DIR, "Facebook.txt")
#os.makedirs(SAVE_IMG, exist_ok=True)
UID_TXT = os.path.join(BASE_DIR, "UID.txt")

# ================= CONFIG =================
FIREFOX_BIN = "/data/data/com.termux/files/usr/bin/firefox"
GECKO_PATH  = "/data/data/com.termux/files/usr/bin/geckodriver"
MAIL_API = "https://hunght1890.com/"

# ================= RANDOM =================
HO  = ["Nguyễn","Trần","Lê","Phạm","Hoàng","Huỳnh","Phan","Vũ","Võ","Đặng"]
TEN = ["An","Bình","Bảo","Chi","Dương","Giang","Hà","Hải","Hiếu"]
Domain = ["@hunght1890.com","@ait-tesol.edu.vn"]
def random_name():
    return random.choice(HO), random.choice(TEN)

def random_email():
    return f"letien09.{random.randint(100000,999999)}{random.choice(Domain)}"

def random_pass():
    return "@Letien09"#+ "".join(random.choices(string.digits, k=4))

# ================= GET UID =================
def get_uid(driver):
    """
    Lấy UID Facebook acc vừa tạo
    Ưu tiên profile_id → fallback userID
    """
    html = driver.page_source

    m = re.search(r'"profile_id":\s*"(\d+)"', html)
    if m:
        return m.group(1)

    m = re.search(r'"profile_id":(\d+)', html)
    if m:
        return m.group(1)

    m = re.search(r'"userID":"(\d+)"', html)
    if m:
        return m.group(1)

    # Thêm cách tìm UID khác
    m = re.search(r'"actorID":"(\d+)"', html)
    if m:
        return m.group(1)

    # Thử tìm trong URL nếu là trang profile
    current_url = driver.current_url
    if "facebook.com/profile.php" in current_url:
        m = re.search(r'id=(\d+)', current_url)
        if m:
            return m.group(1)
    elif "facebook.com/" in current_url and not "facebook.com/home" in current_url:
        # Trang cá nhân có username
        parts = current_url.split("facebook.com/")[1].split("/")[0]
        if parts and parts != "home" and parts != "me" and "?" not in parts:
            # Đây có thể là username, không phải UID số
            # Ta cần lấy UID từ dữ liệu trang
            pass

    return "UNKNOWN"

# ================= HUMAN TYPE =================
def human_type(el, text):
    for ch in text:
        el.send_keys(ch)
        time.sleep(random.uniform(0.1, 0.2))

# ================= DRIVER (FIX LAG FIREFOX) =================
def new_driver():
    opt = Options()
    opt.binary_location = FIREFOX_BIN
    opt.add_argument("--headless")

    opt.set_preference("permissions.default.image", 2)
    opt.set_preference("media.autoplay.default", 5)
    opt.set_preference("media.autoplay.blocking_policy", 2)
    opt.set_preference("media.volume_scale", "0.0")
    opt.set_preference("toolkit.cosmeticAnimations.enabled", False)
    opt.set_preference("ui.prefersReducedMotion", 1)
    opt.set_preference("layout.css.prefers-reduced-motion.enabled", True)
    opt.set_preference("dom.webnotifications.enabled", False)
    

    driver = webdriver.Firefox(
        service=Service(GECKO_PATH),
        options=opt
    )
    driver.set_page_load_timeout(40)
    return driver

# ================= CLEAR TRACE =================
def clear_browser(driver):
    try:
        driver.delete_all_cookies()
        driver.execute_script("window.localStorage.clear();")
        driver.execute_script("window.sessionStorage.clear();")
        driver.execute_script("""
            if (window.indexedDB && indexedDB.databases) {
                indexedDB.databases().then(dbs => {
                    dbs.forEach(db => indexedDB.deleteDatabase(db.name));
                });
            }
        """)
    except:
        pass

# ================= WAIT FORM =================
def wait_register_form(driver):
    for _ in range(6):
        try:
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.NAME, "firstname"))
            )
            return True
        except:
            try:
                driver.find_element(By.XPATH, "//*[contains(text(),'Create')]").click()
            except:
                pass
            time.sleep(5)
    return False

# ================= GET FB CODE =================
def get_fb_code(email):
    for _ in range(40):
        try:
            data = requests.get(MAIL_API + email, timeout=10).json()
            if data:
                m = re.search(r"FB-(\d{5,6})", data[0].get("body",""))
                if m:
                    return m.group(1)
        except:
            pass
        time.sleep(3)
    return None

# ================= SAVE SUCCESS =================
def save_success(name, email, pwd, uid):
    with open(SAVE_TXT, "a", encoding="utf-8") as f:
        f.write("==========\n")
        f.write(f"Tên Acc: {name}\n")
        f.write(f"UID: {uid}\n")
        f.write(f"Email: {email}\n")
        f.write(f"Pass: {pwd}\n")
        f.write("==========\n")
# ================= SAVE UID ================
def save_uid(uid):
    if not uid or uid == "UNKNOWN":
        return
    with open(UID_TXT, "a", encoding="utf-8") as f:
        f.write(uid + "\n")
# ================= REG CORE =================
def reg_one_with_name(full_name):
    parts = full_name.split(" ", 1)
    ho = parts[0]
    ten = parts[1] if len(parts) > 1 else ""

    email = random_email()
    pwd = random_pass()

    day, month, year = "11", "12", "1999"

    driver = None
    uid = "UNKNOWN"
    try:
        print("Đang Vào Facebook")
        driver = new_driver()
        driver.get("https://www.facebook.com/r.php")
        time.sleep(5)

        try:
            driver.find_element(By.XPATH, "//*[contains(text(),'Create')]").click()
        except:
            pass
        time.sleep(4)

        if not wait_register_form(driver):
            print("------Lỗi Or Checkpoint------")
            return False, uid

        print(f"Đang Nhập Họ Và Tên: {full_name}")
        human_type(driver.find_element(By.NAME, "firstname"), ho)
        human_type(driver.find_element(By.NAME, "lastname"), ten)

        print(f"Đang Nhập Ngày Tháng Năm Sinh: {day}/{month}/{year}")
        Select(driver.find_element(By.NAME,"birthday_day")).select_by_value(day)
        Select(driver.find_element(By.NAME,"birthday_month")).select_by_value(month)
        Select(driver.find_element(By.NAME,"birthday_year")).select_by_value(year)

        print(f"Đang Nhập Email: {email}")
        human_type(driver.find_element(By.NAME, "reg_email__"), email)

        print(f"Đang Nhập Pass: {pwd}")
        human_type(driver.find_element(By.NAME, "reg_passwd__"), pwd)

        driver.find_element(By.XPATH, "//input[@value='2']").click()
        driver.find_element(By.NAME, "websubmit").click()
        time.sleep(15)

        try:
            code_input = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.NAME, "code"))
            )
        except:
            print("------Lỗi Or Checkpoint------")
            return False, uid

        print("Đang Check Mail")
        code = get_fb_code(email)
        if not code:
            print("------Lỗi Or Checkpoint------")
            return False, uid

        print(f"Check Được Mã: {code}")
        human_type(code_input, code)
        time.sleep(3)
        driver.find_element(By.XPATH, "//button").click()
        time.sleep(random.uniform(6, 12))

        # QUAN TRỌNG: Vào trang cá nhân để lấy UID
        print("Đang vào trang cá nhân để lấy UID...")
        
        # Thử nhiều cách vào trang cá nhân
        try:
            # Cách 1: Vào trang me
            driver.get("https://www.facebook.com/me")
            time.sleep(10)
            
            # Cách 2: Thử click vào profile link nếu có
            try:
                profile_link = driver.find_element(By.XPATH, "//a[contains(@href, '/me') or contains(@href, '/profile.php')]")
                profile_link.click()
                time.sleep(8)
            except:
                pass
        except:
            pass

        # Lấy UID từ trang cá nhân
        uid = get_uid(driver)
        print(f"UID tìm được: {uid}")
        save_uid(uid)
        # Nếu vẫn không tìm được UID, thử cách khác
        if uid == "UNKNOWN":
            print("Thử cách khác để lấy UID...")
            try:
                # Thử lấy từ JavaScript
                uid_js = driver.execute_script("""
                    try {
                        // Tìm trong dữ liệu JSON
                        var scripts = document.querySelectorAll('script');
                        for (var s of scripts) {
                            var text = s.textContent || s.innerText;
                            if (text.includes('profile_id') || text.includes('userID')) {
                                var match = text.match(/"profile_id":\s*"?(\\d+)"?/);
                                if (match) return match[1];
                                match = text.match(/"userID":\s*"?(\\d+)"?/);
                                if (match) return match[1];
                            }
                        }
                        return 'UNKNOWN';
                    } catch(e) { return 'UNKNOWN'; }
                """)
                if uid_js and uid_js != "UNKNOWN":
                    uid = uid_js
                    print(f"UID tìm được từ JS: {uid}")
                    
            except:
                pass

        # Vào trang chủ để chụp ảnh (như cũ)
        driver.get("https://www.facebook.com/?stype=lo&flo=1&deoia=1&jlou=AfjAvAkbMeiJnmBqPAh7Wbe7j55CCVrspx5zt1U4czJlJEctxPC3xGHIPEXgxwV3iQPk-shebZbMTJRdjNZKKbuUyvdLto2BdTRC6f4GBtDskw&smuh=21035&lh=AdCBr-Et8GqmQVEsnco")
        time.sleep(10)

    #    img = os.path.join(SAVE_IMG, f"{email}.png")
   #     driver.save_screenshot(img)
        save_success(full_name, email, pwd, uid)

        return True, uid

    except Exception as e:
        traceback.print_exc()
        print(f"------Lỗi Or Checkpoint: {e}------")
        return False, uid

    finally:
        if driver:
            clear_browser(driver)
            driver.quit()

# ================= MAIN =================
def clear_last_lines(n=2):
    for _ in range(n):
        print("\033[F\033[K", end="")

def main():
    os.system("clear")
    total = int(input("Bạn Muốn Reg Bao Nhiêu Acc: "))

    print("1. Auto Random First Name Và Last Name")
    print("2. Bạn Tự Đặt Có Từng Acc")
    t = input("> ").strip()

    names = []
    if t == "2":
        for i in range(total):
            while True:
                print(f"\n=====Tên Acc {i+1}/{total}=====")
                full_name = input("Họ Và Tên: ").strip()
                wc = len(full_name.split())
                if wc < 2 or wc > 3:
                    print("2 - 3 Chữ")
                    print(f"Họ Và Tên: {full_name}")
                    print("Họ Tên Phải 2 - 3 Chữ Em Ơi")
                    time.sleep(2)
                    clear_last_lines(3)
                    continue
                names.append(full_name)
                break
    else:
        for _ in range(total):
            ho, ten = random_name()
            names.append(f"{ho} {ten}")

    success_count = 0
    uids = []
    
    for i, name in enumerate(names, 1):
        print(f"\n===== REG {i}/{total} =====")
        success, uid = reg_one_with_name(name)
        if success:
            success_count += 1
            uids.append(uid)
            print(f"✓ Thành công: {name} | UID: {uid}")
        else:
            print(f"✗ Thất bại: {name}")
        time.sleep(6)

    # Hiển thị tổng kết
    print("\n" + "="*40)
    print(f"TỔNG KẾT: {success_count}/{total} acc thành công")
    
    if uids:
        print("\nTổng UID:")
        print("-" * 20)
        for uid in uids:
            print(uid)
        print("-" * 20)
        
        # Lưu UID vào file riêng
        uid_file = os.path.join(BASE_DIR, "UID.txt")
        with open(uid_file, "w", encoding="utf-8") as f:
            f.write("Tổng UID:\n")
            f.write("="*20 + "\n")
            for uid in uids:
                f.write(uid + "\n")
        print(f"\n✓ Đã lưu UID vào file: {uid_file}")
    
    print("="*40)

if __name__ == "__main__":
    main()
