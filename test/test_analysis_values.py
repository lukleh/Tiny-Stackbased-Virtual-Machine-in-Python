# -*- coding: utf-8  -*-

from TSBVMIP.analysis.values import BasicValue, INT_VALUE, FLOAT_VALUE, INT_ARRAY_REF, ARRAY_REF
from TSBVMIP import value_types


def test_values():
    assert BasicValue(value_types.INT).equals(BasicValue(value_types.INT))
    assert BasicValue(None).equals(BasicValue(None))
    assert INT_VALUE.equals(INT_VALUE)
    assert INT_VALUE.equals(FLOAT_VALUE) is False
    assert INT_ARRAY_REF.is_array_reference is True
    assert ARRAY_REF.is_array_reference is True
    assert INT_VALUE.is_array_reference is False
    assert INT_ARRAY_REF.is_sub_type(ARRAY_REF)
    assert INT_ARRAY_REF.is_sub_type(INT_ARRAY_REF)
    assert INT_ARRAY_REF.is_sub_type(FLOAT_VALUE) is False
    assert ARRAY_REF.is_sub_type(INT_ARRAY_REF) is False
    assert ARRAY_REF.is_sub_type(ARRAY_REF)