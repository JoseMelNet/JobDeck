# Crea un pequeño script test.py
from anthropic import Anthropic
import os

api_key = os.getenv("ANTHROPIC_API_KEY")
client = Anthropic(api_key=api_key)

try:
    message = client.messages.create(
        model="claude-3-5-sonnet-20250519",
        max_tokens=100,
        messages=[{"role": "user", "content": "Hola"}]
    )
    print("✅ Funciona con claude-3-5-sonnet-20250519")
except Exception as e:
    print(f"❌ Error: {e}")