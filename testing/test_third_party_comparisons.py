from pyErrorProp import UncertaintyConvention
from uncertainties import ufloat
from Utils import *

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

  z = x*y
  zz = xx*yy

  print z,zz
