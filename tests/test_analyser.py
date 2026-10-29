from pathlib import Path

from debtect.cli import _analyser_fichier
from debtect.git_miner import churn

racine = Path(r"D:\Study\ProjFinAnnée\Test_PHP\akaunting")

chemins = [
    "app/Traits/Modules.php",
    "app/Http/Controllers/Settings/Modules.php",
    "app/Models/Document/Document.php",
]

churn_dict = churn(str(racine))

for relatif in chemins:
    resultat = _analyser_fichier(
        racine / relatif,
        racine,
        churn_dict,
    )

    print(f"{relatif} : {resultat.nb_lignes} lignes")
