import array
from .UncertainQuantity import _UncertainQuantity

class CorrelationMatrix(object):
  '''A simple class that represents a correlation matrix
     where Matrix elements can be accessed with variable instances.

     There are 3 ways to create the matrix:

     1. Pass a list of quantities to the `make` method.
     2. Add quantities to the queue using the `queue` method, then call the 
        `make` method without arguments. The `make` method will then use the
        list of queued quantities to build the matrix.
     3. Pass a list of quantities to the constructor. These will just be passed
        to the `make` method.

     The correlation coefficients are stored in array of doubles and are
     directly accessed using an single array index. The array index is
     automatically computed from row and column indexes, so the data can
     be accessed like a matrix.

     A mapping of variables ids (from python's id() function) to row/column indexes
     is stored so that the correlation coefficients can be accessed with the
     actual variables themselves (this is actually the default behavior for the
     `get` method). When the correlation between two variables is requresed
     from the `get` method, the row and column indexes are first determined
     from the id of each variable, and these are then used to access the correlation
     coefficient from the matrix.
     '''

  def __init__(self, quantities = None ):
    self._matrix = None
    self._varmap  = None
    self._N = 0

    if not quantities is None:
      self.make( quantities )

    self._queue = None

  def __call__(self,i,j):
    '''Return an element of the correlation matrix.'''
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
    '''Creates the correlation matrix from a list of quantities.
       Currently, only correlation between UncertainQuantity instances
       is supported directly, but the matrix elements can be modified
       after the matrix has been created to support other uncertain types.'''

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
    '''Calculate the array index for a given entry. If map_indexes is True,
       the row and column indexes will be determined from the id of a and b.
       If map_indexes is False, a and b are treated as the row and column indexes.
       '''
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
    '''Set the correlation coefficient for a given pair of variables.'''
    k = self.__index__(a,b,map_indexes)
    self._matrix[k] = v

  def get(self,a,b,map_indexes=True):
    '''Get the correlation coefficient for a given pair of variables.'''
    k = self.__index__(a,b,map_indexes)
    return self._matrix[k]

  def __str__(self):
    '''String representation of the matrix.'''
    s = ""
    for i in range(self._N):
      for j in range(self._N):
        s += str( self.get(i,j,False) )
        s += ' '
      s += '\n'
    return s
