from pyErrorProp import UncertaintyConvention, Math
from Utils import *
import math
import pytest

uconv = UncertaintyConvention()
UQ_ = uconv.UncertainQuantity
Q_  = UQ_.Quantity

def test_manual_wrap():
  x = Q_( 30, 'degree' )
  v = Math.manual_sin(x)
  assert Close( v, 0.5, 0.0001 )


  x = UQ_( 30, 1, 'degree' )
  v = Math.manual_sin(x)
  nv = math.sin( math.radians(30) )
  dv = math.sin( math.radians(31) ) - nv
  assert Close( v.nominal, nv, 0.0001 )
  assert Close( v.uncertainty, dv, 0.0001 )

def test_wrapping():
  sin = Math.WrapNumFunc( 'sin', 'radian', '' )
  x = Q_( 30, 'degree' )
  v = sin(x)
  assert Close( v, 0.5, 0.0001 )


  x = UQ_( 30, 1, 'degree' )
  v = sin(x)
  nv = math.sin( math.radians(30) )
  dv = math.sin( math.radians(31) ) - nv
  assert Close( v.nominal, nv, 0.0001 )
  assert Close( v.uncertainty, dv, 0.0001 )

  x = UQ_( 30, 1, 'degree' )
  v = Math.sin(x)
  nv = math.sin( math.radians(30) )
  dv = math.sin( math.radians(31) ) - nv
  assert Close( v.nominal, nv, 0.0001 )
  assert Close( v.uncertainty, dv, 0.0001 )

  # with pytest.raises(AttributeError):
    # sin = Math.WrapNumFunc( 'sn', 'radian', '' )
