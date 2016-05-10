from weakref import WeakKeyDictionary
from .CorrelationMatrix import CorrelationMatrix
from .util import isuncertain
wdict = WeakKeyDictionary

class CorrelationRegistry(object):

  def __init__(self):
    self._correlations = wdict()

  def keys(self):
    ks = self._correlations.keys()
    for k in self._correlations.keys():
      ks.append( self._correlations[k] )

    return ks


  def correlated( self, x, y, r ):
    if not isuncertain(x) or not isuncertain(y):
      return

    a = x if id(x) < id(y) else y
    b = y if id(x) < id(y) else x

    if not a in self._correlations:
      self._correlations[a] = wdict()

    self._correlations[a][b] = r

  def correlation( self, x, y, default = 0 ):
    if x is y:
      return 1

    a = x if id(x) < id(y) else y
    b = y if id(x) < id(y) else x

    if not a in self._correlations:
      return default
    if not b in self._correlations[a]:
      return default

    return self._correlations[a][b]

