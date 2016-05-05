from pyErrorProp import UncertaintyConvention
from uncertainties import ufloat
from Utils import *

import timeit
import pytest

uconv = UncertaintyConvention()
UQ_ = uconv.UncertainQuantity
Q_  = UQ_.Quantity

def test_uncertainties_comparison():
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
  # not sure how to add correlation for two existing variables.
  assert not Close( z.uncertainty.magnitude, zz.std_dev, 1e-5 )


  N = 2
  data = [ UQ_('2 +/- 0.1 m') ] * N
  ddata = [ ufloat(2,0.1) ] * N

  z = sum(data)
  zz = sum(ddata)

  assert Close( z.nominal.magnitude, 2*2, 1e-5 )
  assert Close( z.uncertainty.magnitude, (2*0.1), 1e-5 )
  assert Close( z.nominal.magnitude, zz.nominal_value, 1e-5 )
  assert Close( z.uncertainty.magnitude, zz.std_dev, 1e-5 )


  N = 10
  data = [ UQ_('2 +/- 0.1 m') ] * N
  ddata = [ ufloat(2,0.1) ] * N

  z = sum(data)
  zz = sum(ddata)

  assert Close( z.nominal.magnitude, 10*2, 1e-5 )
  assert Close( z.uncertainty.magnitude, (10*0.1), 1e-5 )
  assert Close( z.nominal.magnitude, zz.nominal_value, 1e-5 )
  assert Close( z.uncertainty.magnitude, zz.std_dev, 1e-5 )
