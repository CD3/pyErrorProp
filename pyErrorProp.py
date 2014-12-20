#! /bin/env python

import uncertainties
import pint
import numpy
import copy

units = pint.UnitRegistry()

Q_ = units.Quantity
UF_ = uncertainties.ufloat

#########
# utils 
#########

def nominal( x ):
  if isinstance(x, uncertainties.Variable) or isinstance( x, uncertainties.AffineScalarFunc):
    return x.nominal_value

  if isinstance(x, units.Quantity):
    return Q_( nominal( x.magnitude ), x.units )

  return x

def uncertainty( x ):
  if isinstance(x, uncertainties.Variable) or isinstance( x, uncertainties.AffineScalarFunc):
    return x.std_dev

  if isinstance(x, units.Quantity):
    return Q_( uncertainty( x.magnitude ), x.units )

  return 0.0

def upper( x ):
  return nominal(x) + uncertainty(x)

def lower( x ):
  return nominal(x) - uncertainty(x)

def is_uncertain( x ):
  if isinstance(x, uncertainties.Variable) or isinstance( x, uncertainties.AffineScalarFunc):
    return True

  return False


def make_unc_quant( nom, unc ):
  # if nominal value is a quantity, we need to return a quantity
  if isinstance( nom, units.Quantity ):
    u     = nom.units
    nom = nom.magnitude
    if isinstance( unc, units.Quantity ):
      unc = unc.to(u).magnitude
    else:
      unc = nom*unc

    return Q_( UF_(nom, unc), u )

    
  return UF_(nom,unc)



####################
# error propagators
####################


class ErrorPropagator:
  pass

class PositiveIntervalPropagator( ErrorPropagator ):
  def __init__(self, func = None):
    self.setFunc(func)

  def setFunc(self, func = None):
    self.func = func

  def __call__(self, *args, **kargs):
    return PositiveIntervalPropagator.propagate(self.func,args,kargs)

  @staticmethod
  def propagate(func, args = (), kargs = {}):

    nominal_args = []
    for a in args:
      nominal_args.append( nominal(a) )

    nominal_kargs = dict()
    for k in kargs:
      nominal_kargs[k] = nominal( kargs[k] )

    
    nominal_value = func(*nominal_args,**nominal_kargs)

    uncertainties = {}

    for i in range(len(args)):
      myargs = copy.copy(nominal_args)
      myargs[i] = upper( args[i] )
      uncertainties[i] = func(*myargs,**nominal_kargs) - nominal_value

    for karg in kargs:
      mykargs = copy.copy(nominal_kargs)
      mykargs[karg] = upper( kargs[karg] )
      uncertainties[karg] = func(*nominal_args,**mykargs) - nominal_value

    uncertainty = numpy.sqrt( sum( [ x*x for x in uncertainties.values() ] ) )

    

    return ( make_unc_quant( nominal_value, uncertainty ), uncertainties)






