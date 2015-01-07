# -*- coding: utf-8  -*-
import pytest

from TSBVMIP.analysis.frame import Frame
from TSBVMIP.analysis.interpreter import BasicInterpreter, BasicVerifier
from TSBVMIP.analysis.values import (UNINITIALIZED_VALUE,
                                     INT_VALUE,
                                     FLOAT_VALUE,
                                     ARRAY_REF,
                                     INT_ARRAY_REF,
                                     FLOAT_ARRAY_REF)
from TSBVMIP import instructions
from TSBVMIP import value_containers
from TSBVMIP import opcodes
from TSBVMIP import exceptions


def test_execute():
    for _, inst in instructions.keywords.items():
        for inter in [BasicInterpreter, BasicVerifier]:
            frame = Frame()
            frame.add_local(UNINITIALIZED_VALUE)
            if issubclass(inst, instructions.InsArgInteger):
                ins = inst(value_containers.ValueInt(0))
            elif issubclass(inst, instructions.InsArgFloat):
                ins = inst(value_containers.ValueFloat(0.0))
            else:
                ins = inst()

            # prepare frame state
            if inst.opcode == opcodes.ILOAD:
                frame.locals[0] = INT_VALUE
            elif inst.opcode == opcodes.FLOAD:
                frame.locals[0] = FLOAT_VALUE
            elif inst.opcode == opcodes.ISTORE:
                frame.add_local_type(INT_VALUE)
                frame.push(INT_VALUE)
            elif inst.opcode == opcodes.FSTORE:
                frame.add_local_type(FLOAT_VALUE)
                frame.push(FLOAT_VALUE)
            elif inst.opcode == opcodes.IRETURN:
                frame.push(INT_VALUE)
                frame.return_value = INT_VALUE
            elif inst.opcode == opcodes.FRETURN:
                frame.push(FLOAT_VALUE)
                frame.return_value = FLOAT_VALUE
            elif inst.opcode == opcodes.POP:
                frame.push(UNINITIALIZED_VALUE)
            elif inst.opcode == opcodes.DUP:
                frame.push(UNINITIALIZED_VALUE)
            elif inst.opcode == opcodes.SWAP:
                frame.push(INT_VALUE)
                frame.push(FLOAT_VALUE)
            elif opcodes.IF_ICMPEQ <= inst.opcode <= opcodes.IF_ICMPLT:
                frame.push(INT_VALUE)
                frame.push(INT_VALUE)
            elif opcodes.IF_FCMPEQ <= inst.opcode <= opcodes.IF_FCMPLT:
                frame.push(FLOAT_VALUE)
                frame.push(FLOAT_VALUE)
            elif inst.opcode == opcodes.IFNONNULL or inst.opcode == opcodes.IFNULL:
                frame.push(ARRAY_REF)
            elif opcodes.IADD <= inst.opcode <= opcodes.IDIV:
                frame.push(INT_VALUE)
                frame.push(INT_VALUE)
            elif opcodes.FADD <= inst.opcode <= opcodes.FDIV:
                frame.push(FLOAT_VALUE)
                frame.push(FLOAT_VALUE)
            elif inst.opcode == opcodes.F2I:
                frame.push(FLOAT_VALUE)
            elif inst.opcode == opcodes.I2F:
                frame.push(INT_VALUE)
            elif inst.opcode == opcodes.ALOAD:
                frame.locals[0] = ARRAY_REF
            elif inst.opcode == opcodes.ASTORE:
                frame.add_local_type(ARRAY_REF)
                frame.push(INT_ARRAY_REF)
            elif inst.opcode == opcodes.IASTORE:
                frame.push(INT_ARRAY_REF)
                frame.push(INT_VALUE)
                frame.push(INT_VALUE)
            elif inst.opcode == opcodes.IALOAD:
                frame.push(INT_ARRAY_REF)
                frame.push(INT_VALUE)
            elif inst.opcode == opcodes.FASTORE:
                frame.push(FLOAT_ARRAY_REF)
                frame.push(INT_VALUE)
                frame.push(FLOAT_VALUE)
            elif inst.opcode == opcodes.FALOAD:
                frame.push(FLOAT_ARRAY_REF)
                frame.push(INT_VALUE)
            elif inst.opcode == opcodes.ARETURN:
                frame.push(ARRAY_REF)
                frame.return_value = ARRAY_REF
            elif inst.opcode == opcodes.NEWARRAY:
                frame.push(INT_VALUE)
            elif inst.opcode == opcodes.ARRAYLENGTH:
                frame.push(ARRAY_REF)
            elif inst.opcode == opcodes.NOP:
                pass
            elif inst.opcode == opcodes.GOTO:
                pass
            elif inst.opcode == opcodes.IPUSH:
                pass
            elif inst.opcode == opcodes.FPUSH:
                pass
            else:
                assert False

            # execute instruction in frame using and interpreter
            frame.execute(ins, inter())

            # check frame state after execution
            if inst.opcode == opcodes.ILOAD:
                assert frame.pop() == INT_VALUE
            elif inst.opcode == opcodes.FLOAD:
                assert frame.pop() == FLOAT_VALUE
            elif inst.opcode == opcodes.ISTORE:
                assert frame.stack_size == 0
                assert frame.locals[0] == INT_VALUE
            elif inst.opcode == opcodes.FSTORE:
                assert frame.stack_size == 0
                assert frame.locals[0] == FLOAT_VALUE
            elif inst.opcode == opcodes.IRETURN:
                assert frame.stack_size == 0
                assert frame.return_value == INT_VALUE
            elif inst.opcode == opcodes.FRETURN:
                assert frame.stack_size == 0
                assert frame.return_value == FLOAT_VALUE
            elif inst.opcode == opcodes.POP:
                assert frame.stack_size == 0
            elif inst.opcode == opcodes.DUP:
                assert frame.pop() == UNINITIALIZED_VALUE
                assert frame.pop() == UNINITIALIZED_VALUE
            elif inst.opcode == opcodes.SWAP:
                assert frame.pop() == INT_VALUE
                assert frame.pop() == FLOAT_VALUE
            elif opcodes.IF_ICMPEQ <= inst.opcode <= opcodes.IF_ICMPLT or opcodes.IF_FCMPEQ <= inst.opcode <= opcodes.IF_FCMPLT:
                assert frame.stack_size == 0
            elif inst.opcode == opcodes.IFNONNULL or inst.opcode == opcodes.IFNULL:
                assert frame.stack_size == 0
            elif opcodes.IADD <= inst.opcode <= opcodes.IDIV:
                assert frame.pop() == INT_VALUE
            elif opcodes.FADD <= inst.opcode <= opcodes.FDIV:
                assert frame.pop() == FLOAT_VALUE
            elif inst.opcode == opcodes.F2I:
                assert frame.pop() == INT_VALUE
            elif inst.opcode == opcodes.I2F:
                assert frame.pop() == FLOAT_VALUE
            elif inst.opcode == opcodes.ALOAD:
                assert frame.pop() == ARRAY_REF
            elif inst.opcode == opcodes.ASTORE:
                assert frame.locals[0] == INT_ARRAY_REF
            elif inst.opcode == opcodes.IASTORE:
                assert frame.stack_size == 0
            elif inst.opcode == opcodes.IALOAD:
                assert frame.pop() == INT_VALUE
            elif inst.opcode == opcodes.FASTORE:
                assert frame.stack_size == 0
            elif inst.opcode == opcodes.FALOAD:
                assert frame.pop() == FLOAT_VALUE
            elif inst.opcode == opcodes.ARETURN:
                assert frame.stack_size == 0
            elif inst.opcode == opcodes.NEWARRAY:
                assert frame.pop() == INT_ARRAY_REF
            elif inst.opcode == opcodes.ARRAYLENGTH:
                assert frame.pop() == INT_VALUE
            elif inst.opcode == opcodes.NOP:
                pass
            elif inst.opcode == opcodes.GOTO:
                pass
            elif inst.opcode == opcodes.IPUSH:
                assert frame.pop() == INT_VALUE
            elif inst.opcode == opcodes.FPUSH:
                assert frame.pop() == FLOAT_VALUE
            else:
                assert False

            # stack has to be empty
            assert frame.stack_size == 0


def test_merge():
    interpreter = BasicVerifier()
    frame1 = Frame()
    frame1.push(INT_VALUE)
    frame1.push(FLOAT_VALUE)
    frame2 = Frame()
    frame2.push(INT_VALUE)
    # stack size must be the same, otherwise exception
    pytest.raises(exceptions.VerifyException, frame1.merge, frame2, interpreter)

    frame2.push(INT_VALUE)
    # frames not the equal, retrun True (change)
    assert frame1.merge(frame2, interpreter) is True
    # also, the difference gets nulled
    assert frame1.stack[-1] == UNINITIALIZED_VALUE

    frame1.pop()
    frame1.push(INT_VALUE)
    # frames the same, nothing is changing
    assert frame1.merge(frame2, interpreter) is False
    assert frame1.stack == frame2.stack

    # same for the local variables
    frame1.add_local(INT_VALUE)
    frame2.add_local(INT_VALUE)
    assert frame1.merge(frame2, interpreter) is False

    frame1.add_local(INT_VALUE)
    frame2.add_local(FLOAT_VALUE)
    assert frame1.merge(frame2, interpreter) is True
    assert frame1.locals[-1] == UNINITIALIZED_VALUE
