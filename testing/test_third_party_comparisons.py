from pyErrorProp import UncertaintyConvention
from Utils import *

import timeit,math
import pytest

uconv = UncertaintyConvention()
UQ_ = uconv.UncertainQuantity
Q_  = UQ_.Quantity

def test_uncertainties_comparison_general():
  try:
    import uncertainties
    from uncertainties import ufloat
  except:
    return
    
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
  (xx,yy) = uncertainties.correlated_values_norm( [(2.5,0.5), (2.5,0.5)], [ [1,1],[1,1] ] )
  z = x - y
  zz = xx - yy
  assert Close( z.nominal.magnitude, 0, 1e-5 )
  assert Close( z.nominal.magnitude, zz.nominal_value, 1e-5 )
  assert Close( z.uncertainty.magnitude, zz.std_dev, 1e-5 )


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


  zz = 2*xx
  ww = zz + yy

  z = 2*x
  w = z + y

  corr = uncertainties.correlation_matrix( [xx,yy,zz,ww] )

  assert x.correlation(x) == corr[0][0]
  assert x.correlation(y) == corr[0][1]
  assert x.correlation(z) == corr[0][2]
  assert x.correlation(w) == corr[0][3]
  assert x.correlation(x) == corr[0][0]
  assert y.correlation(x) == corr[1][0]
  assert z.correlation(x) == corr[2][0]
  assert w.correlation(x) == corr[3][0]

def test_uncertainties_comparison_correlations():
  try:
    import uncertainties
    from uncertainties import ufloat
  except:
    return

  # compare error propagation.
  x = UQ_( '2.0 +/- 0.5 m' )
  y = UQ_( '3.5 +/- 0.25 m' )
  w = UQ_( '8.5 +/- 0.5 m' )

  xx = ufloat( 2.0, 0.5 )
  yy = ufloat( 3.5, 0.25 )
  ww = ufloat( 8.5, 0.5 )

  z = x*x
  zz = xx*xx

  z = x*y
  zz = xx*yy

  z = x*x + x*y
  zz = xx*xx + xx*yy

def test_uncertainties_comparison_speed():
  try:
    import uncertainties
    from uncertainties import ufloat
  except:
    return

  x = UQ_( '15. +/- 0.1 m' )
  y = UQ_( '25. +/- 0.2 m' )
  w = UQ_( '35. +/- 0.3 m' )

  xx = ufloat( 15, 0.1 )
  yy = ufloat( 25, 0.2 )
  ww = ufloat( 35, 0.3 )

  z = ((x - y)/(x - w))*w
  zz = ((xx - yy)/(xx - ww))*ww

  t_us = timeit.timeit( lambda : (((x - y)/(x - w))*w).uncertainty , number = 200 )
  t_unc = timeit.timeit( lambda : (((xx - yy)/(xx - ww))*ww).std_dev, number = 200 )

  assert t_us > t_unc

  assert Close( z.nominal.magnitude    , zz.nominal_value)
  assert Close( z.uncertainty.magnitude, zz.std_dev)

  corr = uconv.correlations.matrix( x,y,z,w )
  ccorr = uncertainties.correlation_matrix( [xx,yy,zz,ww] )

  for i in range(4):
    for j in range(4):
      assert Close( corr(i,j), ccorr[i][j], 0.1 )

def test_uncertainties_comparison_user_defined_funcs():
  try:
    import uncertainties
    from uncertainties import ufloat
  except:
    return

  x = UQ_( '15. +/- 0.1 m' )
  y = UQ_( '25. +/- 0.2 m' )
  w = UQ_( '35. +/- 0.3 m' )

  xx = ufloat( 15, 0.1 )
  yy = ufloat( 25, 0.2 )
  ww = ufloat( 35, 0.3 )

  def calc(x,y,w):
    return ((x - y)/(x - w))*w

  f = uconv.WithError(calc)
  ff = uncertainties.wrap(calc)

  z = f(x,y,w)
  zz = ff(xx,yy,ww)

  t_us  = timeit.timeit( lambda :  f( x, y, w), number = 200 )
  t_unc = timeit.timeit( lambda : ff(xx,yy,ww), number = 200 )

  assert t_us > t_unc

  assert Close( z.nominal.magnitude    , zz.nominal_value)
  assert Close( z.uncertainty.magnitude, zz.std_dev)

  corr = uconv.correlations.matrix( x,y,z,w )
  ccorr = uncertainties.correlation_matrix( [xx,yy,zz,ww] )

  for i in range(4):
    for j in range(4):
      assert Close( corr(i,j), ccorr[i][j], 0.1 )

def test_pint_measurement_comparison_speed():
  try:
    import uncertainties
  except:
    return
  import pint
  ureg = pint.UnitRegistry()

  x = UQ_( '15. +/- 0.1 m' )
  y = UQ_( '25. +/- 0.2 m' )
  w = UQ_( '35. +/- 0.3 m' )

  xx = ureg.Measurement( ureg.Quantity(15.,'m'), ureg.Quantity(0.1,'m') )
  yy = ureg.Measurement( ureg.Quantity(25.,'m'), ureg.Quantity(0.2,'m') )
  ww = ureg.Measurement( ureg.Quantity(35.,'m'), ureg.Quantity(0.3,'m') )

  z = ((x - y)/(x - w))*w
  zz = ((xx - yy)/(xx - ww))*ww

  print timeit.timeit( lambda : (((x - y)/(x - w))*w).uncertainty, number = 20 )
  print timeit.timeit( lambda : (((xx - yy)/(xx - ww))*ww).std_dev, number = 20 )

  assert Close( z.nominal.magnitude, zz.value.magnitude )
  # assert Close( z.uncertainty.magnitude, zz.error.magnitude )

def test_mcerp_comparison():
  try:
    import mcerp
    from mcerp import N
  except:
    return

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
  assert Close( z.nominal.magnitude, zz.mean, 1e-1 )
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
