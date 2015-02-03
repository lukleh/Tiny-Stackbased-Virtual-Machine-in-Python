# -*- coding: utf8 -*-


class Method():

    def __init__(self, _code=None, _variables=None, _argument_count=0, _return_type=None):
        if not _variables:
            _variables = []
        if not _code:
            _code = []
        self.code = _code
        self.variables = _variables
        self.argument_count = _argument_count
        self.return_type = _return_type
        self.function_name = None
        self.labels = {}
