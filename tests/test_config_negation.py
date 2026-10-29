from pathlib import Path

from debtect.config import charger, est_exclu

racine = Path(r"D:\Study\ProjFinAnnée\Test_PHP\akaunting")

spec = charger(str(racine))

for chemin in [
    "overrides/Illuminate/Translation/MessageSelector.php",
    "storage/app/test.php",
    "app/Models/Document/Document.php",
]:
    print(chemin, "->", est_exclu(spec, chemin))
