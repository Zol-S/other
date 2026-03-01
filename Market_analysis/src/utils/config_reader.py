import os
from pathlib import Path

def load_to_env_var(filename: str, env_var: str) -> None:
    token_path = Path(filename)
    if not token_path.exists():
        raise FileNotFoundError(
            "Missing {:}. Create it with your Hugging Face token on a single line.".format(filename)
        )

    token = token_path.read_text(encoding="utf-8").strip()
    if not token:
        raise ValueError("{:} is empty.".format(filename))
    
    os.environ[env_var] = token

load_to_env_var('configs/openai_api_key.txt', 'OPENAI_API_KEY')