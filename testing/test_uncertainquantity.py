from pyErrorProp import UncertaintyConvention
import pytest

uconv = UncertaintyConvention()
UQ_ = uconv.UncertainQuantity
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

def test_decimal_support():
  x = UQ_( Q_('1.50','m'), Q_('0.03','m') )
  y = UQ_( Q_(1.50,'m'), Q_(0.03,'m') )


def test_formatted_output():

  x = UQ_( Q_('1.50','m'), Q_('7','cm') )

  xstr = '{:Lx}'.format(x)

  assert xstr == r'\SI[]{1.50 +- 0.07}{\meter}'
