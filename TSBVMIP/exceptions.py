# -*- coding: utf-8  -*-


class ParserException(Exception):
    pass


class ValueException(Exception):
    pass


class RuntimeException(Exception):
    pass


class InstructionException(RuntimeException):
    pass