import decimal

import pint
from pint import UnitRegistry

from .ErrorPropagator import PositiveIntervalPropagator, nominal, uncertainty
from .CorrelationRegistry import CorrelationRegistry
from .util import *

from .unicode import *

from .decorator import decorate

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
    z = ( nominal(a) - nominal(b) ) / special_square_root(uncertainty(a)**2 + uncertainty(b)**2)
    try:
      return z.to("")
    except:
      return z

  def __propagate_errors__(self, f, args, kwargs = {}):
    '''Propagates error through a function.'''
    # assume we are calculating z = f(x,y,...)
    zbar,dzs= self.ErrorPropagator.__propagate_errors__( f, *args, **kwargs )

    # dzs is a dict of the uncertainty contributions from args and kwargs.
    # it will be more convienient to have a list of quantities paired with their uncertainty...
    dzs = [ ( dzs[k], kwargs[k] if k in kwargs else args[k] ) for k in dzs ]

    creg = self._CORRREGISTRY

    # calculate the total uncertainty
    dz = 0
    for dzx,x in dzs:
      for dzy,y in dzs:
        dz += creg.correlation(x,y) * dzx * dzy
    dz = special_square_root(dz)

    z = self.UncertainQuantity(zbar,dz)

    # set correlations for the result
    # the result may be correlated to each of the inputs, but
    # may also be correlated to all of the quantities that the inputs are correlated to.

    for dzx,x in dzs:
      r = 0.0
      for dzy,y in dzs:
        try:
          # WORKAROUND
          # always store correlations as float, even if inputs parameters
          # are decimal.Decimal.
          r += float(dzy / dz) * creg.correlation( x, y )
        except ZeroDivisionError:
          # if dz is zero, then z is not correlated to anything
          break
      creg.correlated( z, x, r )

      for v in creg.dependencies(x):
        r = 0.0
        for dzy,y in dzs:
          try:
            r += float(dzy / dz) * creg.correlation( v, y )
          except ZeroDivisionError:
            # if dz is zero, then z is not correlated to anything
            break
        creg.correlated( z, v, r )

    return z

  def __round__( self, uq, n = None ):
    '''Round an uncertain quantity based on the following conventions
       1. Normally, uncertainty should be rounded to one significant figure.
       2. If the uncertainty's first significant figure is 1, it should be rounded to two significant figures.
       3. The nominal value should be rounded to the same decimal position as the uncertainty.
    '''

    # we use the Decimal class to handle rounding correctly
    # we converting to a string first allows this to work with float and Decimal types
    # without losing precision 
    nom = decimal.Decimal(str(uq.nominal.magnitude))
    unc = decimal.Decimal(str(uq.error.magnitude))

    # if n was not given, then we round uncertainty to 1 sigfig.
    ndig = n
    if ndig is None:
      ndig = 1

    with decimal.localcontext() as ctx:
      # check if we should increase the number
      # of sigfigs from 1 to 2
      ctx.prec = 10
      if n is None and ndig == 1 and "{:+.10e}".format(unc)[1] == "1" :
          ndig += 1

    # get scientific notation string representation of the uncertainty
    with decimal.localcontext() as ctx:
      ctx.rounding = decimal.ROUND_HALF_UP
      unc_str = ("{:+.%de}"%(ndig-1)).format(unc)

    sign = 1 if unc_str[0] == '-' else 0
    digits = ()
    for d in unc_str.split('e')[0]:
      if d not in '.+-' :
        digits += (int(d),)

    exponent = int(unc_str.split('e')[1]) - len(digits) + 1


    # NOTE: exponent returned by as_tuple is for when all significant figures are to the *left* of the decimal point.
    # so, if we add/remove 1 significant figure (rather than set it to zero), we will need to decrease/increase
    # the exponent by 1.

    # if requested number of digits is greater than the number available, pad
    # with zeros.

    while len(digits) < ndig:
      exponent -= 1
      digits = digits + (0,)


    unc = decimal.Decimal( (sign, digits, exponent) )

    # now round nominal value to the same decimal position as the uncertainty.
    nom = nom.quantize(unc)


    # now create quantities for the nominal and uncertainty, making sure to use the same types for each magnitude that were used in uq.
    nom = uq.Quantity( type(uq.nominal.magnitude)(nom), uq.nominal.units )
    unc = uq.Quantity( type(uq.error.magnitude)(unc), uq.error.units )


    return uq.make( nom, unc )

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
    variance = ( sum( [ (x - nominal)**2 for x in data ] ) / (len(data)-1) ) # Note: using the 'unbiased' estimate
    std_dev = special_square_root(variance)
    std_err = std_dev / get_quantity_compatible_type(std_dev)(len( data )**0.5)

    q = self.UncertainQuantity( nominal, std_err )
    if round:
      q = self.__round__( q )

    return q

  calc_UQ = calc_UncertainQuantity

  def WithError(self,func):

    def wrapper(f,*args,**kwargs):
      return self.__propagate_errors__( f, args, kwargs )

    return decorate(func,wrapper)

  def WithAutoError(self,sigfigs=3):
    '''Automatically calculate uncertainty in a function return value assuming all arguments are uncertain
       to a given significant figure.
       
       CORRELATIONS ARE IGNORED.'''

    def Decorator(func):

      def wrapper(f,*args,**kwargs):
        propagator = AutoErrorPropagator(self,sigfigs)
        zbar,dzs = propagator.__propagate_errors__(f,*args,**kwargs)
        dzs = [ ( dzs[k], kwargs[k] if k in kwargs else args[k] ) for k in dzs ]
        creg = self._CORRREGISTRY

        # calculate the total uncertainty
        dz = 0
        for dzx,x in dzs:
          for dzy,y in dzs:
            dz += creg.correlation(x,y) * dzx * dzy
        dz = special_square_root(dz)

        z = self.UncertainQuantity(zbar,dz)

        return z

      return decorate(func,wrapper)

    return Decorator

  def make_sigfig_UQ( self, nom, sigfigs ):
    '''Create and return uncertain quantity from a quantity and number of sigfigs. The
    uncertain quantity will have an error that corresponds to the last
    significant figure plus or minus 1.'''

    # need to determine the type for the uncertainty value.
    # uncertainty value type should match the nominal value type,
    # unless it is an int. If nominal type is an int, it is
    # possible for the uncertainty to be a decimal.
    # i.e. 2 +/- 0.1
    try: unc_type = type(nom.magnitude)
    except: unc_type = type(nom)
    if unc_type is int:
      unc_type = float


    nom = nominal( nom )
    # round to correct number of sigfigs
    val = sigfig_round( nom, sigfigs )
    # get sigfig decimal postion
    pos = get_sigfig_decimal_pos( magof(nom), sigfigs )
    # the uncertainty is the last significant figure plus-or-minus 1
    # need to make sure we cast the value type to match the nominal value passed in
    unc = self.UncertainQuantity.Quantity( unc_type(pow(10,-pos)),unitsof(nom))

    return self.UncertainQuantity(val, unc)

  def percent_error( self, expected, measured ):
    return self.UncertainQuantity.Quantity( abs( (nominal(expected) - nominal(measured) ) / nominal(expected) ) ).to('percent')

  def percent_difference( self, a, b ):
    return self.UncertainQuantity.Quantity( 2*abs( (nominal(a) - nominal(b) ) / (nominal(a) + nominal(b)) ) ).to('percent')

  def agree(self, a, b):
    return self.z(a,b) <= 2


