import pint
import numpy
import copy
import collections
import decimal

units = pint.UnitRegistry()

Q_ = units.Quantity
UQ_ = units.Measurement

#########
# utils 
#########

pint_quantity_new  = pint.quantity._Quantity.__new__
def quantity_new(cls,value,units=None):
  if isinstance(value, (str,unicode)):
    value = decimal.Decimal( value )
  return pint_quantity_new( cls, value, units )
pint.quantity._Quantity.__new__ = staticmethod(quantity_new)



def unitsof( v ):
  if isinstance( v, units.Quantity ):
    return v.units

  return Q_(1,'dimensionless').units

def magof( v ):
  if isinstance( v, units.Quantity ):
    return v.magnitude

  return v

def nominal( x ):
  '''Return the nominal value of a quantity'''
  try:
    return x.value
  except AttributeError:
    if isinstance(x, units.Quantity):
      return Q_( nominal( x.magnitude ), x.units )

    return x

def uncertainty( x ):
  '''Returns the uncertainty of a quantity'''
  try:
    return x.error
  except AttributeError:
    return 0

def upper( x ):
  '''Return the upper bound on a quantity (nominal + uncertainty)'''
  try:
    return nominal(x) + uncertainty(x)
  except:
    # adding the nominal value and uncertainty will fail for units that have an offset (like temperatures),
    # if we are here, it is most likely because we have a temperature quantity
    return Q_(nominal(x).magnitude + uncertainty(x).magnitude, unitsof(x))

def lower( x ):
  '''Return the lower bound on a quantity (nominal - uncertainty)'''
  return nominal(x) - uncertainty(x)

def is_uncertain( x ):
  '''Test wether a quantity has uncertianty'''
  if uncertainty(x) is 0:
    return False
  return True

def get_sigfig_decimal_pos( v, n ):
  '''Determine the decimal position of the n'th significant figure'''
  # The simplest way to identify significant figures is to represent
  # a number in scientific notation.
  #
  # examples:
  #
  # num       sci nota    1st sf    2nd sf
  #
  # 1.234  -> 1.234e+0 ->   0     -> +1
  # 12.34  -> 1.234e+1 ->  -1     ->  0
  # 0.1234 -> 1.234e-1 ->  +1     -> +2

  fmt = '{:.0e}'
  coeff,expo = fmt.format( float(v) ).split( 'e' )

  return -int(expo) + n - 1

def sigfig_round( v, n = 2, u = None ):
  '''Round a number or quantity to given number of significant figures.
  
  params:
    v    the value to round.
    n    the number of significant figures to round to.
    u    an uncertainty to round to.
    
    if an uncertainty is given, it is rounded to n significant figures and the value v
    is rounded to the same decimal postion as the result.
    
    Notes:

    If v is a measurment, its uncertainty is used for u.
    '''

  if n < 1:
    return v

  # need to check for Measurement class first because a Measurement is a Quantity
  if isinstance( v, pint.measurement._Measurement):
    nom = nominal(v)
    unc = uncertainty(v)
    nom,unc = sigfig_round(nom,n,unc)
    return UQ_( nom,unc )

  if isinstance( v, pint.quantity._Quantity ):
    unit  = v.units
    value = v.magnitude
    unc   = u.to(unit).magnitude if not u is None else None
    return Q_( sigfig_round(value,n,unc), unit )


  if not u is None:
    # An uncertainty was given, and we want to round this
    # uncertainty to the specified number of significant figures
    # and then round the value to the same decimal position.
    nd = get_sigfig_decimal_pos( u,n )
    return type(v)( round(float(v), nd ) ), type(u)( round(float(u), nd ) )



  # get the decimal position of the n'th sigfig and round
  nd = get_sigfig_decimal_pos( v,n )
  return type(v)( round(float(v), nd ) )





def make_UQ( nom, unc ):
  '''Create an uncertain quantity from two quantities'''
  if isinstance( nom, pint.quantity._Quantity ):
    u   = nom.units
    nom = nom.magnitude
    if isinstance( unc, pint.quantity._Quantity ):
      # check if uncertainty is a delta unit
      if len(unc._get_delta_units()) > 0:
        # unc is a delta unit, check that it is the correct
        # unit for nom
        if unc._has_compatible_delta(str(u)):
          # it is. convert it to an absolute unit
          unc = Q_(0,u) + unc
      unc = unc.to(u).magnitude
    else:
      # TODO: check nom for non-multiplicable units (temperature)
      unc = nom*unc
      
    return UQ_(nom, unc, u)
    
  return UQ_(nom,unc)

def make_sigfig_UQ( nom, sigfigs ):
  '''Create an uncertaint quantity from a quantity and number of sigfigs. The
  uncertain quantity will have an error that corresponds to the last
  significant figure plus or minus 1.'''
  nom = nominal( nom )
  # round to correct number of sigfigs
  val = sigfig_round( nom, sigfigs )
  # get sigfig decimal postion
  pos = get_sigfig_decimal_pos( magof(nom), sigfigs )
  # the uncertainty is the last significant figure plus-or-minus 1
  unc = Q_(pow(10,-pos),unitsof(nom))

  return UQ_(val, unc)

def get_UQ( data, sigfigs = 2 ):
  '''Computes an uncertain quantity from a data set (computes the standard error)'''
  nominal = numpy.mean( data )
  std_dev = numpy.std( data )
  std_err = std_dev / numpy.sqrt( len( data ) )

  q = make_UQ( nominal, std_err )
  if sigfigs > 0:
    q = sigfig_round( q, sigfigs )
  return q
calc_UQ = get_UQ

make_UQ_ = make_UQ  # for the sake of consistency
get_UQ_ = get_UQ

def sort_uncertainties(u):
  '''Sorts a list of uncertainties from largest to smallest'''
  if isinstance( u, dict ) or isinstance( u, collections.OrderedDict ):
    return collections.OrderedDict( sorted( u.items() , reverse = True, key = lambda it : numpy.abs( it[1] ) ) )

  return u



