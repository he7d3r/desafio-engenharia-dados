import pytest
from src.app import get_month_name, get_month_options, large_num_formatter


def test_for_numeric_month_name():
    assert get_month_name(1) == 'janeiro'


def test_for_non_numeric_month_name():
    assert get_month_name('outro') == 'todos os meses'


def test_for_return_type():
    for month in range(1, 13):
        assert type(get_month_name(month)) == str


def test_for_formatting_of_number_under_a_thousand():
    assert large_num_formatter(42) == '42.0 '


def test_for_formatting_of_number_under_a_million():
    assert large_num_formatter(42000) == '42.0 mil'


def test_for_formatting_of_number_under_a_billion():
    assert large_num_formatter(4200420) == '4.2 Mi.'


def test_for_formatting_of_number_under_a_trillion():
    assert large_num_formatter(420420420420) == '420.4 Bi.'
