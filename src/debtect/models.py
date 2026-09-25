"""Structures de données partagées (PUR) : FileAnalysis, AnalysisResult. À détailler en Conception détaillée."""

from dataclasses import dataclass

@dataclass
class FunctionInfo:
  nom: str
  ligne_debut: int
  ligne_fin: int
  complexite: int

@dataclass
class FileAnalysis:
  chemin: str
  ligne: int
  fonctions: list[FunctionInfo]
  complexite: int
  churn: int
  score_hotspot: float
  erreur_parsing: str | None
  dependances: list[str]

@dataclass
class AnalysisResult:
  chemin_proj: str
  date_analyse: str
  duree: float
  fichiers: list[FileAnalysis]
  fichiers_echec: list[str]