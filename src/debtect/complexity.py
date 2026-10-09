"""Calcul de la complexité cyclomatique (F2) — module PUR. Entrée : un AST, jamais un chemin."""

from debtect.models import FunctionInfo
from tree_sitter import Node

NOEUD_FUNCTION = {"function_definition","method_declaration"}
NOEUD_DECISION = {"case_statement", "catch_clause", "do_statement", "match_conditional_expression", "conditional_expression",
                  "if_statement", "else_if_clause", "for_statement", "foreach_statement", "while_statement"}

def _parcourir(noeud: Node):
  pile = [noeud]
  while pile:
    courant = pile.pop()
    yield courant
    pile.extend(reversed(courant.children))

def _compter(noeud: Node) -> int:
  return sum(1 for x in _parcourir(noeud) if x.type in NOEUD_DECISION)

def calculer(ast) -> list[FunctionInfo]:
  resultats = []
  for noeud in _parcourir(ast):
    if noeud.type not in NOEUD_FUNCTION:
      continue

    nom = noeud.child_by_field_name("name").text.decode()

    ligne_debut = noeud.start_point[0] + 1
    ligne_fin = noeud.end_point[0] + 1

    complexite = 1 + _compter(noeud)

    resultat = FunctionInfo(
      nom = nom, 
      ligne_debut = ligne_debut,
      ligne_fin = ligne_fin,
      complexite = complexite)

    resultats.append(resultat)
  return resultats

