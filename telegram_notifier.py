"""
Модуль для отправки сообщений в Telegram
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()


class TelegramNotifier:
    """Отправка уведомлений в Telegram"""
    
    def __init__(self):
        self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat_id = os.getenv("TELEGRAM_CHAT_ID")
        
        if not self.bot_token or not self.chat_id:
            print("⚠️ Предупреждение: Telegram токен или chat_id не найдены")
            print("   Уведомления будут только в консоли")
            self.enabled = False
        else:
            self.enabled = True
    
    def send_message(self, text: str) -> bool:
        """
        Отправить сообщение в Telegram
        
        Args:
            text: текст сообщения
            
        Returns:
            True если успешно, False если ошибка
        """
        
        if not self.enabled:
            print("\n📱 [Telegram отключен - сообщение в консоли]")
            print(text)
            return False
        
        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            
            data = {
                "chat_id": self.chat_id,
                "text": text,
                "parse_mode": "HTML"  # Поддержка HTML форматирования
            }
            
            response = requests.post(url, data=data, timeout=10)
            response.raise_for_status()
            
            print("✅ Сообщение отправлено в Telegram!")
            return True
            
        except Exception as e:
            print(f"❌ Ошибка отправки в Telegram: {e}")
            print("\n📱 [Сообщение в консоли]")
            print(text)
            return False


def test_telegram():
    """Тест отправки в Telegram"""
    notifier = TelegramNotifier()
    
    test_message = """
🤖 <b>Тест уведомлений</b>

Это тестовое сообщение от вашего MCP-агента!

✅ Telegram работает!
"""
    
    notifier.send_message(test_message)


if __name__ == "__main__":
    test_telegram()
