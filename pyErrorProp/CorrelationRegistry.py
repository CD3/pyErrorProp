import array
from weakref import WeakKeyDictionary
from .util import isuncertain
wdict = WeakKeyDictionary

class CorrelationRegistry(object):
  '''A registry that stores correlation coefficients between uncertain quantities. Coefficients
  are stored in a WeakKeyDictionary that is keyed using object instances. This allows the objects
  to be garbage collected and their entries will be automatically removed from the registry.
  '''

  def __init__(self):
    self._correlations = wdict()


  def correlated( self, x, y, r ):

    try:
      if not isuncertain(x) or not isuncertain(y):
        return

      if not x in self._correlations:
        self._correlations[x] = wdict()

      if not y in self._correlations:
        self._correlations[y] = wdict()

      self._correlations[x][y] = r
      self._correlations[y][x] = r
    except TypeError:
      pass

  def correlation( self, x, y, default = 0 ):
    try:
      if x is y:
        return 1

      if not x in self._correlations:
        return default

      if not y in self._correlations[x]:
        return default

      return self._correlations[x][y]
    except TypeError:
      return default
  
  def dependencies( self, x, default = [] ):
    try:
      if not x in self._correlations:
        return default

      return list(self._correlations[x].keys())
    except TypeError:
      return default

  def matrix( self, *args ):
    '''Return a correlation matrix for a set of arguments.'''

    mat = self.Matrix( len(args) )
    for i in range(mat._N):
      for j in range(mat._N):
        mat.set(i,j,self.correlation(args[i],args[j]))

    return mat


  class Matrix(object):

    def __init__(self,N):
      self._N = N
      self._components = array.array('d', [0]*(self._N*self._N))

    def __index__(self,i,j):
      '''Calculate the array index for a given entry.'''
      k = i*self._N + j

      if k >= len(self._components):
        raise IndexError( 'Element (%d,%d) is not in range.' % (i,j) )

      return k

    def set(self,i,j,v=0.0):
      k = self.__index__(i,j)
      self._components[k] = v

    def __call__(self,i,j):
      k = self.__index__(i,j)
      return self._components[k]

    def __str__(self):
      '''String representation of the matrix.'''
      s = ""
      for i in range(self._N):
        for j in range(self._N):
          s += str( self(i,j) )
          s += ' '
        s += '\n'
      return s




