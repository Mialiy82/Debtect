def parcourir(noeud):
    pile = [noeud]

    while pile:
        courant = pile.pop()
        yield courant
        pile.extend(reversed(courant.children))
