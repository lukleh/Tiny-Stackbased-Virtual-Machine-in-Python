# -*- coding: utf-8  -*-

from . import values
from .. import opcodes
from ..exceptions import VerifyException, ExpectedException
from .. import value_types


class InterpreterBase():

    def new_value(self, v):
        raise NotImplementedError()

    def new_operation(self, ins):
        raise NotImplementedError()

    def copy_operation(self, ins, v):
        raise NotImplementedError()

    def unary_operation(self, ins, v):
        raise NotImplementedError()

    def binary_operation(self, ins, v1, v2):
        raise NotImplementedError()

    def ternary_operation(self, ins, v1, v2, v3):
        raise NotImplementedError()

    def return_operation(self, ins, v, e):
        raise NotImplementedError()

    def merge(self, v1, v2):
        raise NotImplementedError()


class BasicInterpreter(InterpreterBase):

    def new_value(self, v):
        if v is None:
            return values.UNINITIALIZED_VALUE
        elif v == value_types.INT:
            return values.INT_VALUE
        elif v == value_types.FLOAT:
            return values.FLOAT_VALUE
        elif v == value_types.FLOAT_ARRAY:
            return values.FLOAT_ARRAY_REF
        elif v == value_types.INT_ARRAY:
            return values.INT_ARRAY_REF
        else:
            raise VerifyException('unknown new value %s' % v)

    def new_operation(self, ins):
        op = ins.opcode
        if op == opcodes.IPUSH:
            return values.INT_VALUE
        elif op == opcodes.FPUSH:
            return values.FLOAT_VALUE
        else:
            VerifyException('opcode %s not allowed in interpreter new operation' % op)

    def copy_operation(self, ins, v):
        return v

    def unary_operation(self, ins, value):
        op = ins.opcode
        if op == opcodes.IRETURN or op == opcodes.F2I or op == opcodes.ARRAYLENGTH:
            return values.INT_VALUE
        elif op == opcodes.FRETURN or op == opcodes.I2F:
            return values.FLOAT_VALUE
        elif op == opcodes.ARETURN:
            return values.ARRAY_REF
        elif op == opcodes.NEWARRAY:
            if ins.argument.value == 0:
                return values.INT_ARRAY_REF
            elif ins.argument.value == 1:
                return values.FLOAT_ARRAY_REF
            else:
                raise VerifyException('prohibited array type %s' % ins.argument.value)
        elif op in [opcodes.IFNULL, opcodes.IFNONNULL]:
            return None
        else:
            raise VerifyException('opcode %s not allowed in interpreter unary operation' % op)

    def binary_operation(self, ins, value1, value2):
        op = ins.opcode
        if opcodes.IADD <= op <= opcodes.IDIV or op == opcodes.IALOAD:
            return values.INT_VALUE
        elif opcodes.FADD <= op <= opcodes.FDIV or op == opcodes.FALOAD:
            return values.FLOAT_VALUE
        elif opcodes.IF_ICMPEQ <= op <= opcodes.IF_FCMPLT:
            return None
        else:
            raise VerifyException('opcode %s not allowed in interpreter binary operation' % op)

    def ternary_operation(self, ins, v1, v2, v3):
        return None

    def return_operation(self, ins, v, e):
        pass

    def merge(self, v1, v2):
        if not v1.equals(v2):
            return values.UNINITIALIZED_VALUE
        return v1


class BasicVerifier(BasicInterpreter):

    def copy_operation(self, ins, value):
        expected = None
        op = ins.opcode
        if op == opcodes.ILOAD or op == opcodes.ISTORE:
            expected = values.INT_VALUE
        elif op == opcodes.FLOAD or op == opcodes.FSTORE:
            expected = values.FLOAT_VALUE
        elif op == opcodes.ALOAD or op == opcodes.ASTORE:
            if not value.is_array_reference:
                raise ExpectedException('expected %s received %s' % (value_types.ARRAY, value))
            return super().copy_operation(ins, value)
        elif op in [opcodes.DUP, opcodes.SWAP]:
            return value
        else:
            raise VerifyException('opcode %s not allowed in interpreter copy operation' % op)
        if not expected.equals(value):
            raise ExpectedException('expected %s received %s' % (expected, value))
        return super().copy_operation(ins, value)

    def unary_operation(self, ins, value):
        expected = None
        op = ins.opcode
        if op == opcodes.IRETURN or op == opcodes.I2F or op == opcodes.NEWARRAY:
            expected = values.INT_VALUE
        elif op == opcodes.FRETURN or op == opcodes.F2I:
            expected = values.FLOAT_VALUE
        elif op in [opcodes.ARETURN, opcodes.ARRAYLENGTH, opcodes.IFNULL, opcodes.IFNONNULL]:
            if not value.is_array_reference:
                raise ExpectedException('expected %s received %s' % (value_types.ARRAY, value))
            return super().unary_operation(ins, value)
        else:
            raise VerifyException('opcode %s not allowed in interpreter unary operation' % op)
        if not expected.equals(value):
            raise ExpectedException('expected %s received %s' % (expected, value))

        return super().unary_operation(ins, value)

    def binary_operation(self, ins, value1, value2):
        expected1 = None
        expected2 = None
        op = ins.opcode
        if opcodes.IADD <= op <= opcodes.IDIV or opcodes.IF_ICMPEQ <= op <= opcodes.IF_ICMPLT:
            expected1 = values.INT_VALUE
            expected2 = values.INT_VALUE
        elif opcodes.FADD <= op <= opcodes.FDIV or opcodes.IF_FCMPEQ <= op <= opcodes.IF_FCMPLT:
            expected1 = values.FLOAT_VALUE
            expected2 = values.FLOAT_VALUE
        elif op == opcodes.IALOAD:
            expected1 = values.INT_ARRAY_REF
            expected2 = values.INT_VALUE
        elif op == opcodes.FALOAD:
            expected1 = values.FLOAT_ARRAY_REF
            expected2 = values.INT_VALUE
        else:
            raise VerifyException('opcode %s not allowed in interpreter binary operation' % op)
        if not expected1.equals(value1):
            raise ExpectedException('expected %s received %s' % (expected1, value1))
        if not expected2.equals(value2):
            raise ExpectedException('expected %s received %s' % (expected2, value2))

        return super().binary_operation(ins, value1, value2)

    def ternary_operation(self, ins, value1, value2, value3):
        expected1 = None
        expected3 = None
        op = ins.opcode
        if op == opcodes.IASTORE:
            expected1 = values.INT_ARRAY_REF
            expected3 = values.INT_VALUE
        elif op == opcodes.FASTORE:
            expected1 = values.FLOAT_ARRAY_REF
            expected3 = values.FLOAT_VALUE
        else:
            raise VerifyException('opcode %s not allowed in interpreter ternary operation' % op)
        if not expected1.equals(value1):
            raise ExpectedException('expected %s received %s' % (expected1, value1))
        if not values.INT_VALUE.equals(value2):
            raise ExpectedException('expected %s received %s' % (values.INT_VALUE, value2))
        if not expected3.equals(value3):
            raise ExpectedException('expected %s received %s' % (expected3, value3))

    def return_operation(self, ins, value, expected):
        if value.is_array_reference:
            if not value.is_sub_type(expected):
                raise ExpectedException('%s is not subtype of %s' % (value, expected))
        elif not value.equals(expected):
            raise ExpectedException('expected %s received %s' % (expected, value))
