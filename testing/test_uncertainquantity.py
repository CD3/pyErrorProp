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

  x = UQ_( Q_('1.5','m'), Q_('7','cm') )

  xstr = '{:.1fLx}'.format(x)
  assert xstr == r'\SI[]{1.50 +- 0.07}{\meter}'
  xstr = '{:.2fLx}'.format(x)
  assert xstr == r'\SI[]{1.500 +- 0.070}{\meter}'
  xstr = '{:.3fLx}'.format(x)
  assert xstr == r'\SI[]{1.5000 +- 0.0700}{\meter}'



  x = UQ_( Q_('1.123456789','m'), Q_('9.87654321','cm') )

  xstr = '{:fLx}'.format(x)
  assert xstr == r'\SI[]{1.1 +- 0.1}{\meter}'

  xstr = '{:.1fLx}'.format(x)
  assert xstr == r'\SI[]{1.1 +- 0.1}{\meter}'
  xstr = '{:.2fLx}'.format(x)
  assert xstr == r'\SI[]{1.123 +- 0.099}{\meter}'
  xstr = '{:.3fLx}'.format(x)
  assert xstr == r'\SI[]{1.1235 +- 0.0988}{\meter}'
  xstr = '{:.4fLx}'.format(x)
  assert xstr == r'\SI[]{1.12346 +- 0.09877}{\meter}'
  xstr = '{:.5fLx}'.format(x)
  assert xstr == r'\SI[]{1.123457 +- 0.098765}{\meter}'
  xstr = '{:.6fLx}'.format(x)
  assert xstr == r'\SI[]{1.1234568 +- 0.0987654}{\meter}'




  x = UQ_( Q_('9.87654321','m'), Q_('1.2345','cm') )

  xstr = '{:fLx}'.format(x)
  assert xstr == r'\SI[]{9.877 +- 0.012}{\meter}'
  xstr = '{:.1fLx}'.format(x)
  assert xstr == r'\SI[]{9.88 +- 0.01}{\meter}'
  xstr = '{:.2fLx}'.format(x)
  assert xstr == r'\SI[]{9.877 +- 0.012}{\meter}'
  xstr = '{:.3fLx}'.format(x)
  assert xstr == r'\SI[]{9.8765 +- 0.0123}{\meter}'



