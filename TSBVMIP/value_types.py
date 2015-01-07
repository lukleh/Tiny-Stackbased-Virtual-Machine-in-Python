# -*- coding: utf-8  -*-


class Type():

    def __init__(self, sort):
        self.sort = sort

    def __str__(self):
        return "Type %s" % self.sort

    def equals(self, value):
        if self == value:
            return True
        elif self.sort is None:
            return value.sort is None
        else:
            return False

VOID = Type(0)
NULL = Type(1)
INT = Type(2)
FLOAT = Type(3)
ARRAY = Type(4)
INT_ARRAY = Type(5)
FLOAT_ARRAY = Type(6)
