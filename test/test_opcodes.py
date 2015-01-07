# -*- coding: utf-8  -*-

from TSBVMIP import opcodes
from TSBVMIP import instructions


def test_completness():
    done = set()
    for _, v in instructions.keywords.items():
        assert v not in done
        done.add(v.opcode)
    assert len(done) == opcodes.TOTAL + 1
