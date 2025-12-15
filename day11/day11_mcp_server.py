import asyncio
import sys
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# Создаём сервер
app = Server("my-example-server")

@app.list_tools()
async def list_tools() -> list[Tool]:
    """Список доступных инструментов"""
    try:
        return [
            Tool(
                name="get_weather",
                description="Получить погоду в указанном городе",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "city": {
                            "type": "string",
                            "description": "Название города"
                        }
                    },
                    "required": ["city"]
                }
            ),
            Tool(
                name="calculate",
                description="Простой калькулятор для математических выражений",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "expression": {
                            "type": "string",
                            "description": "Математическое выражение, например '2 + 2'"
                        }
                    },
                    "required": ["expression"]
                }
            ),
            Tool(
                name="read_file",
                description="Прочитать содержимое файла",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "filepath": {
                            "type": "string",
                            "description": "Путь к файлу"
                        }
                    },
                    "required": ["filepath"]
                }
            )
        ]
    except Exception as e:
        print(f"Ошибка в list_tools: {e}", file=sys.stderr)
        return []

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Вызов инструмента"""
    try:
        if name == "get_weather":
            city = arguments.get("city", "Неизвестный город")
            return [TextContent(
                type="text",
                text=f"Погода в городе {city}: -5°C, снег (это пример)"
            )]
        
        elif name == "calculate":
            expression = arguments.get("expression", "")
            try:
                result = eval(expression)
                return [TextContent(
                    type="text",
                    text=f"Результат: {expression} = {result}"
                )]
            except Exception as calc_error:
                return [TextContent(
                    type="text",
                    text=f"Ошибка вычисления: {calc_error}"
                )]
        
        elif name == "read_file":
            filepath = arguments.get("filepath", "")
            return [TextContent(
                type="text",
                text=f"Чтение файла {filepath} (пример)"
            )]
        
        else:
            return [TextContent(
                type="text",
                text=f"Неизвестный инструмент: {name}"
            )]
    except Exception as e:
        print(f"Ошибка в call_tool: {e}", file=sys.stderr)
        return [TextContent(
            type="text",
            text=f"Ошибка: {e}"
        )]

async def main():
    """Запуск сервера"""
    try:
        async with stdio_server() as (read_stream, write_stream):
            await app.run(
                read_stream,
                write_stream,
                app.create_initialization_options()
            )
    except Exception as e:
        print(f"Ошибка запуска сервера: {e}", file=sys.stderr)
        raise

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"Критическая ошибка: {e}", file=sys.stderr)
        sys.exit(1)