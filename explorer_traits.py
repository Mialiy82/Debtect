from debtect.parser import parser

ast = parser("test_traits.php")

def afficher(noeud, niveau=0):
    print("  " * niveau + noeud.type)

    for enfant in noeud.children:
        afficher(enfant, niveau + 1)

afficher(ast)