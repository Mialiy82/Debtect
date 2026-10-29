from pathlib import Path
from tempfile import TemporaryDirectory

from debtect.config import charger, est_exclu

# Test A : aucun fichier .debtectignore
with TemporaryDirectory() as dossier:
    spec = charger(dossier)

    print("A - vendor :", est_exclu(spec, "vendor/a.php"))
    print("A - storage :", est_exclu(spec, "storage/app/a.php"))


# Test B : fichier .debtectignore personnalisé
with TemporaryDirectory() as dossier:
    chemin_ignore = Path(dossier) / ".debtectignore"
    chemin_ignore.write_text(
        "# commentaire\n\noverrides/\n!storage/\n",
        encoding="utf-8",
    )

    spec = charger(dossier)

    print("B - overrides :", est_exclu(spec, "overrides/a.php"))
    print("B - storage :", est_exclu(spec, "storage/app/a.php"))
    print("B - vendor :", est_exclu(spec, "vendor/a.php"))
