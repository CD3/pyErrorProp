from pyErrorProp import UncertaintyConvention,CorrelationRegistry

uconv = UncertaintyConvention()
UQ_ = uconv.UncertainQuantity
Q_ = UQ_.Quantity

def test_construction():
  x = UQ_( '2 +/- 0.2 m/s' )
  y = UQ_( '2 m/s +/- 1%' )

  creg = CorrelationRegistry()
  creg.correlated(x,y,0.6)

  assert creg.correlation(x,y) == 0.6

