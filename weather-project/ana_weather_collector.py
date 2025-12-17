"""
Ana Weather - Сборщик погоды
Каждые 2 минут собирает погоду и сохраняет в JSON
"""

import time
from datetime import datetime
from day13_weather_mcp import create_agent


def collect_weather(agent, city: str = "Warsaw"):
    """Собирает погоду и сохраняет в JSON через MCP"""
    
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Сбор погоды...")
    
    try:
        # Просим Claude получить погоду И сохранить в историю
        agent.chat(
            f"Получи текущую погоду в городе {city} и сохрани её в историю. "
            f"Используй инструмент get_weather чтобы получить данные, "
            f"а затем weather_history с action='add' чтобы сохранить.",
            silent=True
        )
        
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Сохранено в JSON")
        
    except Exception as e:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Ошибка: {e}")


def main():
    """Главная функция сборщика"""
    
    print("\n" + "="*60)
    print("Ana Weather - Сборщик")
    print("="*60)
    
    agent = create_agent()
    if not agent:
        print("Ошибка: не удалось создать агента")
        return
    
    CITY = "Warsaw"
    INTERVAL_MINUTES = 2
    
    print(f"Город: {CITY}")
    print(f"Интервал: {INTERVAL_MINUTES} минут")
    print("Сохраняет в: weather_history.json")
    print("="*60 + "\n")
    
    # Собираем сразу при запуске
    collect_weather(agent, CITY)
    
    collection_count = 1
    
    try:
        while True:
            # Ждём интервал
            for i in range(INTERVAL_MINUTES):
                time.sleep(60)
            
            # Собираем погоду
            collection_count += 1
            print(f"\n[Сбор #{collection_count}]")
            collect_weather(agent, CITY)
    
    except KeyboardInterrupt:
        print(f"\n\nСборщик остановлен")
        print(f"Всего записей собрано: {collection_count}\n")


if __name__ == "__main__":
    main()
