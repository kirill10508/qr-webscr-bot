import telebot
import qrcode
import io
import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from PIL import Image
import logging

logging.basicConfig(level=logging.INFO)

TOKEN = 'BOT_TOKEN'

bot = telebot.TeleBot(TOKEN)

def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--window-size=1920,1080')
    
    chrome_options.add_argument('--disable-gpu')
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.set_page_load_timeout(30)
    return driver

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    help_text = """

Доступные команды:
1.  /qr <текст или ссылка> - создает QR-код
   Пример: /qr https://google.com

2.  /webscr <URL сайта> - создает скриншот веб-страницы
   Пример: /webscr https://github.com

3.  /help - показывает это сообщение
    """
    bot.reply_to(message, help_text)

@bot.message_handler(commands=['qr'])
def generate_qr_code(message):
    try:
        # Получаем текст после команды /qr
        command_parts = message.text.split()
        
        if len(command_parts) < 2:
            bot.reply_to(message, "Пожалуйста, укажите текст или ссылку после команды /qr\nПример: /qr https://google.com")
            return
        
        text_to_encode = ' '.join(command_parts[1:])
        
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(text_to_encode)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Сохраняем в байтовый поток
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        
        # Отправляем изображение
        bot.send_photo(message.chat.id, img_bytes, 
                      caption=f"QR-код создан!\nТекст: {text_to_encode[:100]}{'...' if len(text_to_encode) > 100 else ''}")
        
        logging.info(f"QR-код создан для: {text_to_encode[:50]}")
        
    except Exception as e:
        error_msg = f"Ошибка при создании QR-кода: {str(e)}"
        bot.reply_to(message, error_msg)
        logging.error(f"Ошибка в generate_qr_code: {e}")

@bot.message_handler(commands=['webscr'])
def take_website_screenshot(message):
    try:
        # Получаем URL после команды /webscr
        command_parts = message.text.split()
        
        if len(command_parts) < 2:
            bot.reply_to(message, "Пожалуйста, укажите URL сайта после команды /webscr\nПример: /webscr https://github.com")
            return
        
        url = command_parts[1].strip()
        
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        bot.send_chat_action(message.chat.id, 'upload_photo')
        
        driver = setup_driver()
        
        try:
            # Открываем страницу
            bot.reply_to(message, f"Делаю скриншот {url}...")
            driver.get(url)
            
            # Даем странице загрузиться
            time.sleep(3)
            
            # Создаем скриншот
            screenshot = driver.get_screenshot_as_png()
            
            # Сохраняем в байтовый поток
            img_bytes = io.BytesIO(screenshot)
            img_bytes.seek(0)
            
            # Отправляем изображение
            bot.send_photo(message.chat.id, img_bytes, 
                          caption=f"Скриншот создан!\nURL: {url}")
            
            logging.info(f"Скриншот создан для: {url}")
            
        finally:
            # Всегда закрываем драйвер
            driver.quit()
            
    except Exception as e:
        error_msg = f"❌ Ошибка при создании скриншота: {str(e)}"
        bot.reply_to(message, error_msg)
        logging.error(f"Ошибка в take_website_screenshot: {e}")

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    if message.text.startswith('!qr ') or message.text.startswith('/qr '):
        generate_qr_code(message)
    elif message.text.startswith('!webscr ') or message.text.startswith('/webscr '):
        take_website_screenshot(message)
    else:
        bot.reply_to(message, "Неизвестная команда. Используйте /help для списка команд")

def main():
    """Основная функция запуска бота"""
    print("Бот запущен...")
    print("Доступные команды:")
    print("1. !qr <текст/ссылка> - создает QR-код")
    print("2. !webscr <URL> - создает скриншот сайта")
    print("Для выхода нажмите Ctrl+C")
    
    try:
        bot.polling(none_stop=True, interval=0)
    except KeyboardInterrupt:
        print("\n Бот остановлен")
    except Exception as e:
        print(f"Ошибка: {e}")

if __name__ == "__main__":

    main()
