# -*- coding: utf-8 -*-

from pyErrorProp import *
from pyErrorProp.util import *
import pint
import decimal
from Utils import Close
import pytest

try:
  import mpmath
except:
  pass


def test_sigfig_rounding():

  x = 1.23456789

  assert get_sigfig_decimal_pos(x,1) == 0
  assert get_sigfig_decimal_pos(x,2) == 1
  assert get_sigfig_decimal_pos(x,3) == 2

  assert Close( sigfig_round( x, 2 ), 1.2,    0.00001 )
  assert Close( sigfig_round( x, 3 ), 1.23,   0.00001 )



  x = 0.000123456789

  assert get_sigfig_decimal_pos(x,1) == 4
  assert get_sigfig_decimal_pos(x,2) == 5
  assert get_sigfig_decimal_pos(x,3) == 6

  assert Close( sigfig_round( x, 2 ), 0.00012,    0.00001 )
  assert Close( sigfig_round( x, 3 ), 0.000123,   0.00001 )

  #                      1 sf     2 sf
  values = [ ('1.1'      , '1.0'    , '1.1'     )
           , ('1.4'      , '1.0'    , '1.4'     )
           , ('1.5'      , '2.0'    , '1.5'     )
           , ('1.9'      , '2.0'    , '1.9'     )
           , ('0.01'     , '0.01'   , '0.010'   )
           , ('0.011'    , '0.01'   , '0.011'   )
           , ('0.014'    , '0.01'   , '0.014'   )
           , ('0.01501'  , '0.02'   , '0.015'   )
           , ('0.019'    , '0.02'   , '0.019'   )
           , ('0.001'    , '0.001'  , '0.0010'  )
           , ('0.0011'   , '0.001'  , '0.0011'  )
           , ('0.0014'   , '0.001'  , '0.0014'  )
           , ('0.001501' , '0.002'  , '0.0015'  )
           , ('0.0019'   , '0.002'  , '0.0019'  )
           , ('0.0001'   , '0.0001' , '0.00010' )
           , ('0.00011'  , '0.0001' , '0.00011' )
           , ('0.00014'  , '0.0001' , '0.00014' )
           , ('0.0001501', '0.0002' , '0.00015' )
           , ('0.00019'  , '0.0002' , '0.00019' )
           ]

  D = decimal.Decimal
  for v in values:
    assert Close( D(v[1]), sigfig_round(D(v[0]),1), 0.00001 )
    assert Close( D(v[2]), sigfig_round(D(v[0]),2), 0.00001 )
    assert  D(v[1]) == sigfig_round(D(v[0]),1)
    assert  D(v[2]) == sigfig_round(D(v[0]),2)

  if 'mpmath' in sys.modules:

    x = mpmath.mpf('1.23456789')

    assert sigfig_round( x, 2 ) == mpmath.mpf('1.2')
    assert sigfig_round( x, 3 ) == mpmath.mpf('1.23')

  F = mpmath.mpf
  for v in values:
    assert F(v[1]) == sigfig_round(F(v[0]),1)
    assert F(v[2]) == sigfig_round(F(v[0]),2)




def test_sf_dec_count():
  assert get_sigfig_decimal_pos(1.2345, 1) == 0
  assert get_sigfig_decimal_pos(1.2345, 2) == 1
  assert get_sigfig_decimal_pos(1.2345, 3) == 2
  assert get_sigfig_decimal_pos(1.2345, 4) == 3
  assert get_sigfig_decimal_pos(1.2345, 5) == 4

  assert get_sigfig_decimal_pos(12.345, 1) == -1
  assert get_sigfig_decimal_pos(12.345, 2) == 0
  assert get_sigfig_decimal_pos(12.345, 3) == 1
  assert get_sigfig_decimal_pos(12.345, 4) == 2
  assert get_sigfig_decimal_pos(12.345, 5) == 3

  assert get_sigfig_decimal_pos(0.12345, 1) == 1
  assert get_sigfig_decimal_pos(0.12345, 2) == 2
  assert get_sigfig_decimal_pos(0.12345, 3) == 3
  assert get_sigfig_decimal_pos(0.12345, 4) == 4
  assert get_sigfig_decimal_pos(0.12345, 5) == 5

  assert get_sigfig_decimal_pos(0.000012345, 1) == 5
  assert get_sigfig_decimal_pos(0.000012345, 2) == 6
  assert get_sigfig_decimal_pos(0.000012345, 3) == 7
  assert get_sigfig_decimal_pos(0.000012345, 4) == 8
  assert get_sigfig_decimal_pos(0.000012345, 5) == 9

@pytest.mark.skipif(True,reason="need to port to new framework")
def test_unc_round():

  val,unc = sigfig_round( 1.234567890, u=0.2345678, n=2 )

  assert Close( 0.23, unc, 0.0001 )
  assert Close( 1.23, val, 0.0001 )


  val,unc = sigfig_round( 1.234567890, u=0.0345678, n=2 )

  assert Close( 0.035, unc, 0.0001 )
  assert Close( 1.235, val, 0.0001 )


  val,unc = sigfig_round( 1.234567890, u=0.0045678, n=2 )

  assert Close( 0.0046, unc, 0.0001 )
  assert Close( 1.2346, val, 0.0001 )

  val,unc = sigfig_round( 1.234567890, u=0.0005678, n=2 )

  assert Close( 0.00057, unc, 0.0001 )
  assert Close( 1.23467, val, 0.0001 )

