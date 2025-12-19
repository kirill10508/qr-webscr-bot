# Telegram Bot: QR Code Generator & Website Screenshot

## Описание
Бот для генерации QR-кодов и создания скриншотов веб-сайтов.

## Команды
- `/qr <текст>` - создаёт QR-код
- `/webscr <URL>` - делает скриншот сайта
- `/help` - справка по командам

## Установка
1. Клонировать репозиторий
2. Установить зависимости: `pip install -r requirements.txt`
3. Заменить токен в `bot.py`
4. Запустить: `python bot.py`

## Технологии
- Python 3.8+
- pyTelegramBotAPI
- QRCode
- Selenium WebDriver