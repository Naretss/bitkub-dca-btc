# Bitkub DCA Bot (บอทซื้อเหรียญแบบถัวเฉลี่ยรายวัน)

This is a simple Python script to automate Dollar-Cost Averaging (DCA) purchases on the Bitkub exchange. The script will place a market buy order for a specified amount and then send a notification to a Telegram chat with the result.

สคริปต์ Python สำหรับการซื้อเหรียญแบบถัวเฉลี่ย (DCA) บน Bitkub Exchange โดยจะทำการส่งคำสั่งซื้อแบบ Market Order ตามจำนวนเงินที่กำหนด และส่งข้อความแจ้งเตือนผลลัพธ์ไปยัง Telegram

---

## Features (คุณสมบัติ)

- Places a market buy order for a fixed amount of THB.
- Fetches current wallet balances after the purchase.
- Sends a detailed notification to Telegram upon success or failure.
- All sensitive information (API keys, etc.) is loaded from an `.env` file for security.

---

## Prerequisites (สิ่งที่ต้องมี)

- Python 3.6+
- Bitkub Account with API Key and Secret
- Telegram Bot and Chat ID

---

## Setup (การติดตั้ง)

1. **Clone or Download:**
   Download the files to your computer.
   (ดาวน์โหลดไฟล์ทั้งหมดลงในเครื่องคอมพิวเตอร์ของคุณ)
2. **Install Dependencies:**
   Open a terminal or command prompt in the project folder and run the following command to install the required libraries:
   (เปิด Terminal หรือ Command Prompt ในโฟลเดอร์ของโปรเจค แล้วรันคำสั่งนี้)

   ```bash
   pip install -r requirements.txt
   ```
3. **Create `.env` file:**
   Create a file named `.env` in the same directory as the script. This file will store your secret keys and settings. Copy the following content into it and replace the placeholder values with your own.
   (สร้างไฟล์ชื่อ `.env` ในโฟลเดอร์เดียวกัน แล้วคัดลอกเนื้อหาข้างล่างไปวาง จากนั้นแก้ไขค่าต่างๆ ให้เป็นของคุณ)

   ```ini
   # Bitkub API Keys
   BITKUB_API_KEY="YOUR_BITKUB_API_KEY"
   BITKUB_API_SECRET="YOUR_BITKUB_API_SECRET"

   # Telegram Bot Credentials
   TELEGRAM_BOT_TOKEN="YOUR_TELEGRAM_BOT_TOKEN"
   TELEGRAM_CHAT_ID="YOUR_TELEGRAM_CHAT_ID"

   # DCA Settings
   AMOUNT="100"
   ```

   - `BITKUB_API_KEY`: Your API Key from Bitkub.
   - `BITKUB_API_SECRET`: Your API Secret from Bitkub.
   - `TELEGRAM_BOT_TOKEN`: The token for your Telegram bot (get it from @BotFather in telegram).
   - `TELEGRAM_CHAT_ID`: The ID of the chat where you want to receive notifications. (get it from @userinfobot in telegram).
   - `AMOUNT`: The amount in **THB** you want to buy in each run (e.g., 100).

---

## Usage (การใช้งาน)

To run the bot manually, execute the following command in your terminal:
(หากต้องการรันบอทด้วยตนเอง ให้ใช้คำสั่งนี้ใน Terminal)

```bash
python dca-btc.py
```

The script will execute once, place the order, and send a notification.

### Automation (การรันอัตโนมัติ)

To make this a true DCA bot, you should schedule it to run automatically.

- **Windows:** Use the **Task Scheduler** to create a new task that runs the `python dca-btc.py` command at your desired interval (e.g., daily).
- **Linux/macOS:** Use **cron** to schedule the job. For example, to run the script every day at 9:00 AM, add the following line to your crontab:

  ```cron
  0 9 * * * /usr/bin/python /path/to/your/project/dca-btc.py
  ```

---

## Disclaimer (ข้อจำกัดความรับผิดชอบ)

- Use this script at your own risk.
- Trading cryptocurrency involves significant risk.
- Ensure your API keys are stored securely and have restricted permissions if possible.
- The use of `verify=False` for API requests is not recommended for production environments as it makes the connection insecure. This is done here to bypass potential SSL certificate issues in simple environments.
