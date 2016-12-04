from pyErrorProp import UncertaintyConvention
import pint
from Utils import Close
import pytest

uconv = UncertaintyConvention()
UQ_ = uconv.UncertainQuantity
Q_ = UQ_.Quantity


def test_construction():
  x = UQ_( Q_(2,'m/s'), Q_(0.5,'cm/s') )

  assert Close( x.nominal.magnitude, 2 )
  assert Close( x.uncertainty.magnitude, 0.005 )


  x = UQ_( '2 +/- 0.2 m/s' )

  assert Close( x.nominal.magnitude, 2 )
  assert Close( x.uncertainty.magnitude, 0.2 )


  x = UQ_( '2 m/s +/- 1%' )

  assert Close( x.nominal.magnitude, 2 )
  assert Close( x.uncertainty.magnitude, 0.02 )


  x = UQ_( '2 +/- 1' )

  assert Close( x.nominal.magnitude, 2 )
  assert Close( x.uncertainty.magnitude, 1 )

  x = UQ_( '2 +/- 1%' )

  # assert Close( x.nominal.magnitude, 2 )
  # assert Close( x.uncertainty.magnitude, 0.02 )


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


  xstr = '{:f}'.format(x)
  assert xstr == r'9.877 +/- 0.012 meter'




  x = UQ_( Q_(9.87654321,'m'), Q_(1.2345,'cm') )

  xstr = '{:f}'.format(x)
  assert xstr == r'9.877 +/- 0.012 meter'


def test_string_parsing():

  t = UQ_.parse_string("1.0 +/- 0.01 m")
  assert t[0] == '1.0 m'
  assert t[1] == '0.01 m'

  t = UQ_.parse_string("1.0   +/- 0.01 m")
  assert t[0] == '1.0 m'
  assert t[1] == '0.01 m'

  t = UQ_.parse_string("1.0 m +/- 1 cm")
  assert t[0] == '1.0 m'
  assert t[1] == '1 cm'

  t = UQ_.parse_string("1.0 m +/- 0.01")
  assert t[0] == '1.0 m'
  assert t[1] == '0.01 dimensionless'

  t = UQ_.parse_string("1.0 m +/- 1%")
  assert t[0] == '1.0 m'
  assert t[1] == '1%'

  t = UQ_.parse_string("1.0 +/- 1")
  assert t[0] == '1.0 dimensionless'
  assert t[1] == '1 dimensionless'

def test_errors():
  with pytest.raises(pint.errors.DimensionalityError):
    x = UQ_( Q_(1,'m'), Q_(0.1,'s') )

  with pytest.raises(pint.errors.DimensionalityError):
    x = UQ_( '1 m +/- 0.1 s' )


def test_comparisons():

  x = UQ_(20, 3, 'm')
  y = UQ_(25, 4, 'm')
  z = UQ_(31, 4, 'm')

  assert     x.consistent(y)
  assert not x.consistent(z)
  assert not (x <  y)
  assert     (x <  z)
  assert not (y >  x)
  assert     (z >  x)


def test_correlation():

  x = UQ_( '1 m +/- 2 cm' )
  y = UQ_( '1 m +/- 2 cm' )
  z = UQ_( '-1 m +/- 2 cm' )

  x.correlated(y, 0.8)
  x.correlated(z,-0.8)

  assert x.correlation(y) == 0.8
  assert y.correlation(x) == 0.8
  assert x.correlation(z) == -0.8
  assert z.correlation(x) == -0.8

def test_offset_units():

  T = UQ_( Q_(212,'degF'), Q_(1,'degF') )

  assert Close( T.upper.magnitude, 213 )
  assert Close( T.lower.magnitude, 211 )

  T2 = T.to('degC')

  assert Close( T2.nominal.magnitude, 100 )
  assert Close( T2.error.magnitude, 0.555)

