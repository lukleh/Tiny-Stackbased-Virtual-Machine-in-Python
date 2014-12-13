# -*- coding: utf-8  -*-

import TSBVMIP.instructions as ins
import TSBVMIP.values as vals
from TSBVMIP.yparser import Code
from TSBVMIP.analysis import analyzer


def test_flow_instructions():
    # make sure no instruction fall through
    for name, i in ins.keywords.items():
        if issubclass(i, ins.InsJump):
            pass
        elif not issubclass(i, ins.InsReturn):
            pass
        elif issubclass(i, ins.InsReturn):
            pass
        else:
            assert False


def test_basic_block():
    c = Code(func={'name': 'n', 'args': []})
    c.instructions = [
        ins.InsIPush(vals.ValueInt(1)),
        ins.InsIReturn()
    ]
    anz = analyzer.Analyzer()
    anz.analyze_control(c)
    anz.control_graph.scan_basic_blocks()
    assert len(anz.control_graph.basic_blocks) == 1
    assert anz.control_graph.basic_blocks[0] == [0, 1]
    c.instructions = [
        ins.InsGoto(vals.ValueInt(1)),
        ins.InsGoto(vals.ValueInt(0)),
        ins.InsIReturn()
    ]
    anz = analyzer.Analyzer()
    anz.analyze_control(c)
    anz.control_graph.scan_basic_blocks()
    print(anz.control_graph.basic_blocks)
    assert len(anz.control_graph.basic_blocks) == 3
    assert anz.control_graph.basic_blocks == [[0], [1], [2]]