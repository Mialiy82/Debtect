"""Chargement de la configuration (IMPUR). Exclusions par défaut + .debtectignore."""

from pathspec import PathSpec
from pathlib import Path

DEFAULT_MOTIFS = ["vendor/", "node_modules/", ".git/", "storage/", "bootstrap/cache/", "*.blade.php"]

def _construire(lignes: list[str]) -> PathSpec:
  return PathSpec.from_lines("gitwildmatch", lignes)

def est_exclu(spec: PathSpec, chemin_relatif: str) -> bool:
  return spec.match_file(chemin_relatif)

def peut_elaguer(spec: PathSpec) -> bool:
    return all(
        getattr(motif, "include", True) is not False
        for motif in spec.patterns
    )

def charger(racine: str) -> PathSpec:
  chemin_ignore = Path(racine) / ".debtectignore"

  if not chemin_ignore.is_file():
    return _construire(DEFAULT_MOTIFS)

  lignes_personnalisees = chemin_ignore.read_text(encoding="utf-8").splitlines()

  motifs = DEFAULT_MOTIFS + lignes_personnalisees

  return _construire(motifs)