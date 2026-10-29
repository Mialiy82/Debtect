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
    nb_lignes: int
    fonctions: list[FunctionInfo]
    complexite_totale: int
    churn: int
    score_hotspot: float
    dependances: list[str]


@dataclass
class AnalysisResult:
    chemin_projet: str
    date_analyse: str
    duree: float
    fichiers: list[FileAnalysis]
    fichiers_echec: list[str]
