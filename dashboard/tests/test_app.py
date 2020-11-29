import pytest
from src.app import get_month_name, get_month_options, large_num_formatter


def test_for_valid_month_values():
    assert get_month_name(1) == 'janeiro'
    assert get_month_name(12) == 'dezembro'


def test_for_invalid_month_values():
    for value in [0, 13, 'outro', '*']:
        assert get_month_name(value) == 'todos os meses'


def test_for_return_type():
    for month in range(1, 13):
        assert isinstance(get_month_name(month), str)


def test_for_formatting_of_number_under_a_thousand():
    # FIXME: Remove whitespaces
    assert large_num_formatter(1) == '1.0 '
    assert large_num_formatter(42) == '42.0 '
    assert large_num_formatter(999) == '999.0 '


def test_for_formatting_of_number_under_a_million():
    assert large_num_formatter(1000) == '1.0 mil'
    assert large_num_formatter(42000) == '42.0 mil'
    assert large_num_formatter(999949) == '999.9 mil'
    # FIXME: Format '1000.0 mil' as '1.0 Mi.'
    assert large_num_formatter(999950) == '1000.0 mil'


def test_for_formatting_of_number_under_a_billion():
    assert large_num_formatter(1000000) == '1.0 Mi.'
    assert large_num_formatter(4200420) == '4.2 Mi.'
    assert large_num_formatter(999949999) == '999.9 Mi.'
    # FIXME: Format '1000.0 Mi.' as '1.0 Bi.'
    assert large_num_formatter(999950000) == '1000.0 Mi.'


def test_for_formatting_of_number_under_a_trillion():
    assert large_num_formatter(1000000000) == '1.0 Bi.'
    assert large_num_formatter(420420420420) == '420.4 Bi.'
    assert large_num_formatter(999949999999) == '999.9 Bi.'
    # FIXME: Format '1000.0 Bi.' as '1.0 Tri.'
    assert large_num_formatter(999950000000) == '1000.0 Bi.'


def test_for_formatting_of_number_over_a_trillion():
    assert large_num_formatter(1000000000000) == '1.0 Tri.'
    assert large_num_formatter(420420420420000) == '420.4 Tri.'
    assert large_num_formatter(999949999999999) == '999.9 Tri.'
    assert large_num_formatter(999950000000000) == '1000.0 Tri.'
