""" String utilities. """

import typing as t


class sequence:
    def __init__(self, seq: str, tail_seq: str=None):
        self.seq          = seq
        self.n            = len(self.seq)
        self.tail_seq     = tail_seq
        self.tail_seq_idx = 0

    def __getitem__(self, key):
        """ overload [] operator to allow for dynamic increasing. """
        if isinstance(key, slice):
            ret_seq = ''
            if key.stop >= self.n:
                ret_seq = (self.seq * (int(key.stop/self.n) + 1))[:key.stop]
            else:
                ret_seq = self.seq[:key.stop]

            if self.tail_seq:
                ret_seq = ret_seq[:-1] + self.tail_seq[self.tail_seq_idx]
                _n = len(self.tail_seq)
                _i = self.tail_seq_idx
                self.tail_seq_idx = (_i+1 + _n) % _n

            return ret_seq
        else:
            return self.seq[(key + self.n) % self.n]
