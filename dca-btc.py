# 1. โหลดตัวแปรจาก .env ก่อน
from dotenv import load_dotenv
load_dotenv()

# 2. import library อื่นๆ
import os
import sys
import time
import hmac
import json
import hashlib
import requests
import urllib3
from datetime import datetime

# --- ค่าคงที่และตัวแปรการกำหนดค่า (Configuration & Constants) ---

# ปิดคำเตือน InsecureRequestWarning เมื่อใช้ verify=False
# หมายเหตุ: การใช้ verify=False ไม่ปลอดภัยสำหรับการใช้งานใน Production จริง
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# --- ดึงค่าจาก .env ---
BITKUB_API_KEY = os.environ.get('BITKUB_API_KEY')
BITKUB_API_SECRET = os.environ.get('BITKUB_API_SECRET')
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')
AMOUNT = int(os.environ.get('AMOUNT', 100)) # ตั้งค่าเริ่มต้นเป็น 100 ถ้าไม่พบใน .env

# --- ค่าคงที่สำหรับ Bitkub API ---
BITKUB_API_HOST = 'https://api.bitkub.com'
SYMBOL = 'btc_thb'

# --- ฟังก์ชันสำหรับ Bitkub API ---

def gen_sign(api_secret: str, payload_string: str) -> str:
    """
    สร้าง Signature สำหรับยืนยันตัวตนกับ Bitkub API
    
    Args:
        api_secret: The API secret key.
        payload_string: The string to sign.
        
    Returns:
        The generated signature in hexdigest format.
    """
    return hmac.new(api_secret.encode('utf-8'), payload_string.encode('utf-8'), hashlib.sha256).hexdigest()

def bitkub_api_request(path: str, method: str = 'POST', data: dict = None) -> dict:
    """
    ฟังก์ชันกลางสำหรับส่ง Request ไปยัง Bitkub API
    
    Args:
        path: The API endpoint path (e.g., '/api/v3/market/wallet').
        method: The HTTP method (e.g., 'POST').
        data: The request body payload.
        
    Returns:
        A dictionary containing the JSON response from the API.
    """
    if data is None:
        data = {}
        
    ts = str(round(time.time() * 1000))
    payload_list = [ts, method.upper(), path, json.dumps(data)]
    sig = gen_sign(BITKUB_API_SECRET, ''.join(payload_list))
    
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'X-BTK-TIMESTAMP': ts,
        'X-BTK-SIGN': sig,
        'X-BTK-APIKEY': BITKUB_API_KEY
    }
    
    try:
        response = requests.request(
            method, 
            BITKUB_API_HOST + path, 
            headers=headers, 
            data=json.dumps(data), 
            verify=False # ไม่แนะนำสำหรับ Production
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error during API request to {path}: {e}")
        return {"error": -1, "message": str(e)} # คืนค่า error ในรูปแบบที่สอดคล้องกัน

def get_wallet_balances() -> tuple[float | None, float | None]:
    """
    ดึงข้อมูลยอดคงเหลือในกระเป๋าเงิน (THB และ BTC)
    
    Returns:
        A tuple containing THB balance and BTC balance. Returns (None, None) on failure.
    """
    path = '/api/v3/market/wallet'
    data = bitkub_api_request(path)
    
    if data.get('error') == 0:
        balances = data.get('result', {})
        thb_balance = balances.get('THB', 0)
        btc_balance = balances.get('BTC', 0)
        return thb_balance, btc_balance
    else:
        print(f"Error fetching wallet (API Error): {data}")
        return None, None

def place_buy_order(symbol: str, amount: int) -> dict:
    """
    ส่งคำสั่งซื้อแบบ Market Order
    
    Args:
        symbol: The trading symbol (e.g., 'BTC_THB').
        amount: The amount in THB to buy.
        
    Returns:
        The JSON response from the place-bid API.
    """
    path = '/api/v3/market/place-bid'
    req_body = {
        'sym': symbol.lower(), 
        'amt': amount,       
        'typ': 'market',
        'rat': 10
    }
    print(f"กำลังส่งคำสั่งซื้อ (Market Buy) {amount} THB ({symbol})...")
    response = bitkub_api_request(path, data=req_body)
    print(f"Order Response: {response}")
    return response

# --- ฟังก์ชันสำหรับ Telegram ---

def send_to_telegram(message: str):
    """
    ส่งข้อความไปยัง Telegram Chat ที่กำหนด
    
    Args:
        message: The text message to send.
    """
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {'chat_id': TELEGRAM_CHAT_ID, 'text': message}
    
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        print("Telegram message sent successfully!")
    except requests.exceptions.RequestException as e:
        print(f"Error sending to Telegram: {e}")

# --- ส่วนประมวลผลหลัก (Main Logic) ---

def main():
    """
    ฟังก์ชันหลักในการรันบอท DCA
    """
    # --- 1. ตรวจสอบ Environment Variables ---
    if not all([BITKUB_API_KEY, BITKUB_API_SECRET, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID]):
        print("Error: Environment variables (API Keys, Token, Chat ID) are not set.")
        print("กรุณาตรวจสอบไฟล์ .env ของคุณ")
        sys.exit(1)

    # --- 2. ส่งคำสั่งซื้อ ---
    order_data = place_buy_order(SYMBOL, AMOUNT)
    
    # --- 3. ตรวจสอบผลลัพธ์และส่งการแจ้งเตือน ---
    if order_data.get('error') == 0:
        print("ซื้อสำเร็จ! กำลังดึงยอดคงเหลือ...")
        time.sleep(3) # รอสักครู่เพื่อให้ระบบ Bitkub อัปเดต
        
        thb_bal, btc_bal = get_wallet_balances()
        
        if thb_bal is not None and btc_bal is not None:
            btc_balance_str = f"{btc_bal:.8f}"
            thb_balance_str = f"{thb_bal:,.2f}"
            
            message = f"""{datetime.now().strftime("%Y-%m-%d")}
            
**ภารกิจ DCA สำเร็จ! 🚀**
✨ ได้เวลาเก็บของ!
* **เหรียญ:** {SYMBOL.split('_')[0]}
* **ยอดซื้อ:** {AMOUNT} THB (Market Order)
* **สถานะ:** ✅ เรียบร้อย

💰 **อัปเดต Balance ล่าสุด:**
* **BTC:** {btc_balance_str} 📈
* **THB คงเหลือ:** {thb_balance_str}

🔥 Keep stacking those sats!"""
            
            send_to_telegram(message)
            print(message)
        else:
            print("ซื้อสำเร็จ แต่ดึงยอดคงเหลือล้มเหลว")
            error_message = f"""**ภารกิจ DCA (เกือบ) สำเร็จ ⚠️**

การสั่งซื้อ {SYMBOL} {AMOUNT} THB (Market Order) **สำเร็จแล้ว**
(Response: {order_data})

แต่ **ไม่สามารถดึงยอดคงเหลือล่าสุดได้** กรุณาตรวจสอบในแอป Bitkub ครับ

🔥 Check your sats!"""
            send_to_telegram(error_message)
            
    else:
        print("การสั่งซื้อล้มเหลว")
        error_reason = order_data.get('message', 'Unknown error')
        error_message = f"""**ภารกิจ DCA ล้มเหลว! ❌**

ไม่สามารถสั่งซื้อ {SYMBOL} {AMOUNT} THB (Market Order) ได้
**สาเหตุ:** {error_reason}

🔥 DCA หยุดชะงัก!"""
        send_to_telegram(error_message)

    print("DCA Bot run complete.")


if __name__ == '__main__':
    print("**********************")
    print("Starting DCA Bot...")
    main()
    print("**********************")
