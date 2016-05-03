import array
from .UncertainQuantity import _UncertainQuantity

class CorrelationMatrix(object):
  '''A simple class that represents a correlation matrix. Matrix elements are accessed with variable instances.'''

  def __init__(self, quantities = None ):
    self._matrix = None
    self._varmap  = None
    self._N = 0

    if not quantities is None:
      self.make( quantities )

    self._queue = None

  def __call__(self,i,j):
    return self.get(i,j,False)

  def queue( self, quantities ):
    '''Queue up a variable for building the correlation matrix.'''
    if self._queue is None:
      self._queue = list()

    if not isinstance(quantities,list):
      quantities = [quantities]

    for q in quantities:
      self._queue.append( q )
    

  def make( self, quantities = None ):
    '''Creates the correlation matrix from a list of quantities.'''

    if quantities is None:
      quantities = self._queue
      self._queue = None

    self._N = len(quantities)
    self._matrix = array.array('d', [0]*(self._N*self._N))
    self._varmap = dict()

    for i in range(self._N):
      self._varmap[ id(quantities[i]) ] = i
      for j in range(self._N):
        if i == j:
          c = 1
        elif isinstance( quantities[i], _UncertainQuantity ):
          c = quantities[i].correlated(quantities[j], return_None=False)
        else:
          c = 0
        self.set(i,j,c,map_indexes=False )

  def __index__(self,a,b,map_indexes=True):
    if map_indexes:
      ida = id(a)
      idb = id(b)
      if not ida in self._varmap:
        raise IndexError( 'Variable (%s) does not have entry in correlation matrix.' % a )
      if not idb in self._varmap:
        raise IndexError( 'Variable (%s) does not have entry in correlation matrix.' % b )

      i = self._varmap(id(ida))
      j = self._varmap(id(idb))
    else:
      i = a
      j = b

    k = i*self._N + j

    if k >= len(self._matrix):
      raise IndexError( 'Element (%d,%d) is not in range.' % (i,j) )

    return k

  def set(self,a,b,v=0.0,map_indexes=True):
    k = self.__index__(a,b,map_indexes)
    self._matrix[k] = v

  def get(self,a,b,map_indexes=True):
    k = self.__index__(a,b,map_indexes)
    return self._matrix[k]

  def __str__(self):
    s = ""
    for i in range(self._N):
      for j in range(self._N):
        s += str( self.get(i,j,False) )
        s += ' '
      s += '\n'
    return s
