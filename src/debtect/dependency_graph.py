"""Graphe de dépendances et analyse d'impact (F9) — PUR. use/extends/implements + BFS/DFS."""

from tree_sitter import Node
from collections import deque

from debtect.ast_utils import parcourir
from debtect.models import InfoDependances

def extraire(ast: Node) -> InfoDependances:
    espace_de_noms = ""
    declarations = []
    imports = {}
    references = []

    for noeud in parcourir(ast):

        if noeud.type == "namespace_definition":
            nom = noeud.child_by_field_name("name")
            if nom:
                espace_de_noms = nom.text.decode("utf-8")

        elif noeud.type in {
            "class_declaration",
            "interface_declaration",
            "trait_declaration",
            "enum_declaration",
        }:
            nom = noeud.child_by_field_name("name")
            if nom:
                nom_complet = (
                    f"{espace_de_noms}\\{nom.text.decode('utf-8')}"
                    if espace_de_noms
                    else nom.text.decode("utf-8")
                )
                declarations.append(nom_complet)

        elif noeud.type == "namespace_use_declaration":
            _extraire_imports(noeud, imports)

        elif noeud.type in {
            "base_clause",
            "class_interface_clause",
            "use_declaration",
        }:
            for enfant in noeud.named_children:
                if enfant.type in {"name", "qualified_name"}:
                    references.append(enfant.text.decode("utf-8"))

    return InfoDependances(
        espace_de_noms=espace_de_noms,
        declarations=declarations,
        imports=imports,
        references=references,
    )

def _extraire_imports(noeud: Node, imports: dict[str, str]) -> None:
    clauses = []

    prefixe = None
    groupe = None

    for enfant in noeud.children:
        if enfant.type == "namespace_use_clause":
            clauses.append(enfant)
        elif enfant.type == "namespace_name":
            prefixe = enfant.text.decode("utf-8")
        elif enfant.type == "namespace_use_group":
            groupe = enfant

    if groupe:
        for clause in groupe.named_children:
            clauses.append(clause)

    for clause in clauses:
        enfants = clause.named_children

        if not enfants:
            continue

        # Ignorer les imports de fonctions et de constantes.
        if clause.children[0].type in {"function", "const"}:
            continue

        nom_noeud = enfants[0]
        nom = nom_noeud.text.decode("utf-8")

        alias = None

        for i, enfant in enumerate(clause.children):
            if enfant.type == "as" and i + 1 < len(clause.children):
                alias = clause.children[i + 1].text.decode("utf-8")
                break

        nom_complet = f"{prefixe}\\{nom}" if prefixe else nom
        nom_court = alias or nom.split("\\")[-1]

        imports[nom_court] = nom_complet


def _construire_index(
    infos: dict[str, InfoDependances],
) -> dict[str, list[str]]:
    index = {}

    for chemin in sorted(infos):
        info = infos[chemin]

        for declaration in info.declarations:
            cle = declaration.lower()

            if cle not in index:
                index[cle] = []

            index[cle].append(chemin)

    return index

def _resoudre_reference(
    reference: str,
    info: InfoDependances,
) -> str:
    # 1. Nom absolu : supprimer le \ initial.
    if reference.startswith("\\"):
        return reference[1:]

    # 2. Séparer le premier segment du reste.
    segments = reference.split("\\")
    premier = segments[0]

    # 3. Vérifier si le premier segment correspond à un import.
    if premier in info.imports:
        return "\\".join(
            [info.imports[premier], *segments[1:]]
        )

    # 4. Sinon, utiliser le namespace courant.
    if info.espace_de_noms:
        return f"{info.espace_de_noms}\\{reference}"

    return reference

def resoudre(
    infos: dict[str, InfoDependances],
) -> dict[str, list[str]]:
    index = _construire_index(infos)
    graphe = {}

    for chemin, info in infos.items():
        dependances = set()

        # Les imports sont déjà des noms complets.
        noms_a_resoudre = set(info.imports.values())

        # Les références doivent être résolues selon le namespace.
        for reference in info.references:
            noms_a_resoudre.add(
                _resoudre_reference(reference, info)
            )

        for nom in noms_a_resoudre:
            fichiers_cibles = index.get(nom.lower(), [])

            for fichier_cible in fichiers_cibles:
                if fichier_cible != chemin:
                    dependances.add(fichier_cible)

        graphe[chemin] = sorted(dependances)

    return graphe

def inverser(
    dependances: dict[str, list[str]],
) -> dict[str, list[str]]:
    graphe_inverse = {
        chemin: []
        for chemin in dependances
    }

    for fichier, fichiers_dep in dependances.items():
        for dependance in fichiers_dep:
            if dependance not in graphe_inverse:
                graphe_inverse[dependance] = []

            graphe_inverse[dependance].append(fichier)

    return {
        chemin: sorted(fichiers)
        for chemin, fichiers in graphe_inverse.items()
    }

class ErreurImpact(Exception):
    """Erreur lors du calcul du parcours d'impact."""

def impact(
    dependances: dict[str, list[str]],
    cible: str,
    profondeur: int | None = None,
) -> dict[str, int]:

    if cible not in dependances:
        raise ErreurImpact(f"Fichier inconnu : {cible}")

    graphe_inverse = inverser(dependances)

    distances = {cible: 0}
    file = deque([cible])

    while file:
        courant = file.popleft()
        distance = distances[courant]

        if profondeur is not None and distance >= profondeur:
            continue

        for dependant in graphe_inverse[courant]:
            if dependant not in distances:
                distances[dependant] = distance + 1
                file.append(dependant)

    del distances[cible]

    return distances