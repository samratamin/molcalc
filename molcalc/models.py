import gzip
import io

import numpy as np
import sqlalchemy as sa
from sqlalchemy import (
    Column,
    DateTime,
    Float,
    Integer,
    LargeBinary,
    String,
)

from molcalc.extensions import db


def compress(s):
    if isinstance(s, str):
        s = s.encode()
    b = gzip.compress(s)
    return b


def decompress(b):
    s = gzip.decompress(b)
    return s


class CompressedString(sa.types.TypeDecorator):
    """
    Storage datatype for large blobs of text
    """

    impl = LargeBinary

    def process_bind_param(self, value, dialect):
        return compress(value)

    def process_result_value(self, value, dialect):
        return decompress(value)


class NumpyArray(sa.types.TypeDecorator):
    """
    Storage datatype for numpy arrays
    """

    impl = LargeBinary

    def save_array(self, arr):
        s = io.StringIO()
        np.savetxt(s, arr)
        return s.getvalue()

    def load_array(self, txt):
        s = io.StringIO(txt)
        arr = np.loadtxt(s)
        return arr

    def process_bind_param(self, value, dialect):
        value = self.save_array(value)
        return compress(value)

    def process_result_value(self, value, dialect):
        value = decompress(value)
        value = self.load_array(value)
        return value


class GamessCalculation(db.Model):
    __tablename__ = "gamesscalculations"
    id = Column(Integer, primary_key=True)

    # Basic descriptors
    hashkey = Column(String)
    created = Column(DateTime)
    name = Column(String)
    smiles = Column(String)
    sdf = Column(String)
    mol2 = Column(String)
    svg = Column(String)
    coordinates = Column(String)

    # GAMESS Results
    enthalpy = Column(Float)
    charges = Column(String)

    islinear = Column(String)
    vibjsmol = Column(CompressedString)
    vibfreq = Column(String)
    vibintens = Column(String)
    thermo = Column(String)

    orbitals = Column(String)
    orbitalstxt = Column(CompressedString)

    soltotal = Column(Float)
    solpolar = Column(Float)
    solnonpolar = Column(Float)
    solsurface = Column(Float)
    soldipole = Column(String)
    soldipoletotal = Column(Float)

    def __repr__(self):
        fmt = "<GamessCalculation {:} {:} >"
        return fmt.format(self.smiles, self.hashkey)


class Counter(db.Model):
    __tablename__ = "molecules"
    smiles = Column(String, primary_key=True)
    count = Column(Integer)

    def __repr__(self):
        fmt = "<Molecule {:} {:} >"
        return fmt.format(self.smiles, self.count)
