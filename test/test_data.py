# -*- coding: utf-8  -*-

from TSBVMIP.engine import VM
from TSBVMIP.value_containers import ValueInt, ValueIntArrayRef, convert_values


def test_data_sum():
    m = VM()
    m.load_file_code('data/sum.yaml')
    cargs = m.convert_args([1, 5])
    ret = m.run(*cargs)
    assert ret == ValueInt(15)


def test_data_bubblesort():
    m = VM()
    m.load_file_code('data/bubblesort.yaml')
    cargs = m.convert_args([[5, 5, 1, -8, 2]])
    ret = m.run(*cargs)
    expected = ValueIntArrayRef(convert_values(ValueIntArrayRef, [-8, 1, 2, 5, 5]))
    assert ret == expected
