#! /bin/env python

import pint
import numpy
import copy
import collections

units = pint.UnitRegistry()

Q_ = units.Quantity
UQ_ = units.Measurement

#########
# utils 
#########

def unitsof( v ):
  if isinstance( v, units.Quantity ):
    return v.units

  return units.Quantity('dimensionless').units

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
  return nominal(x) + uncertainty(x)

def lower( x ):
  '''Return the lower bound on a quantity (nominal - uncertainty)'''
  return nominal(x) - uncertainty(x)

def is_uncertain( x ):
  '''Test wether a quantity has uncertianty'''
  if uncertainty(x) is 0:
    return False
  return True

def make_UQ( nom, unc ):
  '''Create an uncertain quantity from two quantities'''
  if isinstance( nom, units.Quantity ):
    u   = nom.units
    nom = nom.magnitude
    if isinstance( unc, units.Quantity ):
      unc = unc.to(u).magnitude
    else:
      unc = nom*unc

    return UQ_(nom, unc, u)
    
  return UQ_(nom,unc)


def get_UQ( data, dorounding = False ):
  '''Computes an uncertain quantity from a data set (computes the standard error)'''
  nominal = numpy.mean( data )
  std_dev = numpy.std( data )
  std_err = std_dev / numpy.sqrt( len( data ) )

  q = make_UQ( nominal, std_err )
  if dorounding:
    q = sigfig_round( q, 2 )
  return q

make_UQ_ = make_UQ  # for the sake of consistency
get_UQ_ = get_UQ

def sort_uncertainties(u):
  '''Sorts a list of uncertainties from largest to smallest'''
  if isinstance( u, dict ) or isinstance( u, collections.OrderedDict ):
    return collections.OrderedDict( sorted( u.items() , reverse = True, key = lambda it : numpy.abs( it[1] ) ) )

  return u



####################
# error calculations
####################

def rel_unc( q ):
  '''Computes the relative uncertainty of an uncertain quantity'''
  return (uncertainty( q ) / nominal( q ) )*100

def percent_error( actual, measured ):
  return ((nominal(measured)-nominal(actual))/nominal(actual))*100

def z( x, y ):
  '''Compute the z value for two uncertain quantities'''
  return ( numpy.abs( nominal(x) - nominal(y) ) ) / numpy.sqrt( uncertainty(x)**2 + uncertainty(y)**2 )

def agree( x, y ):
  '''Return true if to quantities are statistically the same.'''
  return z(x,y) < 2.0


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
  '''Round a number or quantity to given number of significant figures.'''

  # need to check for Measurement class first because a Measurement is a Quantity
  if isinstance( v, units.Measurement ):
    nom = nominal(v)
    unc = uncertainty(v)
    nom,unc = sigfig_round(nom,n,unc)
    return UQ_( nom,unc )

  if isinstance( v, units.Quantity ):
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



####################
# error propagators
####################

class ErrorPropagator(object):
  def __init__(self, func = None):
    self.set_return_uncertainties(False)
    self.set_func(func)
    self.set_correlated(False)

  def set_func(self, func = None):
    self.func = func

  def set_return_uncertainties(self, v):
    self.return_uncertainties = v

  def set_correlated(self, v):
    self.correlated = v

  def total_uncertainty( self, uncertainties ):
    '''Compute and return the total uncertainty from individual uncertainty contributions.'''
    if isinstance(uncertainties,dict) or isinstance(uncertainties,collecitons.OrderedDict) :
      uncs = uncertainties.values()
    else:
      uncs = uncertainties.values()

    if self.correlated:
      return sum( uncs )
    else:
      return numpy.sqrt( sum( [ x*x for x in uncs ] ) )

  def __call__(self, *args, **kargs):
    nominal_value, uncertainties = self.propagate_uncertainties( *args, **kargs )
    uncertainty   = self.total_uncertainty( uncertainties )
    if self.return_uncertainties:
      return ( make_UQ( nominal_value, uncertainty ), uncertainties)
    else:
      return make_UQ( nominal_value, uncertainty )

class PositiveIntervalPropagator( ErrorPropagator ):
  def __init__(self, *args, **kargs):
    # super().__init__( *args, **kargs )
    super( PositiveIntervalPropagator, self ).__init__( *args, **kargs )


  def propagate_uncertainties(self, *args, **kargs):

    nominal_args = []
    for i,a in enumerate(args):
      nominal_args.append( nominal(a) )

    nominal_kargs = dict()
    for k,v in kargs.items():
      nominal_kargs[k] = nominal( v )

    
    nominal_value = self.func(*nominal_args,**nominal_kargs)

    uncertainties = dict()

    for i in range(len(args)):
      myargs = copy.copy(nominal_args)
      myargs[i] = upper( args[i] )
      uncertainties[i] = self.func(*myargs,**nominal_kargs) - nominal_value

    for karg in kargs:
      mykargs = copy.copy(nominal_kargs)
      mykargs[karg] = upper( kargs[karg] )
      uncertainties[karg] = self.func(*nominal_args,**mykargs) - nominal_value

    return (nominal_value, uncertainties)


def WithError(func):
  propagator = PositiveIntervalPropagator()
  propagator.set_func( func )
  return propagator

def WithErrorPropagator(propagator=None):
  if propagator is None:
    return WithError

  def Decorator(func):
    propagator.set_func( func )
    return propagator

  return Decorator





