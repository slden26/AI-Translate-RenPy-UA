# AI Translate - Ren'Py UA
<p align="center"><img src="https://github.com/user-attachments/assets/df92a4b2-9753-4e2a-b580-91909a4e8a37" width="" alt=""></p>

Інструмент для автоматичного редагування та перекладу ігрових файлів Ren'Py (.rpy) за допомогою штучного інтелекту (через OpenRouter або інші API).

### Основні функції:
- **Пакетна обробка (Batch Size):** Налаштування кількості рядків для одного запиту до ШІ.
- **Контроль температури (Temperature):** Регулювання точності або творчості відповідей моделі.
- **Автоматичні налаштування:** Всі дані (API ключ, URL, моделі, шляхи) зберігаються у `settings.ini`.
- **Зручний інтерфейс:** Лаконічне вікно з фіксованим розміром.

<p align="center"><img src="https://github.com/user-attachments/assets/c6a7849c-f08e-43eb-aee7-94eba93ff497" width="" alt=""></p>  

### Швидкий старт:
1. Переконайтеся, що встановлено Python.
2. Встановіть необхідну бібліотеку:
   ```cmd
   pip install openai
 
Команда запуску генерації: pyinstaller --noconsole --onefile --icon=icon.ico --name "RenPy_AI_Translator" src/app.py  
Я робив установку і збірку використовуючи venv, щоб не ламати систему.
