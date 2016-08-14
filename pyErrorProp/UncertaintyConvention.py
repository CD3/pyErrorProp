import decimal

import pint
from pint import UnitRegistry

from .ErrorPropagator import PositiveIntervalPropagator, nominal, uncertainty
from .CorrelationRegistry import CorrelationRegistry
from .util import *

UR = UnitRegistry()
EP = PositiveIntervalPropagator

class UncertaintyConvention(object):
  def __init__(self, _UR = UR, _EP = EP):
    self._UNITREGISTRY = _UR
    self._ERRORPROPAGATOR = _EP
    self.UncertainQuantity = build_uncertainquantity_class(self, self._UNITREGISTRY)
    self.ErrorPropagator = EP()

    self._CORRREGISTRY = CorrelationRegistry()

  @property
  def correlations(self):
    return self._CORRREGISTRY

  def z(self,a,b):
    try:
      return ( nominal(a) - nominal(b) ) / (uncertainty(a)**2 + uncertainty(b)**2)**0.5
    except:
      return 1e10

  def __propagate_error__(self, f, args, kwargs = {}):
    '''Propagates error through a function.'''
    # assume we are calculating z = f(x,y,...)
    zbar,dzs= self.ErrorPropagator.__propagate_uncertainties__( f, *args, **kwargs )

    # dzs is a dict of the uncertainty contributions from args and kwargs.
    # it will be more convienient to have a list of quantities paired with their uncertainty...
    dzs = [ ( dzs[k], kwargs[k] if k in kwargs else args[k] ) for k in dzs ]

    creg = self._CORRREGISTRY

    # calculate the total uncertainty
    dz = 0
    for dzx,x in dzs:
      for dzy,y in dzs:
        dz += creg.correlation(x,y) * dzx * dzy
    dz = dz**0.5

    z = self.UncertainQuantity(zbar,dz)

    # set correlations for the result
    # the result may be correlated to each of the inputs, but
    # may also be correlated to all of the quantities that the inputs are correlated to.

    for dzx,x in dzs:
      r = 0.0
      for dzy,y in dzs:
        try:
          r += (dzy / dz) * creg.correlation( x, y )
        except ZeroDivisionError:
          # if dz is zero, then z is not correlated to anything
          break
      creg.correlated( z, x, r )

      for v in creg.dependencies(x):
        r = 0.0
        for dzy,y in dzs:
          try:
            r += (dzy / dz) * creg.correlation( v, y )
          except ZeroDivisionError:
            # if dz is zero, then z is not correlated to anything
            break
        creg.correlated( z, v, r )

    return z

  def __round__( self, uq ):
    '''Round an uncertain quantity based on the following conventions
       1. Normally, uncertainty should be rounded to one significant figure.
       2. If the uncertainty's first significant figure is 1, it should be rounded to two significant figures.
       3. The nominal value should be rounded to the same decimal position as the uncertainty.
    '''
    return uq

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

  def consistent( self, a, b ):
    z = abs( self.z(a,b) )
    return z <= 2

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
      return self.__propagate_error__( func, args, kwargs )

    return wrapper

  def WithAutoError(self,sigfigs=3):
    '''Automatically calculate uncertainty in a function return value assuming all arguments are uncertain
       to a given significant figure.
       
       CORRELATIONS ARE IGNORED.'''

    def Decorator(func):

      def wrapper(*args,**kwargs):
        propagator = AutoErrorPropagator(self,sigfigs)
        zbar,dzs = propagator.__propagate_uncertainties__(func,*args,**kwargs)
        dzs = [ ( dzs[k], kwargs[k] if k in kwargs else args[k] ) for k in dzs ]
        creg = self._CORRREGISTRY

        # calculate the total uncertainty
        dz = 0
        for dzx,x in dzs:
          for dzy,y in dzs:
            dz += creg.correlation(x,y) * dzx * dzy
        dz = dz**0.5

        z = self.UncertainQuantity(zbar,dz)

        return z



      return wrapper 

    return Decorator




  def make_sigfig_UQ( self, nom, sigfigs ):
    '''Create and return uncertain quantity from a quantity and number of sigfigs. The
    uncertain quantity will have an error that corresponds to the last
    significant figure plus or minus 1.'''
    nom = nominal( nom )
    # round to correct number of sigfigs
    val = sigfig_round( nom, sigfigs )
    # get sigfig decimal postion
    pos = get_sigfig_decimal_pos( magof(nom), sigfigs )
    # the uncertainty is the last significant figure plus-or-minus 1
    unc = self.UncertainQuantity.Quantity(pow(10,-pos),unitsof(nom))

    return self.UncertainQuantity(val, unc)


class AutoErrorPropagator( PositiveIntervalPropagator ):
  '''An error propagator that automatically propagates error based on a given number of significant figures. For example,
     by default the propagator determines the uncertainy in the result by assuming all input parameters
     have 3 significant figures and the last significant figure is uncertain by plus/minus 1.'''
  def __init__(self, uconv, sigfigs = 3, *args, **kargs):
    self.uconv = uconv
    self.sigfigs = sigfigs
    super( AutoErrorPropagator, self ).__init__( *args, **kargs )

  def __propagate_uncertainties__(self, func, *args, **kargs):
    new_args = []
    for i,a in enumerate(args):
      if not a.__class__.__name__ == 'UncertainQuantity':
        a = self.uconv.make_sigfig_UQ( a, self.sigfigs )
      new_args.append( a )

    new_kargs = dict()
    for k,v in kargs.items():
      if not v.__class__.__name__ == 'UncertainQuantity':
        v = self.uconv.make_sigfig_UQ( v, self.sigfigs )
      new_kargs[k] = v

    value,uncertainties = super( AutoErrorPropagator, self).__propagate_uncertainties__( func, *new_args, **new_kargs )

    return value, uncertainties








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
