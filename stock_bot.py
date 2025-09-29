import requests
import time
from datetime import datetime
import os

# ============================================
# CONFIGURATION - येथे तुमची details भरा
# ============================================

# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"  # @BotFather पासून मिळवा
TELEGRAM_CHAT_ID = "YOUR_CHAT_ID"  # तुमचा Chat ID

# DhanHQ API Configuration
DHAN_CLIENT_ID = "YOUR_DHAN_CLIENT_ID"
DHAN_ACCESS_TOKEN = "YOUR_DHAN_ACCESS_TOKEN"

# ============================================
# STOCK SYMBOLS (DhanHQ Security IDs)
# ============================================
STOCKS = {
    "NIFTY 50": "13",          # Nifty 50 Index
    "BANK NIFTY": "25",        # Bank Nifty Index
    "SENSEX": "51",            # Sensex Index
    "RELIANCE": "2885",        # Reliance Industries
    "TCS": "11536",            # Tata Consultancy Services
    "TATAMOTORS": "3456"       # Tata Motors
}

# ============================================
# FUNCTIONS
# ============================================

def send_telegram_message(message):
    """Telegram वर message पाठवण्यासाठी"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            print(f"✅ Message sent: {message[:50]}...")
        else:
            print(f"❌ Failed to send message: {response.text}")
    except Exception as e:
        print(f"❌ Error sending telegram message: {e}")


def get_dhan_quote(security_id):
    """DhanHQ API वरून stock price मिळवण्यासाठी"""
    url = "https://api.dhan.co/v2/marketfeed/quote"
    headers = {
        "access-token": DHAN_ACCESS_TOKEN,
        "Content-Type": "application/json"
    }
    payload = {
        "security_id": security_id,
        "exchange_segment": "NSE_EQ" if security_id not in ["13", "25", "51"] else "IDX_I"
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            data = response.json()
            return data.get("data", {}).get("LTP", None)  # Last Traded Price
        else:
            print(f"❌ API Error for {security_id}: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Exception getting quote for {security_id}: {e}")
        return None


def format_price_alert(stock_name, price, prev_price=None):
    """Price alert message format करण्यासाठी"""
    timestamp = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    
    change_emoji = ""
    change_text = ""
    
    if prev_price:
        change = price - prev_price
        change_pct = (change / prev_price) * 100
        
        if change > 0:
            change_emoji = "📈"
            change_text = f"+₹{change:.2f} (+{change_pct:.2f}%)"
        elif change < 0:
            change_emoji = "📉"
            change_text = f"₹{change:.2f} ({change_pct:.2f}%)"
        else:
            change_emoji = "➡️"
            change_text = "No Change"
    
    message = f"""
<b>{change_emoji} {stock_name}</b>
💰 Price: ₹{price:.2f}
{change_text if change_text else ''}
🕐 Time: {timestamp}
"""
    return message.strip()


def monitor_stocks():
    """Main function - stocks monitor करण्यासाठी"""
    print("🚀 Stock Market Bot Started!")
    print("=" * 50)
    
    # Store previous prices
    prev_prices = {}
    
    # Send startup message
    send_telegram_message("✅ <b>Stock Alert Bot Started!</b>\n\nMonitoring: NIFTY, BANKNIFTY, SENSEX, RELIANCE, TCS, TATAMOTORS\n\nUpdates every 1 minute 📊")
    
    while True:
        try:
            current_time = datetime.now().strftime("%H:%M:%S")
            print(f"\n⏰ {current_time} - Fetching prices...")
            
            all_prices = []
            
            for stock_name, security_id in STOCKS.items():
                price = get_dhan_quote(security_id)
                
                if price:
                    prev_price = prev_prices.get(stock_name)
                    message = format_price_alert(stock_name, price, prev_price)
                    all_prices.append(message)
                    prev_prices[stock_name] = price
                    print(f"  ✓ {stock_name}: ₹{price:.2f}")
                else:
                    print(f"  ✗ {stock_name}: Failed to fetch")
                
                time.sleep(0.5)  # API rate limiting साठी
            
            # Send combined message
            if all_prices:
                combined_message = "\n\n" + "─" * 30 + "\n\n"
                combined_message = combined_message.join(all_prices)
                send_telegram_message(combined_message)
            
            # Wait for 1 minute
            print(f"\n💤 Waiting for 60 seconds...")
            time.sleep(60)
            
        except KeyboardInterrupt:
            print("\n\n🛑 Bot stopped by user")
            send_telegram_message("🛑 <b>Stock Alert Bot Stopped</b>")
            break
        except Exception as e:
            print(f"❌ Error in main loop: {e}")
            time.sleep(10)


# ============================================
# MAIN EXECUTION
# ============================================

if __name__ == "__main__":
    # Check if credentials are set
    if TELEGRAM_BOT_TOKEN == "YOUR_TELEGRAM_BOT_TOKEN":
        print("❌ Please set your TELEGRAM_BOT_TOKEN in the code!")
    elif TELEGRAM_CHAT_ID == "YOUR_CHAT_ID":
        print("❌ Please set your TELEGRAM_CHAT_ID in the code!")
    elif DHAN_ACCESS_TOKEN == "YOUR_DHAN_ACCESS_TOKEN":
        print("❌ Please set your DHAN_ACCESS_TOKEN in the code!")
    else:
        monitor_stocks()
