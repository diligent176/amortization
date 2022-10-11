"""
tests for project.py
"""
from project import (
    make_table_data,
    payments_per_year,
    mortgage_payment_calc,
    mortgage_payment_accelerated,
    amortization_schedule
)
import pytest


def test_payments_per_year():
    assert payments_per_year("Monthly") == 12
    assert payments_per_year("Weekly") == 52


def test_payments_per_year_err():
    assert payments_per_year("Noncely") == None
    assert payments_per_year(15) == None


def test_mortgage_payment_calc():
    assert mortgage_payment_calc(200000, 30, 4.00, 12) == '954.83'
    assert mortgage_payment_calc(500000, 25, 5.22, 52) == '688.84'


def test_mortgage_payment_calc_err():
    assert mortgage_payment_calc('20000f', 30, 4.00, 12) == ' DATA ERROR!'
    assert mortgage_payment_calc(200000, 30, 0, 12) == ' DATA ERROR!'


def test_mortgage_payment_accelerated():
    assert mortgage_payment_accelerated(500000, 25, 5.22, 52) == '746.85'
    assert mortgage_payment_accelerated(600000, 30, 4.76, 26) == '1566.75'


def test_mortgage_payment_accelerated_err():
    assert mortgage_payment_accelerated(500000, 25, 0, 52) == ' DATA ERROR!'
    assert mortgage_payment_accelerated(500000, 25, 2.3, 13) == ' DATA ERROR!'


def test_make_table_data():

    rate_list = [
        {'lender': 'BMO', 'amort_years': 25, 'rate_percent': 4.81, 'rate_type': 'Fixed', 'term_years': 5, 'term_type': 'Closed'},
        {'lender': 'BMO', 'amort_years': 25, 'rate_percent': 5.17, 'rate_type': 'Fixed', 'term_years': 5, 'term_type': 'Closed'},
        {'lender': 'RBC', 'amort_years': 25, 'rate_percent': 5.44, 'rate_type': 'Fixed', 'term_years': 4, 'term_type': 'Closed'}
    ]

    table_data = make_table_data(rate_list)
    # data from input dicts should be in specific locations in 2-dimensional list
    assert table_data[1][0] == 'BMO'
    assert table_data[2][1] == '5.44%'
    assert table_data[0][5] == '25 years'


def test_make_table_data_err():

    rate_list = [
        {'lender': 'BMO', 'amort_years': 25, 'rate_percent': 4.81, 'rate_type': 'Fixed', 'term_type': 'Closed'},
        {'lender': 'RBC', 'rate_percent': 5.44, 'rate_type': 'Fixed', 'term_years': 4, 'term_type': 'Closed'}
    ]

    table_data = make_table_data(rate_list)
    assert table_data == []


def test_amortization_schedule():
    data = amortization_schedule(500000, 25, 5.22, 52, 688.84)
    # total interest paid after final payment #1300 is $395491.55
    assert data[1299][6] == '$395491.55'

    data = amortization_schedule(600000, 30, 4.76, 26, 1566.75)
    # Starting balance on payment #661 should be $403.18
    assert data[660][1] == '$403.18'
