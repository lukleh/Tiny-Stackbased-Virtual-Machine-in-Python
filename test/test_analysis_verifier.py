# -*- coding: utf-8  -*-

import copy

import pytest

from TSBVMIP import code_parser as parser
from TSBVMIP import instructions
from TSBVMIP import value_containers
from TSBVMIP.exceptions import VerifyException
from TSBVMIP.analysis.verifier import Verifier
from TSBVMIP.analysis.interpreter import BasicVerifier
import fixtures


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


def test_verify_jump_points():
    cc = copy.deepcopy(clean_code)
    cc['ins'] = [{'label': 'x'}, {'ipush': 1}, 'ireturn']
    method = parser.process_yaml(cc)
    method.code.append(instructions.InsGoto(value_containers.ValueInt(-1)))
    pytest.raises(VerifyException, Verifier(BasicVerifier()).verify_jump_points, method)
    method.code[2] = instructions.InsGoto(value_containers.ValueInt(3))
    pytest.raises(VerifyException, Verifier(BasicVerifier()).verify_jump_points, method)
    method.code[2] = instructions.InsGoto(value_containers.ValueInt(0))
    assert Verifier(BasicVerifier()).verify_jump_points(method)


def test_verify_load_store():
    cc = copy.deepcopy(clean_code)
    cc['ins'] = [{'label': 'x'}, {'ipush': 1}, 'ireturn']
    method = parser.process_yaml(cc)
    method.code.insert(1, instructions.InsIStore(value_containers.ValueInt(1)))
    pytest.raises(VerifyException, Verifier(BasicVerifier()).verify_load_store_vars, method)
    method.code[1] = instructions.InsAStore(value_containers.ValueInt(1))
    pytest.raises(VerifyException, Verifier(BasicVerifier()).verify_load_store_vars, method)
    method.code[1] = instructions.InsFStore(value_containers.ValueInt(1))
    assert Verifier(BasicVerifier()).verify_load_store_vars(method)


def test_verify_return():
    cc = copy.deepcopy(clean_code)
    cc['ins'] = [{'ipush': 1}, {'ipush': 2}]
    method = parser.process_yaml(cc)
    pytest.raises(VerifyException, Verifier(BasicVerifier()).verify_return, method)
    cc['ins'] = [{'ipush': 1}, 'ireturn']
    method = parser.process_yaml(cc)
    assert Verifier(BasicVerifier()).verify_return(method)
    cc['ins'] = [{'if_icmpeq': 'done'}, {'ipush': 2}, {'label': 'done'}, 'ireturn']
    method = parser.process_yaml(cc)
    assert Verifier(BasicVerifier()).verify_return(method)


def test_verify_values():
    code = parser.parse_file(fixtures.full_path('bubblesort_verify_bad_stack_height.yaml'))
    assert pytest.raises(VerifyException, Verifier(BasicVerifier()).verify_values, code)
