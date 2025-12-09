from anthropic import Anthropic
from dotenv import load_dotenv
import os
import time
import requests

load_dotenv()
claude_key = os.getenv("ANTHROPIC_API_KEY")
openrouter_key = os.getenv("OPENROUTER_API_KEY")

print("=" * 80)
print("СРАВНЕНИЕ МОДЕЛЕЙ ИИ")
print("=" * 80)

user_prompt = input("\nВведите ваш промпт:\n> ")

print("\n" + "=" * 80)
print("Запускаю тестирование моделей...")
print("=" * 80)

# ===== Claude =====
def test_claude(prompt):
    print("\nClaude Sonnet...")
    client = Anthropic(api_key=claude_key)
    start = time.time()
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}]
    )
    return {
        "model": "Claude Sonnet 4 (Anthropic)",
        "time": time.time() - start,
        "tokens": response.usage.input_tokens + response.usage.output_tokens,
        "response": response.content[0].text
    }

# ===== OpenRouter =====
def test_openrouter(prompt, model_id, model_name):
    print(f"{model_name}...")
    start = time.time()
    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={"Authorization": f"Bearer {openrouter_key}"},
        json={"model": model_id, "messages": [{"role": "user", "content": prompt}], "max_tokens": 500},
        timeout=60
    )
    elapsed = time.time() - start
    result = response.json()
    text = result['choices'][0]['message']['content']
    tokens = result.get('usage', {}).get('total_tokens', int(len(text.split()) * 1.3))
    return {"model": model_name, "time": elapsed, "tokens": tokens, "response": text}

# ===== ЗАПУСК =====
results = [
    test_claude(user_prompt),
    test_openrouter(user_prompt, "openai/gpt-oss-20b:free", "GPT-OSS 20B (OpenAI)"),
    test_openrouter(user_prompt, "mistralai/mistral-7b-instruct:free", "Mistral 7B (Mistral AI)")
]

# ===== РЕЗУЛЬТАТЫ =====
print("\n" + "=" * 80)
print("РЕЗУЛЬТАТЫ")
print("=" * 80)

for i, r in enumerate(results, 1):
    print(f"\n{'=' * 80}")
    print(f"Модель {i}: {r['model']}")
    print(f"Время: {r['time']:.2f} сек")
    print(f"Токены: {r['tokens']}")
    print(f"\nОТВЕТ:")
    print("-" * 80)
    print(r['response'])
    print("-" * 80)

# ===== ТАБЛИЦА =====
print("\n" + "=" * 80)
print("ТАБЛИЦА")
print("=" * 80)
print(f"{'Модель':<35} {'Время (сек)':<15} {'Токены':<10}")
print("-" * 80)
for r in results:
    print(f"{r['model']:<33} {r['time']:<15.2f} {r['tokens']:<10}")

print("\n" + "=" * 80)