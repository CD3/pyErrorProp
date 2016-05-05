from pyErrorProp import UncertaintyConvention
from Utils import *

import timeit,math
import pytest

uconv = UncertaintyConvention()
UQ_ = uconv.UncertainQuantity
Q_  = UQ_.Quantity

def test_uncertainties_comparison():
  from uncertainties import ufloat
  # compare error propagation.
  x = UQ_( '2.5 +/- 0.5 m' )
  y = UQ_( '2.5 +/- 0.5 m' )
  w = x

  xx = ufloat( 2.5, 0.5 )
  yy = ufloat( 2.5, 0.5 )
  ww = xx

  z = x+y
  zz = xx+yy
  assert Close( z.nominal.magnitude, zz.nominal_value, 1e-5 )
  assert Close( z.uncertainty.magnitude, zz.std_dev, 1e-5 )

  z = x-y/2
  zz = xx-yy/2
  assert Close( z.nominal.magnitude, zz.nominal_value, 1e-5 )
  assert Close( z.uncertainty.magnitude, zz.std_dev, 1e-5 )

  z = x*y
  zz = xx*yy
  assert Close( z.nominal.magnitude, zz.nominal_value, 1e-5 )
  assert Close( z.uncertainty.magnitude, zz.std_dev, 1e-5 )

  z = x/y
  zz = xx/yy
  assert Close( z.nominal.magnitude, zz.nominal_value, 1e-5 )
  # linear approximation differs here!
  assert not Close( z.uncertainty.magnitude, zz.std_dev, 1e-5 )


  z = w - x
  zz = ww - xx
  assert Close( z.nominal.magnitude, 0, 1e-5 )
  assert Close( z.nominal.magnitude, zz.nominal_value, 1e-5 )
  assert Close( z.uncertainty.magnitude, zz.std_dev, 1e-5 )

  # add correlation
  x.correlated(y,1)
  z = x - y
  zz = xx - yy
  assert Close( z.nominal.magnitude, 0, 1e-5 )
  assert Close( z.nominal.magnitude, zz.nominal_value, 1e-5 )
  # can't correlate variables, only affinescalarfuncs
  assert not Close( z.uncertainty.magnitude, zz.std_dev, 1e-5 )


  num = 2
  data = [ UQ_('2 +/- 0.1 m') ] * num
  ddata = [ ufloat(2,0.1) ] * num

  z = sum(data)
  zz = sum(ddata)

  assert Close( z.nominal.magnitude, 2*2, 1e-5 )
  assert Close( z.uncertainty.magnitude, (2*0.1), 1e-5 )
  assert Close( z.nominal.magnitude, zz.nominal_value, 1e-5 )
  assert Close( z.uncertainty.magnitude, zz.std_dev, 1e-5 )


  num = 10
  data = [ UQ_('2 +/- 0.1 m') ] * num
  ddata = [ ufloat(2,0.1) ] * num

  z = sum(data)
  zz = sum(ddata)

  assert Close( z.nominal.magnitude, 10*2, 1e-5 )
  assert Close( z.uncertainty.magnitude, (10*0.1), 1e-5 )
  assert Close( z.nominal.magnitude, zz.nominal_value, 1e-5 )
  assert Close( z.uncertainty.magnitude, zz.std_dev, 1e-5 )



def test_mcerp_comparison():
  import mcerp
  from mcerp import N
  # bump up the number of samples that will be used
  mcerp.npts = 100000
  # compare error propagation.
  x = UQ_( '2.5 +/- 0.5 m' )
  y = UQ_( '2.5 +/- 0.5 m' )
  w = x

  xx = N( 2.5, 0.5 )
  yy = N( 2.5, 0.5 )
  ww = xx

  z = x+y
  zz = xx+yy
  assert Close( z.nominal.magnitude, zz.mean, 1e-2 )
  assert Close( z.uncertainty.magnitude, math.sqrt(zz.var), 1e-2 )

  z = x-y/2
  zz = xx-yy/2
  assert Close( z.nominal.magnitude, zz.mean, 1e-2 )
  assert Close( z.uncertainty.magnitude, math.sqrt(zz.var), 1e-2 )

  z = x*y
  zz = xx*yy
  assert Close( z.nominal.magnitude, zz.mean, 1e-2 )
  assert Close( z.uncertainty.magnitude, math.sqrt(zz.var), 1e-2 )

  z = x/y
  zz = xx/yy
  # expected value is not actually 1...
  assert not Close( z.nominal.magnitude, zz.mean, 1e-2 )
  assert not Close( z.uncertainty.magnitude, math.sqrt(zz.var), 1e-2 )


  z = w - x
  zz = ww - xx
  assert Close( z.nominal.magnitude, 0, 1e-2 )
  # mc based method will never get exactly zero
  # assert Close( z.nominal.magnitude, zz.mean, 1e-2 )
  assert Close( z.uncertainty.magnitude, math.sqrt(zz.var), 1e-2 )

  # add correlation
  x.correlated(y,1)
  z = x - y
  zz = xx - yy
  assert Close( z.nominal.magnitude, 0, 1e-2 )
  # assert Close( z.nominal.magnitude, zz.mean, 1e-2 )
  # can't correlate variables, only affinescalarfuncs
  assert not Close( z.uncertainty.magnitude, math.sqrt(zz.var), 1e-2 )


  num = 2
  data = [ UQ_('2 +/- 0.1 m') ] * num
  ddata = [ N(2,0.1) ] * num

  z = sum(data)
  zz = sum(ddata)

  assert Close( z.nominal.magnitude, 2*2, 1e-2 )
  assert Close( z.uncertainty.magnitude, (2*0.1), 1e-2 )
  assert Close( z.nominal.magnitude, zz.mean, 1e-2 )
  assert Close( z.uncertainty.magnitude, math.sqrt(zz.var), 1e-2 )


  num = 10
  data = [ UQ_('2 +/- 0.1 m') ] * num
  ddata = [ N(2,0.1) ] * num

  z = sum(data)
  zz = sum(ddata)

  assert Close( z.nominal.magnitude, 10*2, 1e-2 )
  assert Close( z.uncertainty.magnitude, (10*0.1), 1e-2 )
  assert Close( z.nominal.magnitude, zz.mean, 1e-2 )
  assert Close( z.uncertainty.magnitude, math.sqrt(zz.var), 1e-2 )
