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

def test_unit_aware_functions():

  qfuncs = Math.wrap_functions(Q_._REGISTRY)

  x = qfuncs.sin(Q_(90,'degree'))
  assert isinstance( x, Q_ )
  assert x.units == ""
  assert x.magnitude == Approx(1)

  x = qfuncs.cos(Q_(180,'degree'))
  assert isinstance( x, Q_ )
  assert x.units == ""
  assert x.magnitude == Approx(-1)

  x = qfuncs.tan(Q_(45,'degree'))
  assert isinstance( x, Q_ )
  assert x.units == ""
  assert x.magnitude == Approx(1)



  x = qfuncs.asin(Q_(1,'')).to('degree')
  assert isinstance( x, Q_ )
  assert x.units == "degree"
  assert x.magnitude == Approx(90)

  x = qfuncs.acos(Q_(-1,'')).to('degree')
  assert isinstance( x, Q_ )
  assert x.units == "degree"
  assert x.magnitude == Approx(180)

  x = qfuncs.atan(Q_(1,'')).to('degree')
  assert isinstance( x, Q_ )
  assert x.units == "degree"
  assert x.magnitude == Approx(45)

  assert isinstance( x, Q_ )
  assert x.units == "degree"
  assert x.magnitude == Approx(45)



  x = qfuncs.exp(Q_(1,''))
  assert isinstance( x, Q_ )
  assert x.units == ""
  assert x.magnitude == Approx(math.e)

  x = qfuncs.log(Q_(math.e,''))
  assert isinstance( x, Q_ )
  assert x.units == ""
  assert x.magnitude == Approx(1)

  x = qfuncs.log10(Q_(10.,''))
  assert isinstance( x, Q_ )
  assert x.units == ""
  assert x.magnitude == Approx(1)






