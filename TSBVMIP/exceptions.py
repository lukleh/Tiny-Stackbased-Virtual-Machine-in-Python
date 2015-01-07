# -*- coding: utf-8  -*-


class VirtualMachineException(Exception):
    pass


class ParserException(VirtualMachineException):
    pass


class ValueException(VirtualMachineException):
    pass


class VerifyException(VirtualMachineException):
    pass


class ExpectedException(VerifyException):
    pass


class RuntimeException(VirtualMachineException):
    pass


class InstructionException(RuntimeException):
    pass
