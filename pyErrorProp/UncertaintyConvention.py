import decimal

import pint
from pint import UnitRegistry

from ErrorPropagator import PositiveIntervalPropagator, nominal, uncertainty

UR = UnitRegistry()
EP = PositiveIntervalPropagator

class UncertaintyConvention(object):

  def __init__(self, _UR = UR, _EP = EP):
    self._UNITREGISTRY = _UR
    self._ERRORPROPAGATOR = _EP
    self.UncertainQuantity = build_uncertainquantity_class(self, self._UNITREGISTRY)
    self.ErrorPropagator = EP()

  def z(self,a,b):
    z =  ( nominal(a) - nominal(b) ) / ( uncertainty(a)**2 + uncertainty(b)**2)**0.5
    return z

  def __propagate_error__(self, f, args, kwargs = {}):
    '''Propagates error through a function.'''
    self.ErrorPropagator.return_all_uncertainties = True

    nom,unc,uncs = self.ErrorPropagator.propagate_uncertainties( f, *args, **kwargs )

    y = self.UncertainQuantity(nom,unc)
    # set correlations between inputs and result
    for k in uncs:
      x = kwargs.get( k, args[k] )
      y.correlated( x, 1.0 if uncs[k].magnitude > 0 else -1.0 )


    return y

  def __round__( self, uq ):
    '''Round an uncertain quantity based on the following conventions
       1. Normally, uncertainty should be rounded to one significant figure.
       2. If the uncertainty's first significant figure is 1, it should be rounded to two significant figures.
       3. The nominal value should be rounded to the same decimal position as the uncertainty.
    '''
    return uq

  def __eq__( self, a, b ):
    '''Compare two uncertain quantities.'''
    # calculate z-value.
    z = abs(self.z(a,b))
    return z <= 2

  def __lt__( self, a, b ):
    '''Check that a is less than b.'''
    # calculate z-value.
    z = self.z(a,b)
    return z < -2

  def __gt__( self, a, b ):
    '''Check that a is less than b.'''
    # calculate z-value.
    z = self.z(a,b)
    return z > 2

  def calc_UncertainQuantity( self, data, round = False ):
    '''Computes an uncertain quantity from a data set (computes the standard error)'''
    nominal = sum( data ) / len(data)
    std_dev = ( sum( [ (x - nominal)**2 for x in data ] ) / len(data) )**0.5 # Note: using the 'biased' estimate
    std_err = std_dev /len( data )**0.5

    q = self.UncertainQuantity( nominal, std_err )
    if round:
      q = self.round( q )

    return q

  calc_UQ = calc_UncertainQuantity

  def WithError(self,func):
    def wrapper(*args,**kwargs):
      return self.UncertainQuantity( *self.ErrorPropagator.propagate_uncertainties( func, *args, **kwargs ) )

    return wrapper










def build_uncertainquantity_class(conv, ureg):
  from .UncertainQuantity import _UncertainQuantity

  class UncertainQuantity(_UncertainQuantity):
      pass

  UncertainQuantity._CONVENTION = conv
  UncertainQuantity.Quantity    = ureg.Quantity

  ureg.define('percent = 0.01 * radian = perc = %')

  # we need to modify the quantity magic functions to return NotImplemented if
  # the other type is an uncertain quantity so that the UncertainQuantity __r* methods can take over.
  UQ_ = UncertainQuantity
  def disable_for_UQ(f):
    def new_f(self,other):
      if type(other) is UQ_:
        return NotImplemented
      return f(self, other)

    return new_f

  UncertainQuantity.Quantity.__add__ = disable_for_UQ( UncertainQuantity.Quantity.__add__ )
  UncertainQuantity.Quantity.__sub__ = disable_for_UQ( UncertainQuantity.Quantity.__sub__ )
  UncertainQuantity.Quantity.__mul__ = disable_for_UQ( UncertainQuantity.Quantity.__mul__ )
  UncertainQuantity.Quantity.__div__ = disable_for_UQ( UncertainQuantity.Quantity.__div__ )


  # add auto support for Decimal type to quantity
  def wrap(f):
    def new_f(cls,value,units=None):
      if isinstance(value,(str,unicode)):
        try:
          value = decimal.Decimal(value)
        except:
          pass
      return f(cls,value,units)

    return new_f

  UncertainQuantity.Quantity.__new__ = staticmethod(wrap( UncertainQuantity.Quantity.__new__ ))


  
  return UncertainQuantity
