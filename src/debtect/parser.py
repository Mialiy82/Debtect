"""Parsing PHP via tree-sitter-php (F1). Lecture disque = impur, construction AST = pur."""

from tree_sitter import Language, Parser
import tree_sitter_php

PHP_LANGUAGE = Language(tree_sitter_php.language_php())
_parser = Parser(PHP_LANGUAGE)

class ErreurParsing(Exception):
  pass

def parser(chemin: str):
  with open(chemin, 'rb') as f: 
    code = f.read()

  tree = _parser.parse(code)
  if tree.root_node.has_error:
    raise Erreur(f"Erreur de parsing pour le fichier: {chemin}")
  
  return tree.root_node