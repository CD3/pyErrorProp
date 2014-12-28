
from pyErrorProp import *
import math
import numpy
import sympy

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

def sort_uncertainties( unc ):
  return sorted( unc, key = numpy.abs )
