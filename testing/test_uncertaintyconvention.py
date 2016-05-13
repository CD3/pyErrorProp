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
  assert Close( x.uncertainty.magnitude, numpy.std( numpy.array([1,2,3]) )/(3.**0.5) )


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

