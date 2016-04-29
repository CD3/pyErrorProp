from UncertainQuantity import *
import pint
import numpy
import math
import pytest

units = UR

Q_ = units.Quantity
UQ_ = UncertainQuantity

def test_properties():

  x = UQ_( Q_(1,'m'), Q_(1,'cm') )

  assert x.nominal     == Q_(1,'m')
  assert x.uncertainty == Q_(0.01,'m')
  assert x.upper       == Q_(1.01,'m')
  assert x.lower       == Q_(0.99,'m')

def test_math():

  assert sin( Q_(30,'degree') ).magnitude == math.sin( math.radians(30) )
  assert cos( Q_(30,'degree') ).magnitude == math.cos( math.radians(30) )
  assert tan( Q_(30,'degree') ).magnitude == math.tan( math.radians(30) )

  assert asin( Q_(0.5,'') ).to('degree').magnitude == math.degrees( math.asin( 0.5 ) )
  assert acos( Q_(0.5,'') ).to('degree').magnitude == math.degrees( math.acos( 0.5 ) )
  assert atan( Q_(0.5,'') ).to('degree').magnitude == math.degrees( math.atan( 0.5 ) )

  assert sqrt( Q_(16,'m^2') ) == Q_(4,'m')




def test_catchall():

  x = UQ_( Q_(30,'degree'), Q_(1,'degree') )

