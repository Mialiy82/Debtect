
from pathlib import Path

import tree_sitter_php
from tree_sitter import Language, Parser


PHP_LANGUAGE = Language(tree_sitter_php.language_php())
parser = Parser(PHP_LANGUAGE)

source = Path("exploration_f9_2.php").read_bytes()
tree = parser.parse(source)

print(tree.root_node)

def afficher_enfants(noeud, niveau=0):
    indentation = "  " * niveau

    for enfant in noeud.children:
        texte = source[enfant.start_byte:enfant.end_byte].decode("utf-8")

        print(
            f"{indentation}"
            f"type={enfant.type}, "
            f"is_named={enfant.is_named}, "
            f"text={texte!r}"
        )

        afficher_enfants(enfant, niveau + 1)

def parcourir(noeud):
    yield noeud
    for enfant in noeud.children:
        yield from parcourir(enfant)


for noeud in parcourir(tree.root_node):
    if noeud.type == "namespace_use_declaration":
        print("\nIMPORT :", source[noeud.start_byte:noeud.end_byte].decode())
        afficher_enfants(noeud)