class AutoErrorPropagator( PositiveIntervalPropagator ):
  '''An error propagator that automatically propagates error based on a given number of significant figures. For example,
     by default the propagator determines the uncertainy in the result by assuming all input parameters
     have 3 significant figures and the last significant figure is uncertain by plus/minus 1.'''
  def __init__(self, uconv, sigfigs = 3, *args, **kargs):
    self.uconv = uconv
    self.sigfigs = sigfigs
    super( AutoErrorPropagator, self ).__init__( *args, **kargs )

  def __propagate_errors__(self, func, *args, **kargs):
    new_args = []
    for i,a in enumerate(args):
      if not a.__class__.__name__ == 'UncertainQuantity':
        a = self.uconv.make_sigfig_UQ( a, self.sigfigs )
      new_args.append( a )

    new_kargs = dict()
    for k,v in list(kargs.items()):
      if not v.__class__.__name__ == 'UncertainQuantity':
        v = self.uconv.make_sigfig_UQ( v, self.sigfigs )
      new_kargs[k] = v

    value,uncertainties = super( AutoErrorPropagator, self).__propagate_errors__( func, *new_args, **new_kargs )

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
  UncertainQuantity.Quantity.__truediv__ = disable_for_UQ( UncertainQuantity.Quantity.__truediv__ )


  # automatically interpret string values as Decimals.
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
