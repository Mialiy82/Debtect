from tree_sitter import Language, Parser
import tree_sitter_php

from debtect.ast_utils import parcourir


def test_parcourir_ast_tres_profond():
    php = "<?php $a = " + " . ".join(["'x'"] * 1500) + ";"

    parser = Parser(
        Language(tree_sitter_php.language_php())
    )
    ast = parser.parse(php.encode("utf-8")).root_node

    noeuds = list(parcourir(ast))

    assert noeuds