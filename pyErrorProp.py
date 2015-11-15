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
    if isinstance(x, units.Quantity):
      return Q_( uncertainty( x.magnitude ), x.units )

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
    return True

  return False

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


def get_UQ( data ):
  '''Computes an uncertain quantity from a data set (computes the standard error)'''
  units = unitsof( data )
  nominal = numpy.mean( data )
  std_dev = numpy.std( data )
  std_err = std_dev / numpy.sqrt( len( data ) )

  return make_UQ( nominal, std_err )

make_UQ_ = make_UQ  # for the sake of consistency
get_UQ_ = get_UQ

def sort_uncertainties(u):
  '''Sorts a list of uncertainties from largest to smallest'''
  if isinstance( u, dict ) or isinstance( u, collections.OrderedDict ):
    return collections.OrderedDict( sorted( u.items() , reverse = True, key = lambda it : numpy.abs( it[1] ) ) )

  return u


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





