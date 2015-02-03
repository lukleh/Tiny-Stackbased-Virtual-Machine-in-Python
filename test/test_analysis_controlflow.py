# -*- coding: utf-8  -*-

import fixtures

from TSBVMIP import instructions
from TSBVMIP import value_containers
from TSBVMIP.code_parser import parse_string
from TSBVMIP.method import Method
from TSBVMIP.analysis import controlflow
from TSBVMIP.analysis.controlflow import BasicBlock


def test_flow_instructions():
    # make sure no instruction fall through
    for name, i in instructions.keywords.items():
        m = Method()
        anz = controlflow.ControlFlowAnalyzer()
        if issubclass(i, instructions.InsGoto):
            m.code.append(i(value_containers.ValueInt(3)))
            m.code.append(instructions.InsNop())
            m.code.append(instructions.InsNop())
            m.code.append(instructions.InsNop())
            anz.analyze(m)
            assert anz.basic_blocks == [BasicBlock(instruction_indexes=[0], sucessors=[None]),
                                        BasicBlock(instruction_indexes=[1, 2], sucessors=[None]),
                                        BasicBlock(instruction_indexes=[3], predecessors=[None, None])]
        elif issubclass(i, instructions.InsBranch):
            m.code.append(instructions.InsNop())
            m.code.append(i(value_containers.ValueInt(0)))
            anz.analyze(m)
            assert anz.basic_blocks == [BasicBlock(instruction_indexes=[0, 1], sucessors=[None], predecessors=[None])]
        elif not issubclass(i, instructions.InsReturn):
            if issubclass(i, instructions.InsNoArgument):
                m.code.append(i())
            elif issubclass(i, instructions.InsArgInteger):
                m.code.append(i(value_containers.ValueInt(1)))
            elif issubclass(i, instructions.InsArgFloat):
                m.code.append(i(value_containers.ValueFloat(5.0)))
            else:
                assert False
            anz.analyze(m)
            assert anz.basic_blocks == [BasicBlock(instruction_indexes=[0])]
        elif issubclass(i, instructions.InsReturn):
            m.code.append(i())
            anz.analyze(m)
            assert anz.basic_blocks == [BasicBlock(instruction_indexes=[0])]
        else:
            assert False


def test_basic_block_simple():
    m = Method()
    m.code = [
        instructions.InsIPush(value_containers.ValueInt(1)),
        instructions.InsIReturn()
    ]
    anz = controlflow.ControlFlowAnalyzer()
    anz.analyze(m)
    assert len(anz.basic_blocks) == 1
    assert anz.basic_blocks == [BasicBlock(instruction_indexes=[0, 1])]


def test_basic_block_complex():
    m = parse_string(fixtures.load('sum.code'))
    anz = controlflow.ControlFlowAnalyzer()
    anz.analyze(m)
    assert len(anz.basic_blocks) == 4
    assert [bb.instruction_indexes for bb in anz.basic_blocks] == [
        [0, 1, 2, 3], [4, 5, 6, 7, 8, 9], [10, 11, 12, 13, 14, 15], [16, 17]]

    m = parse_string(fixtures.load('bubblesort.code'))
    anz = controlflow.ControlFlowAnalyzer()
    anz.analyze(m)
    assert len(anz.basic_blocks) == 7
    assert [bb.instruction_indexes for bb in anz.basic_blocks] == [[0, 1, 2],
                                                                   [3, 4, 5, 6],
                                                                   [7, 8, 9, 10, 11, 12, 13],
                                                                   [14, 15, 16, 17, 18, 19, 20, 21, 22],
                                                                   [23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35,
                                                                    36, 37, 38, 39, 40, 41,
                                                                    42, 43],
                                                                   [44, 45, 46],
                                                                   [47, 48]]


def test_basic_block_oneblock():
    m = Method()
    anz = controlflow.ControlFlowAnalyzer()
    m.code.append(instructions.InsNop())
    m.code.append(instructions.InsNop())
    m.code.append(instructions.InsNop())
    anz.analyze(m)
    assert anz.basic_blocks == [BasicBlock(instruction_indexes=[0, 1, 2])]


def test_basic_block_onejumpback():
    m = Method()
    anz = controlflow.ControlFlowAnalyzer()
    m.code.append(instructions.InsNop())
    m.code.append(instructions.InsNop())
    m.code.append(instructions.InsNop())
    m.code.append(instructions.InsGoto(value_containers.ValueInt(0)))
    m.code.append(instructions.InsNop())
    anz.analyze(m)
    assert anz.basic_blocks == [BasicBlock(instruction_indexes=[0, 1, 2, 3], sucessors=[None], predecessors=[None]),
                                BasicBlock(instruction_indexes=[4])]


def test_basic_block_onejumpforward():
    m = Method()
    anz = controlflow.ControlFlowAnalyzer()
    m.code.append(instructions.InsGoto(value_containers.ValueInt(3)))
    m.code.append(instructions.InsNop())
    m.code.append(instructions.InsNop())
    m.code.append(instructions.InsNop())
    m.code.append(instructions.InsNop())
    anz.analyze(m)
    assert anz.basic_blocks == [BasicBlock(instruction_indexes=[0], sucessors=[None]),
                                BasicBlock(instruction_indexes=[1, 2], sucessors=[None]),
                                BasicBlock(instruction_indexes=[3, 4], predecessors=[None, None])]
