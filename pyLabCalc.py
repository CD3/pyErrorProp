
from pyErrorProp.pyErrorProp import *
import math
import numpy
import sympy
import collections

def Units( v ):
  if isinstance( v, units.Quantity ):
    return v.units

  return None

def Quant( v, u ):
  if u != None:
    return units.Quantity(v,u)

  return v


def compute_unc_quant( data ):
  units = Units( data )
  nominal = numpy.mean( data )
  std_dev = numpy.std( data )
  std_err = std_dev / numpy.sqrt( len( data ) )

  return make_unc_quant( nominal, std_err )

def rel_unc( q ):
  return (uncertainty( q ) / nominal( q ) )*100

def z( actual, measured ):
  return ( numpy.abs( nominal(actual) - nominal(measured) ) ) / numpy.sqrt( uncertainty(actual)**2 + uncertainty(measured)**2 )

def agree( q1, q2 ):
  return z(q1,q2) < 2.0

def percent_error( actual, measured ):
  return ((nominal(measured)-nominal(actual))/nominal(actual))*100

def sort_uncertainties(u):
  if isinstance( u, dict ) or isinstance( u, collections.OrderedDict ):
    return collections.OrderedDict( sorted( u.items() , reverse = True, key = lambda it : numpy.abs( it[1] ) ) )

  return u

def relative_uncertainties( uncertainties ):
  '''Determine the relative contribution of each uncertainty to the total uncertainty.'''
  total_unc = ErrorPropagator.total_uncertainty( uncertainties )
  relative_unc = dict()
  for k,v in uncertainties.items():
    relative_unc[k] = (total_unc - ErrorPropagator.total_uncertainty( collections.OrderedDict( filter( lambda it: it[0] != k, uncertainties.items() ) ) )  ) / total_unc

  return relative_unc

