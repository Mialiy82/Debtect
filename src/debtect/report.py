"""Assemblage du résultat final (F5) — PUR. N'écrit rien sur disque (rôle du CLI)."""

from debtect.models import AnalysisResult, FileAnalysis, Couplage
import json
from dataclasses import asdict


def construire(
    chemin_projet: str,
    date_analyse: str,
    duree: float,
    fichiers: list[FileAnalysis],
    fichiers_echec: list[str],
    couplages: list[Couplage] | None = None,
) -> AnalysisResult:
    fichiers_tries = sorted(fichiers, key=lambda f: (-f.score_hotspot, f.chemin))

    return AnalysisResult(
        chemin_projet=chemin_projet,
        date_analyse=date_analyse,
        duree=duree,
        fichiers=fichiers_tries,
        fichiers_echec=sorted(fichiers_echec),
        couplages=couplages or [],
    )


def vers_json(resultat: AnalysisResult) -> str:
    return json.dumps(asdict(resultat), indent=2, ensure_ascii=False)
