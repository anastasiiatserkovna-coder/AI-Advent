from anthropic import Anthropic
from datetime import datetime
from dotenv import load_dotenv
import os

# ===== ЗАГРУЗКА API КЛЮЧА =====
# Загружаем переменные из файла .env
load_dotenv()

# Получаем ключ из переменной окружения
api_key = os.getenv("ANTHROPIC_API_KEY")

if not api_key:
    print("Ошибка: API ключ не найден!")
    exit(1)

# Инициализация клиента Claude
client = Anthropic(api_key=api_key)

# ===== ОПРЕДЕЛЕНИЕ ИНСТРУМЕНТОВ =====

def get_weather(city):
    """Получить информацию о погоде в городе"""
    # Симуляция данных о погоде
    weather_data = {
        "москва": "Солнечно, +15°C",
        "санкт-петербург": "Дождь, +10°C",
        "лондон": "Облачно, +12°C",
        "париж": "Переменная облачность, +14°C",
        "берлин": "Пасмурно, +11°C",
        "нью-йорк": "Снег, -2°C"
    }
    return weather_data.get(city.lower(), f"Погода в городе {city}: +18°C, переменная облачность")

def calculate(expression):
    """Выполнить математическое вычисление"""
    try:
        # Безопасное вычисление
        result = eval(expression)
        return f"Результат: {result}"
    except Exception as e:
        return f"Ошибка вычисления: {str(e)}"

def get_current_time():
    """Получить текущее время и дату"""
    now = datetime.now()
    return now.strftime("Текущее время: %H:%M:%S, дата: %d.%m.%Y")

# Описание инструментов для Claude (чтобы он знал что может делать)
tools = [
    {
        "name": "get_weather",
        "description": "Получить информацию о текущей погоде в указанном городе",
        "input_schema": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "Название города на русском или английском языке"
                }
            },
            "required": ["city"]
        }
    },
    {
        "name": "calculate",
        "description": "Выполнить математическое вычисление. Можно использовать +, -, *, /, ** (степень), () (скобки)",
        "input_schema": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "Математическое выражение для вычисления, например: '2 + 2' или '10 * 5'"
                }
            },
            "required": ["expression"]
        }
    },
    {
        "name": "get_current_time",
        "description": "Получить текущее время и дату",
        "input_schema": {
            "type": "object",
            "properties": {}
        }
    }
]

# Маппинг имен инструментов на функции
tool_functions = {
    "get_weather": get_weather,
    "calculate": calculate,
    "get_current_time": get_current_time
}

# ===== ГЛАВНАЯ ФУНКЦИЯ ОБРАБОТКИ СООБЩЕНИЙ =====

def process_message(user_message):
    """Обрабатывает сообщение пользователя и взаимодействует с Claude"""
    
    # Шаг 1: Отправляем запрос Claude с инструментами
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        tools=tools,
        messages=[{"role": "user", "content": user_message}]
    )
    
    # Шаг 2: Проверяем, хочет ли Claude использовать инструмент
    if response.stop_reason == "tool_use":
        # Находим блок с вызовом инструмента
        tool_use_block = None
        for block in response.content:
            if block.type == "tool_use":
                tool_use_block = block
                break
        
        if tool_use_block:
            tool_name = tool_use_block.name
            tool_input = tool_use_block.input
            tool_use_id = tool_use_block.id
            
            # Выводим информацию о вызове инструмента
            print(f"\nАгент вызывает инструмент: {tool_name}")
            print(f"Параметры: {tool_input}")
            
            # Шаг 3: Вызываем соответствующую функцию
            tool_result = tool_functions[tool_name](**tool_input)
            print(f"Результат инструмента: {tool_result}")
            
            # Шаг 4: Отправляем результат обратно Claude
            final_response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1024,
                tools=tools,
                messages=[
                    {"role": "user", "content": user_message},
                    {"role": "assistant", "content": response.content},
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "tool_result",
                                "tool_use_id": tool_use_id,
                                "content": tool_result
                            }
                        ]
                    }
                ]
            )
            
            # Получаем финальный ответ
            assistant_message = final_response.content[0].text
            return assistant_message
    
    # Если инструмент не нужен, возвращаем прямой ответ
    assistant_message = response.content[0].text
    return assistant_message

# ===== ОСНОВНОЙ ЦИКЛ ПРОГРАММЫ =====

print("=" * 60)
print("Консольный AI-агент с инструментами (Claude)")
print("=" * 60)
print("\nЯ могу:")
print("  • Отвечать на любые вопросы")
print("  • Узнавать погоду в городах")
print("  • Выполнять математические вычисления")
print("  • Показывать текущее время")
print("\nПросто задай любой вопрос!")
print("Для выхода введите: 'exit' или 'выход'\n")

while True:
    user_input = input("Вы: ").strip()
    
    if not user_input:
        continue
    
    if user_input.lower() in ['exit', 'выход', 'quit']:
        print("\n👋 До свидания!")
        break
    
    try:
        # Обрабатываем сообщение
        response = process_message(user_input)
        print(f"\nПомощник: {response}\n")
        print("-" * 60)
        
    except Exception as e:
        print(f"\nОшибка: {str(e)}\n")
        print("Проверьте что API ключ правильный и на балансе есть средства.")