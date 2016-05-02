import array

class CorrelationMatrix(object):
  '''A simple class that represents a correlation matrix. The class just wraps array.array and provides some useful
     methods for setting up and accessing the matrix elements.'''

  def __init__(self, quantities = None ):
    self._matrix = None
    self._N = 0
    if not quantities is None:
      self.create_matrix( quantities )


  def create_matrix( self, quantities ):
    '''Creates the correlation matrix from a list of quantities.'''
    self._N = len(quantities)
    self._matrix = array.array('d', [0]*(self._N*self._N))

    for i in range(self._N):
      for j in range(self._N):
        self.set(i, j, quantities[i].correlated(quantities[j], return_None=False) )


  def set(self,i,j,v=0.0):
    k = i*self._N + j
    if k >= len(self._matrix):
      raise IndexError( 'Element (%d,%d) is not in range.' % (i,j) )
    self._matrix[k] = v

  def get(self,i,j,v=0.0):
    k = i*self._N + j
    if k >= len(self._matrix):
      raise IndexError( 'Element (%d,%d) is not in range.' % (i,j) )
    return self._matrix[k]

  def __str__(self):
    s = ""
    for i in range(self._N):
      for j in range(self._N):
        s += str( self.get(i,j) )
        s += ' '
      s += '\n'
    return s
