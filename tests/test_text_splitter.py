import pytest

from src.text_splitter import split_text

def test_empty_text():
    result = split_text("")

    assert result == []
