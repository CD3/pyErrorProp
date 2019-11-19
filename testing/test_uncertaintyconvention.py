from pyErrorProp import UncertaintyConvention
import numpy
from Utils import *

uconv = UncertaintyConvention()
UQ_ = uconv.UncertainQuantity
Q_  = UQ_.Quantity


def test_from_data():

  data = [ Q_( 1, 'm' )
         , Q_( 2, 'm' )
         , Q_( 3, 'm' )
         ]

  x = uconv.calc_UncertainQuantity( data )

  assert Close( x.nominal.magnitude    , 2 )
  assert Close( x.uncertainty.magnitude, numpy.std( numpy.array([1,2,3]), ddof=1 )/(3.**0.5) )

def test_from_data_with_decimal():
  data = [ Q_( '1', 'm' )
         , Q_( '2', 'm' )
         , Q_( '3', 'm' )
         ]

  x = uconv.calc_UncertainQuantity( data )

  assert str(x.nominal.magnitude) == '2'
  assert str(x.uncertainty.magnitude).startswith( '0.577350269' )

  x.normalize(2)

  assert str(x.nominal.magnitude) == '2.00'
  assert str(x.uncertainty.magnitude) ==  '0.58' 

  x.normalize(1)

  assert str(x.nominal.magnitude) == '2.0'
  assert str(x.uncertainty.magnitude) ==  '0.6' 


def test_ep_decorator():

  x = UQ_( '65 mile +/- 2%' )
  t = UQ_( '1 hr +/- 5 min' )

  @uconv.WithError
  def velocity(x,t):
    return x/t

  v = velocity(x,t)
  vv = x/t

  assert Close( v.nominal.magnitude     , vv.nominal.magnitude )
  assert Close( v.uncertainty.magnitude , vv.uncertainty.magnitude )

  nv = 65
  dvx = 65*1.02 - nv
  dvt = 65/(1+5./60) - nv
  dv = (dvx*dvx + dvt*dvt)**0.5

  assert Close( v.nominal.magnitude     , nv )
  assert Close( v.uncertainty.magnitude , dv )

def test_kwargs():

  x = UQ_( '65 mile +/- 2%' )
  t = UQ_( '1 hr +/- 5 min' )

  @uconv.WithError
  def velocity(x,t):
    return x/t

  v = velocity(x=x,t=t)
  vv = x/t

  assert Close( v.nominal.magnitude     , vv.nominal.magnitude )
  assert Close( v.uncertainty.magnitude , vv.uncertainty.magnitude )

  nv = 65
  dvx = 65*1.02 - nv
  dvt = 65/(1+5./60) - nv
  dv = (dvx*dvx + dvt*dvt)**0.5

  assert Close( v.nominal.magnitude     , nv )
  assert Close( v.uncertainty.magnitude , dv )


def test_rounding():

  x = UQ_( '123 m +/- 24.132 m' )

  nomt = type(x.nominal.magnitude)
  unct = type(x.error.magnitude)

  assert str(x) == "<UncertainQuantity(123, 24.132, meter)>"

  y = x.__round__(1)
  assert str(y) == "<UncertainQuantity(120, 20.0, meter)>"
  assert type(y.nominal.magnitude) == nomt
  assert type(y.error.magnitude) == unct

  # x is not changed by rounding
  assert str(x) == "<UncertainQuantity(123, 24.132, meter)>"


  y = x.__round__(2)
  assert str(y) == "<UncertainQuantity(123, 24.0, meter)>"
  assert type(y.nominal.magnitude) == nomt
  assert type(y.error.magnitude) == unct

  # normalization changes x in place
  x.normalize(1)
  assert str(x) == "<UncertainQuantity(120, 20.0, meter)>"
  assert type(x.nominal.magnitude) == nomt
  assert type(x.error.magnitude) == unct


  x = UQ_( '123 m +/- 0.032 m' )

  nomt = type(x.nominal.magnitude)
  unct = type(x.error.magnitude)

  y = x.__round__(1)
  assert str(y) == "<UncertainQuantity(123, 0.03, meter)>"
  assert type(y.nominal.magnitude) == nomt
  assert type(y.error.magnitude) == unct

  y = x.__round__(2)
  assert str(y) == "<UncertainQuantity(123, 0.032, meter)>"
  assert type(y.nominal.magnitude) == nomt
  assert type(y.error.magnitude) == unct

def test_exact_inputs():

  L = Q_(2,'m')
  W = Q_(4,'m')

  @uconv.WithError
  def area(l,w):
    return l*w

  A = area(L,W)

  assert Approx(8) == A.nominal.magnitude
  assert A.uncertainty.magnitude < 1e-20


  L = UQ_(2,0,'m')
  W = UQ_(4,0,'m')

  A = area(L,W)

  assert Approx(8) == A.nominal.magnitude
  assert A.uncertainty.magnitude < 1e-20


def test_z_value_calculations():

  assert str(uconv.z( Q_(10.0,'cm'), UQ_(9.0,0.5,'cm') ) ).startswith('2.0')
  assert str(uconv.z( Q_('10.0','cm'), UQ_('9.0','0.5','cm') ) ).startswith('2')






