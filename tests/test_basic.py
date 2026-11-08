def add(a, b):
    return a + b


def test_add():
    assert add(2, 3) == 5

def test_add_positive_numbers():
    assert add(10, 20) == 30


def test_add_negative_numbers():
    assert add(-5, -3) == -8

import pytest

@pytest.mark.parametrize(
    "a,b,expected",
    [
        (2, 3, 5),
        (10, 20, 30),
        (-5, -3, -8),
        (0, 5, 5)
    ]
)

def test_add_with_multiple_inputs(a, b, expected):
    assert add(a, b) == expected

def test_file_creation(tmp_path):
    file = tmp_path / "sample.txt"

    file.write_text("Hello RAG")

    assert file.exists()
