from dubbing_pipeline.eval import character_error_rate, levenshtein_distance, normalize_text, word_error_rate


def test_exact_match_has_zero_error():
    assert word_error_rate("namaste duniya", "namaste duniya") == 0
    assert character_error_rate("namaste", "namaste") == 0


def test_edits_increase_error():
    assert word_error_rate("one two three", "one four") > 0
    assert levenshtein_distance("kitten", "sitting") == 3


def test_empty_reference_is_safe():
    assert word_error_rate("", "") == 0
    assert word_error_rate("", "extra") == 1
    assert character_error_rate("", "x") == 1


def test_normalization_handles_case_and_punctuation():
    assert normalize_text("Hello, WORLD!") == "hello world"
    assert word_error_rate("Hello, WORLD!", "hello world") == 0

