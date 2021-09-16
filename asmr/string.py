""" String utilities. """

import typing as t


class sequence:
    def __init__(self, seq: t.List[str]):
        self.seq = seq
        self.n = len(self.seq)

    def __getitem__(self, key):
        """ overload [] operator to allow for dynamic increasing. """
        if isinstance(key, slice):
            if key.stop >= self.n:
                return (self.seq * (int(key.stop/self.n) + 1))[:key.stop]
            else:
                return self.seq[:key.stop]
        else:
            return self.seq[(key + self.n) % self.n]
