from debtect.hotspot import score


def test_score_complexite_et_churn():
    assert score(94, 10) == 940.0


def test_score_churn_nul():
    assert score(0, 183) == 0.0


def test_score_complexite_nulle():
    assert score(5, 0) == 0.0
