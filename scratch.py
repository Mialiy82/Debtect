from debtect.parser import parser
from debtect.complexity import calculer

tree = parser(r"D:\Study\ProjFinAnnée\Test_PHP\akaunting\app\Traits\Modules.php")
resultat = calculer(tree)

print(len(resultat))
print(sum(f.complexite for f in resultat))

top3 = sorted(
    resultat,
    key=lambda f: f.complexite,
    reverse=True
)[:3]

for fonction in top3:
    print(fonction)