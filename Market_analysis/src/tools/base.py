from pathlib import Path

SYSTEM_PROMPT = Path('./src/prompts/system_prompt.txt').read_text(encoding="utf-8").strip()