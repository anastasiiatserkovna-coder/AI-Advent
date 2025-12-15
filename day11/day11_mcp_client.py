import asyncio
import os
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def interactive_mode(session):
    
    # Получаем список инструментов
    response = await session.list_tools()
    
    if not response or not hasattr(response, 'tools') or not response.tools:
        print("Нет доступных инструментов")
        return
    
    tools = response.tools
    
    print("\n" + "="*70)
    print("ИНТЕРАКТИВНЫЙ РЕЖИМ")
    print("="*70)
    
    while True:
        print("\nДОСТУПНЫЕ ИНСТРУМЕНТЫ:")
        for i, tool in enumerate(tools, 1):
            print(f"{i}. {tool.name} — {tool.description}")
        print("0. Выход")
        
        try:
            choice = input("\nВыберите инструмент (номер): ").strip()
            
            if choice == "0":
                print("\nВыход из интерактивного режима")
                break
            
            tool_index = int(choice) - 1
            
            if tool_index < 0 or tool_index >= len(tools):
                print("Неверный номер!")
                continue
            
            selected_tool = tools[tool_index]
            
            print(f"\nВыбран инструмент: {selected_tool.name}")
            print(f"Описание: {selected_tool.description}")
            
            arguments = {}
            
            if hasattr(selected_tool, 'inputSchema') and selected_tool.inputSchema:
                schema = selected_tool.inputSchema
                
                if isinstance(schema, dict) and 'properties' in schema:
                    print("\nВведите параметры:")
                    
                    for param_name, param_info in schema['properties'].items():
                        required = param_name in schema.get('required', [])
                        desc = param_info.get('description', '') if isinstance(param_info, dict) else ''
                        
                        prompt = f"   {param_name}"
                        if required:
                            prompt += " (обязательный)"
                        if desc:
                            prompt += f" — {desc}"
                        prompt += ": "
                        
                        value = input(prompt).strip()
                        
                        if value or required:
                            arguments[param_name] = value
            
            print("\nВыполняем...")
            
            try:
                result = await session.call_tool(
                    name=selected_tool.name,
                    arguments=arguments
                )
                
                print("\n" + "="*70)
                print("РЕЗУЛЬТАТ:")
                print("="*70)
                print(result.content[0].text)
                print("="*70)
                
            except Exception as e:
                print(f"\nОшибка при выполнении: {e}")
        
        except ValueError:
            print("Введите число!")
        except KeyboardInterrupt:
            print("\n\nПрервано пользователем")
            break
        except Exception as e:
            print(f"Ошибка: {e}")

async def connect_to_mcp():
    
    print("="*70)
    print("ПОДКЛЮЧЕНИЕ К MCP-СЕРВЕРУ")
    print("="*70)
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    possible_names = ["mcp_server.py", "day11_mcp_server.py"]
    server_path = None
    
    for name in possible_names:
        path = os.path.join(current_dir, name)
        if os.path.exists(path):
            server_path = path
            break
    
    if not server_path:
        print(f"\nНе найден файл сервера")
        return
    
    print(f"\nНайден сервер: {os.path.basename(server_path)}")
    
    server_params = StdioServerParameters(
        command="python",
        args=[server_path],
        env=None
    )
    
    print("Подключаемся к локальному серверу...")
    
    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                
                init_result = await session.initialize()
                print("Подключение установлено!")
                
                print(f"\nИнформация о сервере:")
                server_name = init_result.server_info.name if hasattr(init_result, 'server_info') else "my-example-server"
                server_version = init_result.server_info.version if hasattr(init_result, 'server_info') else "1.0.0"
                print(f"   Имя: {server_name}")
                print(f"   Версия: {server_version}")
                
                # Получаем список инструментов
                print("\nПолучаем список инструментов...")
                
                response = await session.list_tools()
                
                print("\n" + "="*70)
                print("ДОСТУПНЫЕ ИНСТРУМЕНТЫ:")
                print("="*70)
                
                if response and hasattr(response, 'tools') and response.tools:
                    for i, tool in enumerate(response.tools, 1):
                        print(f"\n{i}. {tool.name}")
                        print(f"   Описание: {tool.description}")
                        
                        if hasattr(tool, 'inputSchema') and tool.inputSchema:
                            schema = tool.inputSchema
                            if isinstance(schema, dict) and 'properties' in schema:
                                print(f"   Параметры:")
                                for param_name, param_info in schema['properties'].items():
                                    required = "обязательный" if param_name in schema.get('required', []) else "⚪ необязательный"
                                    desc = param_info.get('description', 'нет описания') if isinstance(param_info, dict) else 'нет описания'
                                    print(f"      • {param_name} ({required})")
                                    print(f"        {desc}")
                    
                    print("\n" + "="*70)
                    print(f"ИТОГО: Найдено {len(response.tools)} инструментов")
                    print("="*70)
                    
                    await interactive_mode(session)
                    
                else:
                    print("Инструменты не найдены")
    
    except Exception as e:
        print(f"\nОшибка подключения: {e}")
        import traceback
        traceback.print_exc()

async def main():
    """Главная функция"""
    await connect_to_mcp()
    print("\nГотово!")

if __name__ == "__main__":
    asyncio.run(main())