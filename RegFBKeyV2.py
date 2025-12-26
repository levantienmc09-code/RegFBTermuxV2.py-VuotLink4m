from datetime import datetime, timedelta
import hashlib
import urllib.parse
import requests
import os
import sys

# ================== CONFIG ==================
LINK4M_TOKEN = "68b5c6a74d9b9e42e653713a"
RAW_TOOL_URL = "https://raw.githubusercontent.com/USERNAME/REPO/main/tool.py"

SECRET = "REGFREE_SECRET_2025"
PREFIX = "Letien09"

HETHAN_PATH = "/sdcard/Android/data/com.facebook.katana/.hethan.txt"
KEY_FILE = "KeyRegFree.txt"
ADMIN_KEY_FILE = "adminkey.txt"

# ================== RUN TOOL ==================
def run_tool_from_github():
    r = requests.get(RAW_TOOL_URL, timeout=15)
    if r.status_code != 200:
        print("❌ Không tải được tool")
        sys.exit()
    exec(r.text, {"__name__": "__main__"})

# ================== ADMIN KEY ==================
def load_admin_keys():
    if not os.path.exists(ADMIN_KEY_FILE):
        return []
    with open(ADMIN_KEY_FILE, encoding="utf-8") as f:
        return [i.strip() for i in f if i.strip()]

# ================== KEY FREE ==================
def gen_key():
    now = datetime.now().strftime("%Y%m%d%H")
    return PREFIX + "-" + hashlib.md5((now + SECRET).encode()).hexdigest()[:10].upper()

def save_hethan(key):
    now = datetime.now()
    end = now + timedelta(hours=24)
    os.makedirs(os.path.dirname(HETHAN_PATH), exist_ok=True)
    with open(KEY_FILE, "w") as f:
        f.write(key)
    with open(HETHAN_PATH, "w") as f:
        f.write(
            f"key: {key}\n"
            f"ngaytaokey: {now:%d/%m/%Y}\n"
            f"giotaokey: {now:%H:%M:%S}\n"
            f"ngayhethan: {end:%d/%m/%Y}\n"
            f"giohethan: {end:%H:%M:%S}\n"
            f"device: android\n"
        )

def check_hethan():
    if not os.path.exists(HETHAN_PATH):
        return False
    data = {}
    with open(HETHAN_PATH) as f:
        for line in f:
            if ":" in line:
                k, v = line.split(":", 1)
                data[k.strip()] = v.strip()
    try:
        end = datetime.strptime(
            data["ngayhethan"] + " " + data["giohethan"],
            "%d/%m/%Y %H:%M:%S"
        )
        return datetime.now() < end
    except:
        return False

# ================== MAIN ==================
print("🔐 TOOL REG FREE 24H")
print("---------------------------------------------")
print("1. Key Free 24h")
print("2. Key Mua")
print("---------------------------------------------")

choice = input("👉 Chọn: ").strip()

# ===== KEY MUA =====
if choice == "2":
    key = input("👉 Nhập key mua: ").strip()
    if key in load_admin_keys():
        print("👑 Key mua hợp lệ – vào tool")
        print("---------------------------------------------")
        run_tool_from_github()
        sys.exit()
    else:
        print("❌ Key sai")
        sys.exit()

# ===== KEY FREE =====
if choice != "1":
    print("❌ Lựa chọn không hợp lệ")
    sys.exit()

# còn hạn → vào thẳng
if check_hethan():
    print("✅ Key Free còn hạn – vào tool")
    print("---------------------------------------------")
    run_tool_from_github()
    sys.exit()

# hết hạn → vượt link
print("⏳ Key Free đã hết hạn")
print("---------------------------------------------")

KEY = gen_key()
google_link = f"https://www.google.com/search?q={KEY}"
encoded = urllib.parse.quote(google_link, safe="")
link4m_api = f"https://link4m.co/st?api={LINK4M_TOKEN}&url={encoded}"

r = requests.get(link4m_api, allow_redirects=False, timeout=10)
if "Location" not in r.headers:
    print("❌ Không tạo được link vượt")
    sys.exit()

short_link = r.headers["Location"]
print("🌐 Vượt link lấy key tại:")
print(short_link)
print("---------------------------------------------")

user_key = input("👉 Dán key lấy: ").strip().upper()
if user_key == KEY:
    print("✅ Key đúngl")
    save_hethan(KEY)
    print("---------------------------------------------")
    run_tool_from_github()
else:
    print("❌ Key sai")
    sys.exit()