#! /bin/env python

import uncertainties
import pint
import numpy
import copy
import collections

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
  def __init__(self, func = None):
    self.set_return_uncertainties(True)
    self.setFunc(func)

  def setFunc(self, func = None):
    self.func = func

  def set_return_uncertainties(self, v):
    self.return_uncertainties = v

  @staticmethod
  def sort_uncertainties(u):
    if isinstance( u, dict ) or isinstance( u, collections.OrderedDict ):
      return collections.OrderedDict( sorted( u.items() , reverse = True, key = lambda it : numpy.abs( it[1] ) ) )

    return u

  @staticmethod
  def relative_uncertainties( uncertainties ):
    '''Determine the relative contribution of each uncertainty to the total uncertainty.'''
    total_unc = ErrorPropagator.total_uncertainty( uncertainties )
    relative_unc = dict()
    for k,v in uncertainties.items():
      relative_unc[k] = (total_unc - ErrorPropagator.total_uncertainty( collections.OrderedDict( filter( lambda it: it[0] != k, uncertainties.items() ) ) )  ) / total_unc

    return relative_unc

  @staticmethod
  def total_uncertainty( uncertainties ):
    '''Compute and return the total uncertainty from individual uncertainty contributions.'''
    if isinstance(uncertainties,dict) or isinstance(uncertainties,collecitons.OrderedDict) :
      uncs = uncertainties.values()
    else:
      uncs = uncertainties.values()
    return numpy.sqrt( sum( [ x*x for x in uncs ] ) )

  def __call__(self, *args, **kargs):
    nominal_value, uncertainties = self.propagate_uncertainties( *args, **kargs )
    uncertainty   = ErrorPropagator.total_uncertainty( uncertainties )
    if self.return_uncertainties:
      return ( make_unc_quant( nominal_value, uncertainty ), uncertainties)
    else:
      return make_unc_quant( nominal_value, uncertainty )




class PositiveIntervalPropagator( ErrorPropagator ):
  def __init__(self, *args, **kargs):
    super().__init__( *args, **kargs )


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

    #return {'nom': nominal_value, 'unc' : uncertainties }
    return (nominal_value, uncertainties)






