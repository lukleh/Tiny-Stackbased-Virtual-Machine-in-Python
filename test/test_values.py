# -*- coding: utf-8  -*-

import pytest

from TSBVMIP.exceptions import ValueException
from TSBVMIP.values import ValueFloat, ValueInt, ValueIntArrayRef


def test_eq():
    assert ValueInt() == ValueInt()
    assert ValueInt(10) == ValueInt(10)
    assert ValueFloat() == ValueFloat()
    assert ValueFloat(1/3) == ValueFloat(1/3)
    assert ValueInt(3) != ValueInt(6)
    assert ValueFloat(4.5) != ValueFloat(7.0)


def test_array_object():
    arr = ValueIntArrayRef()
    assert arr.is_none
    assert arr.length == 0
    pytest.raises(Exception, arr.allocate, 0)
    arr.allocate(10)
    arr[0] = ValueInt(5)
    assert arr[0] == ValueInt(5)
    assert arr[1] == ValueInt()
    pytest.raises(ValueException, arr.__setitem__, 4, 6)
    pytest.raises(ValueException, arr.__setitem__, 4, ValueFloat(8.0))


def test_value_int():
    vs = ValueInt()
    assert vs.is_none
    vs = ValueInt(99)
    assert vs.value == 99
    pytest.raises(ValueException, ValueInt, '99')


def test_value_float():
    vs = ValueFloat()
    assert vs.is_none
    vs = ValueFloat(1/3)
    assert vs.value == 1/3
    pytest.raises(ValueException, ValueFloat, '99')