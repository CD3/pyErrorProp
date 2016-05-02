from pyErrorProp import UncertaintyConvention
import numpy

uconv = UncertaintyConvention()
UQ_ = uconv.UncertainQuantity
Q_  = UQ_.Quantity

def Close( a, b, tol = 0.01 ):
    if isinstance(a,int):
        a = float(a)
    if isinstance(b,int):
        b = float(b)
    return (a - b)**2 / (a**2 + b**2) < 4*tol*tol


def test_from_data():

  data = [ Q_( 1, 'm' )
         , Q_( 2, 'm' )
         , Q_( 3, 'm' )
         ]

  x = uconv.calc_UncertainQuantity( data )

  assert Close( x.nominal.magnitude    , 2 )
  assert Close( x.uncertainty.magnitude, numpy.std( numpy.array([1,2,3]) )/(3.**0.5) )

