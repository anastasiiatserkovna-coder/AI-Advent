from anthropic import Anthropic
from datetime import datetime
import json
from dotenv import load_dotenv
import os

# ===== ЗАГРУЗКА API КЛЮЧА =====
load_dotenv()
api_key = os.getenv("ANTHROPIC_API_KEY")

if not api_key:
    print("Ошибка: API ключ не найден!")
    print("Создайте файл .env и добавьте: ANTHROPIC_API_KEY=ваш-ключ")
    print("Получить ключ: https://console.anthropic.com")
    exit(1)

# Инициализация клиента Claude
client = Anthropic(api_key=api_key)

# ===== СИСТЕМНЫЙ ПРОМПТ (задаёт формат) =====
SYSTEM_PROMPT = """
Ты AI-ассистент, который ВСЕГДА отвечает в формате JSON.

Формат ответа:
{
  "answer": "текст ответа",
  "used_tool": "название инструмента или null",
  "confidence": "высокая/средняя/низкая",
  "metadata": {
    // дополнительная информация если есть
  }
}

КРИТИЧЕСКИ ВАЖНО:
- Возвращай ТОЛЬКО чистый JSON
- НЕ используй markdown блоки (```json или ```)
- НЕ добавляй никакой текст до или после JSON
- Твой ответ должен начинаться с { и заканчиваться }
- Ответ должен быть валидным JSON без markdown обёрток
- Поля answer, used_tool, confidence и metadata должны быть ВСЕГДА

Пример ПРАВИЛЬНОГО ответа:
{"answer": "текст", "used_tool": null, "confidence": "высокая", "metadata": {}}
"""

# ===== ИНСТРУМЕНТЫ =====

def get_weather(city):
    """Получить погоду в городе"""
    weather_data = {
        "москва": {"temp": 15, "condition": "солнечно", "emoji": "☀️"},
        "санкт-петербург": {"temp": 10, "condition": "дождь", "emoji": "🌧️"},
        "берлин": {"temp": 11, "condition": "пасмурно", "emoji": "🌥️"},
        "париж": {"temp": 14, "condition": "переменная облачность", "emoji": "🌤️"},
    }
    return weather_data.get(city.lower(), {"temp": 18, "condition": "ясно", "emoji": "🌤️"})

def calculate(expression):
    """Математические вычисления"""
    try:
        result = eval(expression)
        return {"result": result, "success": True}
    except Exception as e:
        return {"result": None, "success": False, "error": str(e)}

def get_current_time():
    """Получить текущее время"""
    now = datetime.now()
    return {
        "time": now.strftime("%H:%M:%S"),
        "date": now.strftime("%d.%m.%Y"),
        "timestamp": now.timestamp()
    }

# ===== ОПИСАНИЕ ИНСТРУМЕНТОВ =====

tools = [
    {
        "name": "get_weather",
        "description": "Получить погоду в городе",
        "input_schema": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "Название города"
                }
            },
            "required": ["city"]
        }
    },
    {
        "name": "calculate",
        "description": "Выполнить математическое вычисление",
        "input_schema": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "Математическое выражение для вычисления"
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

# Маппинг функций
tool_functions = {
    "get_weather": get_weather,
    "calculate": calculate,
    "get_current_time": get_current_time
}

# ===== ОБРАБОТКА СООБЩЕНИЙ =====

def process_message(user_message):
    """Обработка с форматированным ответом"""
    
    # Шаг 1: Отправляем с системным промптом
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2048,
        system=SYSTEM_PROMPT,
        tools=tools,
        messages=[{"role": "user", "content": user_message}]
    )
    
    used_tool = None
    
    # Шаг 2: Обработка инструментов
    if response.stop_reason == "tool_use":
        tool_use_block = None
        for block in response.content:
            if block.type == "tool_use":
                tool_use_block = block
                break
        
        if tool_use_block:
            tool_name = tool_use_block.name
            tool_input = tool_use_block.input
            tool_use_id = tool_use_block.id
            used_tool = tool_name
            
            print(f"\n🔧 Вызов инструмента: {tool_name}")
            print(f"📥 Параметры: {tool_input}")
            
            # Вызываем функцию
            tool_result = tool_functions[tool_name](**tool_input)
            print(f"Результат: {tool_result}")
            
            # Отправляем результат обратно Claude
            final_response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=2048,
                system=SYSTEM_PROMPT,
                tools=tools,
                messages=[
                    {"role": "user", "content": user_message},
                    {"role": "assistant", "content": response.content},
                    {
                        "role": "user",
                        "content": [{
                            "type": "tool_result",
                            "tool_use_id": tool_use_id,
                            "content": json.dumps(tool_result, ensure_ascii=False)
                        }]
                    }
                ]
            )
            
            return final_response.content[0].text, used_tool
    
    return response.content[0].text, used_tool

# ===== ПАРСИНГ JSON ОТВЕТА =====

def parse_response(response_text):
    """Извлекает JSON из ответа агента (даже если обёрнут в markdown)"""
    try:
        clean_text = response_text.strip()
        
        # Убираем markdown блоки ```json ... ```
        if "```json" in clean_text:
            clean_text = clean_text.split("```json")[1].split("```")[0]
        elif "```" in clean_text:
            parts = clean_text.split("```")
            if len(parts) >= 2:
                clean_text = parts[1]
        
        clean_text = clean_text.strip()
        
        # Парсим JSON
        data = json.loads(clean_text)
        return data, None
    except json.JSONDecodeError as e:
        return None, f"Ошибка парсинга JSON: {str(e)}"
    except Exception as e:
        return None, f"Ошибка: {str(e)}"

# ===== ОСНОВНОЙ ЦИКЛ =====

print("=" * 60)
print("AI-Агент с форматированием ответа (День 2)")
print("=" * 60)
print("\nАгент отвечает в формате JSON!")
print("Для выхода: 'exit'\n")

while True:
    user_input = input("Вы: ").strip()
    
    if not user_input:
        continue
    
    if user_input.lower() in ['exit', 'выход']:
        print("\nДо свидания!")
        break
    
    try:
        # Получаем ответ
        response_text, used_tool = process_message(user_input)
        
        # Парсим JSON
        parsed_data, error = parse_response(response_text)
        
        if error:
            print(f"\n{error}")
        else:
            # Показываем JSON
            print(f"\nJSON ответ:")
            print(json.dumps(parsed_data, indent=2, ensure_ascii=False))
            
            # Показываем извлечённые поля
            print(f"\nИзвлечённые поля:")
            print(f"   Ответ: {parsed_data.get('answer', 'N/A')}")
            print(f"   Инструмент: {parsed_data.get('used_tool', 'N/A')}")
            print(f"   Уверенность: {parsed_data.get('confidence', 'N/A')}")
        
        print("-" * 60)
        
    except Exception as e:
        print(f"\nОшибка: {str(e)}\n")