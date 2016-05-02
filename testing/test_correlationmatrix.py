from pyErrorProp import UncertaintyConvention, CorrelationMatrix
import pint
import pytest
import Utils

uconv = UncertaintyConvention()
UQ_ = uconv.UncertainQuantity
Q_ = UQ_.Quantity

def test_construction():
  x = UQ_( '2 +/- 0.2 m/s' )
  y = UQ_( '2 m/s +/- 1%' )

  x.correlated(y,0.8)

  M = CorrelationMatrix.CorrelationMatrix( [x,y] )

  assert str(M) == '1.0 0.8 \n0.8 1.0 \n'
  
