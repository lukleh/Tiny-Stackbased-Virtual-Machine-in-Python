# -*- coding: utf-8  -*-

import itertools
from ..exceptions import VerifyException
from .. import opcodes


class Frame():

    def __init__(self):
        self.locals = []
        self.local_types = []
        self.stack = []
        self.return_value = None

    def __str__(self):
        return "L%sS%s" % (len(self.locals), self.stack_size)

    @property
    def values(self):
        for v in itertools.chain(self.locals, self.stack):
            yield v

    @property
    def stack_size(self):
        return len(self.stack)

    def pop(self):
        return self.stack.pop()

    def push(self, v):
        self.stack.append(v)

    def set_return(self, v):
        self.return_value = v

    def add_local(self, v):
        self.locals.append(v)

    def set_local(self, i, v):
        self.locals[i] = v

    def get_local(self, i):
        return self.locals[i]

    def add_local_type(self, t):
        self.local_types.append(t)

    def execute(self, insn, interpreter):
        op = insn.opcode
        if op in [opcodes.IPUSH, opcodes.FPUSH]:
            self.push(interpreter.new_operation(insn))
        elif op in [opcodes.ILOAD, opcodes.FLOAD, opcodes.ALOAD]:
            v = interpreter.copy_operation(insn, self.get_local(insn.argument.value))
            self.push(v)
        elif op in [opcodes.ISTORE, opcodes.FSTORE, opcodes.ASTORE]:
            value1 = interpreter.copy_operation(insn, self.pop())
            interpreter.return_operation(insn, value1, self.local_types[insn.argument.value])
            self.set_local(insn.argument.value, value1)
        elif op == opcodes.GOTO:
            pass
        elif op in [opcodes.IRETURN, opcodes.FRETURN, opcodes.ARETURN]:
            value1 = self.pop()
            interpreter.unary_operation(insn, value1)
            interpreter.return_operation(insn, value1, self.return_value)
        elif op == opcodes.NOP:
            pass
        elif op == opcodes.POP:
            self.pop()
        elif op == opcodes.DUP:
            value1 = self.pop()
            self.push(value1)
            self.push(interpreter.copy_operation(insn, value1))
        elif op == opcodes.SWAP:
            value2 = self.pop()
            value1 = self.pop()
            self.push(interpreter.copy_operation(insn, value2))
            self.push(interpreter.copy_operation(insn, value1))
        elif opcodes.IADD <= op <= opcodes.FDIV or \
                op in [opcodes.IALOAD, opcodes.FALOAD]:
            value2 = self.pop()
            value1 = self.pop()
            self.push(interpreter.binary_operation(insn, value1, value2))
        elif opcodes.IF_ICMPEQ <= op <= opcodes.IF_FCMPLT:
            value2 = self.pop()
            value1 = self.pop()
            interpreter.binary_operation(insn, value1, value2)
        elif op in [opcodes.F2I, opcodes.I2F, opcodes.NEWARRAY, opcodes.ARRAYLENGTH]:
            self.push(interpreter.unary_operation(insn, self.pop()))
        elif op in [opcodes.IFNONNULL, opcodes.IFNULL]:
            interpreter.unary_operation(insn, self.pop())
        elif op in [opcodes.IASTORE, opcodes.FASTORE]:
            value3 = self.pop()
            value2 = self.pop()
            value1 = self.pop()
            interpreter.ternary_operation(insn, value1, value2, value3)
        else:
            raise VerifyException('trying to execute unknown instruction %s' % insn)

    def merge(self, frame, interpreter):
        if self.stack_size != frame.stack_size:
            raise VerifyException('incompatible stack heights %s %s' % (self.stack_size, frame.stack_size))
        changes = False
        for i, (v1, v2) in enumerate(zip(self.values, frame.values)):
            v = interpreter.merge(v1, v2)
            if not v.equals(v1):
                if i < len(self.locals):
                    self.locals[i] = v
                else:
                    self.stack[i] = v
                changes = True
        return changes

    def copy(self):
        f = Frame()
        f.locals = list(self.locals)
        f.stack = list(self.stack)
        f.local_types = list(self.local_types)
        f.return_value = self.return_value
        return f
