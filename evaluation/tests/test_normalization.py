from nutriscan_eval.normalization import normalize_food_name, normalized_food_set


def test_aliases_and_punctuation_are_normalized() -> None:
    assert normalize_food_name("Paani-Puri!") == "pani puri"
    assert normalize_food_name("Chapatis") == "roti"
    assert normalize_food_name("panipuri") == "pani puri"
    assert normalize_food_name("Pav Bhaji") == normalize_food_name("pavbhaji")
    assert normalized_food_set(["Pakode", "pakora"]) == {"pakora"}
