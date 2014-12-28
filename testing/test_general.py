# -*- coding: utf-8 -*-

from pyErrorProp.pyErrorProp import *
import math
import numpy
import sympy

sympy.init_printing()




def Close( a, b, tol = 0.01 ):
    if isinstance(a,int):
        a = float(a)
    if isinstance(b,int):
        b = float(b)
    return (a - b)**2 / (a**2 + b**2) < 4*tol*tol


def test_sort_uncertainties():

  def func( a, b, c, d):
    return a + b**2 + c**3 + d**4


  func_ = PositiveIntervalPropagator( func )


  a = UF_(2.,2)
  b = UF_(2.,0.02)
  c = UF_(2.,0.02)
  d = UF_(2.,0.02)

  
  result, unc = func_(a,b,c,d)

  unc    =  ErrorPropagator.sort_uncertainties( unc )
  relunc =  ErrorPropagator.relative_uncertainties( unc )

  print(relunc)
