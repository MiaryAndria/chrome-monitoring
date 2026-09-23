from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parents[3]
OUTPUT_DIR = BASE_DIR / "output"

def save(data, filename_prefix, title, formatter=str):


    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_file = OUTPUT_DIR / f"{filename_prefix}_{timestamp}.txt"

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(f"Rapport : {title}\n")
        f.write(f"Généré le : {datetime.now().strftime('%d/%m/%Y à %H:%M:%S')}\n")
        f.write(f"Nombre d'entrées : {len(data)}\n")
        f.write("=" * 60 + "\n\n")
        for item in data:
            f.write(formatter(item) + "\n")

    print(f"Résultats (.txt) sauvegardés dans : {output_file}")
    return output_file


