# -*- coding: utf-8  -*-

from .. import value_types


class BasicValue():

    def __init__(self, type):
        self.type = type

    def __str__(self):
        return "BasicValue %s" % self.type

    def __repr__(self):
        return self.__str__()

    def equals(self, value):
        if self == value:
            return True
        elif self.type is None:
            return value.type is None
        else:
            return self.type.equals(value.type)

    @property
    def is_array_reference(self):
        return self.type is not None and self.type.sort >= value_types.ARRAY.sort

    def is_sub_type(self, other):
        return other.is_array_reference and self.type.sort >= other.type.sort


UNINITIALIZED_VALUE = BasicValue(None)
INT_VALUE = BasicValue(value_types.INT)
FLOAT_VALUE = BasicValue(value_types.FLOAT)
ARRAY_REF = BasicValue(value_types.ARRAY)
INT_ARRAY_REF = BasicValue(value_types.INT_ARRAY)
FLOAT_ARRAY_REF = BasicValue(value_types.FLOAT_ARRAY)
