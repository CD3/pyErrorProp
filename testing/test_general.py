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

def test_data_based_calcs():
  conv = UncertaintyConvention()
  Q_ = conv.UncertainQuantity.Quantity
  # a time data set
  # average: 3.17647058824 s
  # std dev: 1.09733871213 s
  # std err: 0.27433467803 s
  TimeData = [ 1,2,3,4,2,3,3,4,2,4,3,5,3,4,2,4,5 ]*Q_('s')


  Time = conv.calc_UncertainQuantity(TimeData)
  assert Close( Q_(3.17647058824,'s'),     nominal(Time), 0.00001 )
  assert Close( Q_(0.27433467803,'s'), uncertainty(Time), 0.00001 )



