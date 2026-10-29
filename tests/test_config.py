from debtect.config import DEFAULT_MOTIFS, _construire, est_exclu

spec = _construire(DEFAULT_MOTIFS)
chemins = [
    "vendor/a.php",
    "app/vendor/a.php",
    "resources/views/x.blade.php",
    "tests/Feature/A.php",
    "app/Models/User.php",
]

for chemin in chemins:
    print(chemin, "->", est_exclu(spec, chemin))

motifs_personnalises = DEFAULT_MOTIFS + [
    "overrides/",
    "!storage/",
]

spec_personnalise = _construire(motifs_personnalises)

print(
    "overrides/x.php ->",
    est_exclu(spec_personnalise, "overrides/x.php"),
)
print(
    "storage/app/x.php ->",
    est_exclu(spec_personnalise, "storage/app/x.php"),
)

chemin_windows = r"app\vendor\a.php"

print(
    chemin_windows,
    "->",
    est_exclu(spec, chemin_windows),
)
