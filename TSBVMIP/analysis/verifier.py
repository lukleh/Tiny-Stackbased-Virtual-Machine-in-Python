# -*- coding: utf8 -*-

from ..instructions import InsReturn, InsGoto, InsBranch
from .. import opcodes
from ..exceptions import VerifyException
from .frame import Frame
from .controlflow import ControlFlowAnalyzer


class Verifier():

    def __init__(self, interpreter):
        self.interpreter = interpreter
        self.changed = None
        self.frames = None
        self.queue = []
        self.method = None

    def verify(self, method):
        self.verify_jump_points(method)
        self.verify_load_store_vars(method)
        self.verify_return(method)
        self.verify_values(method)
        return True

    def verify_jump_points(self, method):
        for i, inst in enumerate(method.code):
            if inst.opcode == opcodes.GOTO or isinstance(inst, InsBranch):
                if inst.argument.value < 0 or inst.argument.value >= len(method.code):
                    raise VerifyException('instruction %s jump target %s outside boundary <0, %s>' %
                                          (inst, inst.argument.value, len(method.code) - 1))
        return True

    def verify_load_store_vars(self, method):
        for inst in method.code:
            if inst.opcode in [opcodes.ISTORE, opcodes.FSTORE, opcodes.ASTORE]:
                pos = inst.argument.value
                lv = method.variables[pos]
                vt = self.interpreter.new_value(lv.vtype)
                self.interpreter.copy_operation(inst, vt)
        return True

    def verify_return(self, method):
        cfa = ControlFlowAnalyzer()
        bbs = cfa.analyze(method)
        for bb in bbs:
            end_ins = method.code[bb.end_inst_index]
            if not bb.sucessors and not isinstance(end_ins, InsReturn):
                raise VerifyException('leaf basic block does not end with return instruction, but wirh %s' % end_ins)
        return True

    def verify_values(self, method):
        self.method = method
        self.changed = [False for _ in method.code]
        self.frames = [None for _ in method.code]

        current = Frame()
        current.set_return(self.interpreter.new_value(method.return_type.vtype))

        for i, v in enumerate(method.variables):
            if i < method.argument_count:
                current.add_local(self.interpreter.new_value(v.vtype))
            else:
                current.add_local(self.interpreter.new_value(None))
            current.add_local_type(self.interpreter.new_value(v.vtype))

        self.merge(0, current)

        while self.queue:
            ins_int = self.queue.pop()
            ins = method.code[ins_int]
            frame = self.frames[ins_int]
            self.changed[ins_int] = False

            current = frame.copy()
            current.execute(ins, self.interpreter)
            if not isinstance(ins, InsReturn) and not isinstance(ins, InsGoto):
                self.merge(ins_int + 1, current)

            if isinstance(ins, InsGoto) or isinstance(ins, InsBranch):
                self.merge(ins.argument.value, current)

        return True

    def merge(self, i, frame):
        old_frame = self.frames[i]
        changes = False

        if old_frame is None:
            self.frames[i] = frame.copy()
            changes = True
        else:
            changes = old_frame.merge(frame, self.interpreter)

        if changes and not self.changed[i]:
            self.changed[i] = True
            self.queue.append(i)
