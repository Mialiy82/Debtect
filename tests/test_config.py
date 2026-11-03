import pytest

from debtect.config import (
    DEFAULT_MOTIFS,
    _construire,
    est_exclu,
    peut_elaguer,
)


@pytest.mark.parametrize(
    ("chemin", "attendu"),
    [
        ("vendor/a.php", True),
        ("app/vendor/a.php", True),
        ("resources/views/x.blade.php", True),
        ("tests/Feature/A.php", False),
        ("app/Models/User.php", False),
        ("overrides/x.php", True),
        ("storage/app/x.php", False),
        (r"app\vendor\a.php", True),
    ],
)
def test_est_exclu(chemin, attendu):
    motifs = DEFAULT_MOTIFS + [
        "overrides/",
        "!storage/",
    ]

    spec = _construire(motifs)

    assert est_exclu(spec, chemin) is attendu


def test_peut_elaguer_avec_motifs_par_defaut():
    spec = _construire(DEFAULT_MOTIFS)

    assert peut_elaguer(spec) is True


def test_peut_elaguer_avec_negation():
    motifs = DEFAULT_MOTIFS + ["!storage/"]
    spec = _construire(motifs)

    assert peut_elaguer(spec) is False
