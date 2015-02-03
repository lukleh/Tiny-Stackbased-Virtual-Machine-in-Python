# -*- coding: utf-8  -*-

import copy

import pytest

import fixtures
import TSBVMIP.instructions as ins
from TSBVMIP import code_parser as parser
from TSBVMIP.value_containers import ValueFloat, ValueInt
from TSBVMIP.exceptions import ParserException


clean_code = dict(func={'name': 'n',
                        'args': [
                            {'type': 'int', 'label': 'a'},
                            {'type': 'float', 'label': 'b'}
                        ],
                        'type': 'int'},
                  lvars=[
                      {'type': 'int', 'label': 'c'},
                      {'type': 'float', 'label': 'd'}
])


def test_labels_duplicate():
    cc = copy.deepcopy(clean_code)
    cc['func']['args'][1]['label'] = 'a'
    dupl_labels = cc
    pytest.raises(ParserException, parser.process_yaml, dupl_labels)

    cc = copy.deepcopy(clean_code)
    cc['lvars'][1]['label'] = 'c'
    dupl_labels = cc
    pytest.raises(ParserException, parser.process_yaml, dupl_labels)

    cc = copy.deepcopy(clean_code)
    cc['lvars'][0]['label'] = 'a'
    dupl_labels = cc
    pytest.raises(ParserException, parser.process_yaml, dupl_labels)

    cc = copy.deepcopy(clean_code)
    cc['ins'] = [{'iload': 'a', 'label': 'x'}, {'ipush': 0, 'label': 'x'}]
    missing_labels = cc
    pytest.raises(ParserException, parser.process_yaml, missing_labels)


def test_labels_missing():
    cc = copy.deepcopy(clean_code)
    cc['ins'] = [{'iload': 'x'}]
    missing_labels = cc
    pytest.raises(ParserException, parser.process_yaml, missing_labels)


def test_labels_bad():
    # label has to be a string
    cc = copy.deepcopy(clean_code)
    cc['lvars'][0]['label'] = 0
    bad_labels = cc
    pytest.raises(ParserException, parser.process_yaml, bad_labels)

    # instructions that point to variables has to use labels
    cc = copy.deepcopy(clean_code)
    cc['ins'] = [{'iload': 0}]
    bad_labels = cc
    pytest.raises(ParserException, parser.process_yaml, bad_labels)

    # label part of instruction
    cc = copy.deepcopy(clean_code)
    cc['ins'] = [{'ipush': 0, 'label': 'x'}]
    bad_labels = cc
    pytest.raises(ParserException, parser.process_yaml, bad_labels)

    # label cannot be last instruction
    cc = copy.deepcopy(clean_code)
    cc['ins'] = [{'ipush': 0}, {'label': 'x'}]
    bad_labels = cc
    pytest.raises(ParserException, parser.process_yaml, bad_labels)

    # label cannot follow label
    cc = copy.deepcopy(clean_code)
    cc['ins'] = [{'label': 'x'}, {'label': 'x2'}, {'ipush': 0}]
    bad_labels = cc
    pytest.raises(ParserException, parser.process_yaml, bad_labels)


def test_arguments():
    cc = copy.deepcopy(clean_code)
    cc['ins'] = ['ipush']
    pytest.raises(ParserException, parser.process_yaml, cc)

    cc = copy.deepcopy(clean_code)
    cc['ins'] = [{'iadd': 0}]
    pytest.raises(ParserException, parser.process_yaml, cc)


def test_code():
    m = parser.process_yaml(clean_code)
    assert len(m.variables) == 4


def test_func():
    m = parser.parse_string(fixtures.load('func.code'))
    assert m.function_name == 'multiple word name'
    assert len(m.variables) == 2
    assert m.argument_count == 2
    assert m.labels == {'a': 0, 'L1': 1}
    assert m.variables == [ValueInt(), ValueFloat()]


def test_variables():
    m = parser.parse_string(fixtures.load('variables.code'))
    assert len(m.variables) == 4
    assert m.argument_count == 1
    assert m.labels == {'a': 0, 'x': 1, 'b': 2, 'y': 3}
    assert m.variables == [ValueInt(), ValueInt(), ValueInt(), ValueFloat()]


def test_instructions():
    m = parser.parse_string(fixtures.load('instructions.code'))
    assert len(m.code) == 6
    assert m.code == [ins.InsIPush(ValueInt(10)),
                      ins.InsIPush(ValueInt(11)),
                      ins.InsIAdd(),
                      ins.InsIStore(ValueInt(0)),
                      ins.InsILoad(ValueInt(1)),
                      ins.InsIReturn()]


def test_whole():
    m = parser.parse_string(fixtures.load('parse_ok.code'))
    assert m
