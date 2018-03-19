import pint
from Utils import *

u = pint.UnitRegistry()
Q_ = u.Quantity


def test_pint_and_mpmath():
  try:
    import mpmath as mp
  except:
    return

  x = Q_(mp.mpf('60'), 'degree')
  assert mp.cos(x.to('radian')) == Approx(0.5)

  cos = u.wraps(u.dimensionless,u.radian)(mp.cos)
  assert isinstance(cos(x),Q_)
  assert cos(x).magnitude == Approx(0.5)

  mp.cos = u.wraps(u.dimensionless,u.radian)(mp.cos)
  assert isinstance(mp.cos(x),Q_)
  assert mp.cos(x).magnitude == Approx(0.5)
  


def test_mpmath_vs_decimal():
  try:
    import mpmath as mp
    import numpy as np
    import decimal as d
    import math as m
  except:
    return

  
  x1 = Q_(mp.mpf('30'), 'degree')
  x2 = Q_(d.Decimal('30'), 'degree')
  x3 = Q_(float(30), 'degree')


  assert mp.sin(x1.to('radian')) == Approx(0.5)
  assert m.sin(x2.to('radian')) == Approx(0.5)
  assert np.sin(x3.to('radian')).magnitude == Approx(0.5)

  sin = u.wraps(u.dimensionless,u.radian)(mp.sin)

  assert isinstance(sin(x1),Q_)
  assert sin(x3).magnitude == Approx(0.5)
