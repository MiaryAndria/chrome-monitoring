import json
from pathlib import Path
from datetime import datetime
BASE_DIR = Path(__file__).resolve().parents[3]
OUTPUT_DIR = BASE_DIR / "output"

def save_to_json(data, filename_prefix, indent=2):

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_file = OUTPUT_DIR / f"{filename_prefix}_{timestamp}.json"

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=indent)

    print(f"Résultats (.json) sauvegardés dans : {output_file}")
    return output_file