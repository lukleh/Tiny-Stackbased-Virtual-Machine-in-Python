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
        self.code = None

    def verify(self, code):
        self.verify_jump_points(code)
        self.verify_load_store_vars(code)
        self.verify_return(code)
        self.verify_values(code)
        return True

    def verify_jump_points(self, code):
        for i, inst in enumerate(code.instructions):
            if inst.opcode == opcodes.GOTO or isinstance(inst, InsBranch):
                if inst.argument.value < 0 or inst.argument.value >= code.ins_count:
                    raise VerifyException('instruction %s jump target %s outside boundary <0, %s>' % (inst, inst.argument.value, code.ins_count - 1))
        return True

    def verify_load_store_vars(self, code):
        for inst in code.instructions:
            if inst.opcode in [opcodes.ISTORE, opcodes.FSTORE, opcodes.ASTORE]:
                pos = inst.argument.value
                lv = code.get_var(pos)
                vt = self.interpreter.new_value(lv.vtype)
                self.interpreter.copy_operation(inst, vt)
        return True

    def verify_return(self, code):
        cfa = ControlFlowAnalyzer()
        bbs = cfa.analyze(code)
        for bb in bbs:
            end_ins = code.instructions[bb.end_inst_index]
            if not bb.sucessors and not isinstance(end_ins, InsReturn):
                raise VerifyException('leaf basic block does not end with return instruction, but wirh %s' % end_ins)
        return True

    def verify_values(self, code):
        self.code = code
        self.changed = [False for _ in code.instructions]
        self.frames = [None for _ in code.instructions]

        current = Frame()
        current.set_return(self.interpreter.new_value(code.return_type.vtype))
        for arg in code.arguments:
            current.add_local(self.interpreter.new_value(arg.vtype))
        for _ in code.local_variables:
            current.add_local(self.interpreter.new_value(None))
        for v in code.variables:
            current.add_local_type(self.interpreter.new_value(v.vtype))

        self.merge(0, current)

        while self.queue:
            ins_int = self.queue.pop()
            ins = code.instructions[ins_int]
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
