
from pathlib import Path

from debtect.cli import _decouvrir_fichiers
from debtect.config import charger

racine = Path(
    r"D:\Study\ProjFinAnnée\Test_PHP\akaunting"
)

spec = charger(str(racine))
fichiers = _decouvrir_fichiers(racine, spec)

print("Nombre de fichiers PHP :", len(fichiers))
print("Exemple :", fichiers[0].relative_to(racine).as_posix())
