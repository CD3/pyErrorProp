from pyErrorProp import UncertaintyRegistry
import pytest

uncreg = UncertaintyRegistry()
UQ_ = uncreg.UncertainQuantity
Q_ = UQ_.Quantity

def test_properties():
  x = UQ_( Q_(1,'m'), Q_(1,'cm') )

  assert x.nominal     == Q_(1,'m')
  assert x.uncertainty == Q_(0.01,'m')
  assert x.upper       == Q_(1.01,'m')
  assert x.lower       == Q_(0.99,'m')

def test_conversions():
  x = UQ_( Q_(1,'m'), Q_(1,'cm') )
  x.ito('ft')

  assert x.nominal     == Q_(1,'m').to('ft')
  assert x.uncertainty == Q_(1,'cm').to('ft')
  assert x.upper       == Q_(1.01,'m').to('ft')
  assert x.lower       == Q_(0.99,'m').to('ft')