def test_quantity_rounding():

  ureg = pint.UnitRegistry()
  Q_ = ureg.Quantity

  q = Q_(1.23456789, 'm/s')
  assert Close( Q_(1.00,'m/s'), sigfig_round(q,1), 0.00001 )
  assert Close( Q_(1.20,'m/s'), sigfig_round(q,2), 0.00001 )
  assert Close( Q_(1.23,'m/s'), sigfig_round(q,3), 0.00001 )

  q = Q_(100.23456789, 'm/s')
  assert Close( Q_(100,'m/s'), sigfig_round(q,1), 0.00001 )
  assert Close( Q_(100,'m/s'), sigfig_round(q,2), 0.00001 )
  assert Close( Q_(100,'m/s'), sigfig_round(q,3), 0.00001 )

  q = Q_(0.000000123456789, 'm/s')
  assert Close( Q_(0.000000100,'m/s'), sigfig_round(q,1), 0.00001 )
  assert Close( Q_(0.000000120,'m/s'), sigfig_round(q,2), 0.00001 )
  assert Close( Q_(0.000000123,'m/s'), sigfig_round(q,3), 0.00001 )

@pytest.mark.skipif(True,reason="need to port to new framework")
def test_measurement_rounding():
  q = UQ_( 1.2345678, 0.234567, 'N/m' )
  qr = sigfig_round( q )
  assert Close( Q_(1.23,'N/m'),     nominal(qr), 0.00001 )
  assert Close( Q_(0.23,'N/m'), uncertainty(qr), 0.00001 )
  
  q = UQ_( 1.2345678, 0.234567, 'N/m' )
  qr = sigfig_round( q, 3 )
  assert Close( Q_(1.235,'N/m'),     nominal(qr), 0.00001 )
  assert Close( Q_(0.235,'N/m'), uncertainty(qr), 0.00001 )

@pytest.mark.skipif(True,reason="need to port to new framework")
def test_data_based_calcs():
  # a time data set
  # average: 3.17647058824 s
  # std dev: 1.09733871213 s
  # std err: 0.266143730423 s
  TimeData = [ 1,2,3,4,2,3,3,4,2,4,3,5,3,4,2,4,5 ]*units.second

  Time = get_UQ_(TimeData)
  assert Close( Q_(3.18,'s'),     nominal(Time), 0.00001 )
  assert Close( Q_(0.27,'s'), uncertainty(Time), 0.00001 )

@pytest.mark.skipif(True,reason="need to port to new framework")
def test_quantity_formatting():
  x = Q_(1.23456789, 'kg m^2 / s^2')

  assert '{:.3}'.format( x )  ==  r'1.23 kilogram * meter ** 2 / second ** 2'
  assert '{:.3L}'.format( x ) ==  r'1.23 \frac{kilogram \cdot meter^{2}}{second^{2}}'
  assert '{:.3Lx}'.format( x ) == r'\SI[]{1.23}{\kilo\gram\meter\squared\per\second\squared}'

@pytest.mark.skipif(True,reason="need to port to new framework")
def test_measurement_formatting():
  x = UQ_(1.23456789, 0.0045678, 'kg m^2 / s^2')
  
  assert '{:.2u}'.format( x )  ==  r'(1.2346 +/- 0.0046) kilogram * meter ** 2 / second ** 2'
  assert '{:.2uL}'.format( x ) ==  r'\left(1.2346 \pm 0.0046\right) \frac{kilogram \cdot meter^{2}}{second^{2}}'
  assert '{:.2uLx}'.format( x ) == r'\SI[separate-uncertainty=true]{1.2346(46)}{\kilo\gram\meter\squared\per\second\squared}'

@pytest.mark.skipif(True,reason="need to port to new framework")
def test_output_formatting():
  x = Q_(1.23456789, 'kg m^2 / s^2')
  with open('quantity_formatting.latex','w') as f:
    f.write( '{:.2Lx}'.format( x ) )
  x = UQ_(1.23456789, 0.0045678, 'kg m^2 / s^2')
  with open('measurement_formatting.latex','w') as f:
    f.write( '{:.2uLx}'.format( x*1e7 ) )
  

@pytest.mark.skipif(True,reason="need to port to new framework")
def test_decimal():
  import decimal
  print
  x = Q_(0.15, 'kg m^2 / s^2')
  assert '{:.1f~}'.format(x) == '0.1 kg * m ** 2 / s ** 2' # rounds to 0.1 because 0.15 is really 0.1499...
  x = Q_(decimal.Decimal('0.15'), 'kg m^2 / s^2')
  assert '{:.1f~}'.format(x) == '0.2 kg * m ** 2 / s ** 2'  # rounds correctly because decimal module handles this
  x = Q_('0.15', 'kg m^2 / s^2')
  assert '{:.1f~}'.format(x) == '0.2 kg * m ** 2 / s ** 2' # passing string as value should use decimal module
  

  x = Q_('0.15', 'm')
  t = Q_('0.1', 'ms')
  v = x / t

  a = Q_(30, 'degree')
  # v_x = v*numpy.cos( a ) # can't mix Decimal and float types...


