
import os.path


def full_path(fname):
    dirpath = os.path.dirname(os.path.realpath(__file__))
    return os.path.join(dirpath, fname)


def load(fname):
    return open(full_path(fname)).read()