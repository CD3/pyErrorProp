# -*- coding: utf-8 -*-

from pyErrorProp import *
import math
import numpy
import sympy
import re

sympy.init_printing()




def Close( a, b, tol = 0.01 ):
    if isinstance(a,int):
        a = float(a)
    if isinstance(b,int):
        b = float(b)
    return (a - b)**2 / (a**2 + b**2) < 4*tol*tol

def test_misc():
  x = UF_( 10.0, 0.25, 'x' )
  y = UF_( 20.0, 0.50, 'y' )

  #prop = PositiveIntervalPropagator(lambda x : np.sqrt(x*x) )

  #u,v,a,b,c = sympy.symbols('u v a b c')

  #eq = a*u**2 + b*u + c
  #sol = sympy.solve(eq, u)
  #f = sympy.lambdify( (a,b,c), sol[0], "numpy" )
  #f(4,3,2)




def test_ballistic_pendulum():

  m,M,v0,v,h,g = sympy.symbols('m M v0 v h g')
  eqs = [ m*v0 - (m + M)*v
        , (m + M)*v*v/2. - m*g*h
        ]

  sol = sympy.solve( eqs, v0 )


def test_airtrack_examples():
  angle    = Q_( UF_( 2.14 , 0.05 ), units.degree )
  angle.ito(units.radians)
  distance = Q_( UF_( 1.00 , 0.01 ), units.meter  )
  time     = Q_( UF_( 2.338, 0.005), units.second )



  
  g,th,a,x,t = sympy.symbols('g th a x t')
  eqs = [ g*sympy.sin(th) - a, x - a*t*t/2 ]

  sol = sympy.solve(eqs, [g,a])

  gravity = sympy.lambdify( (th,x,t), sol[g], "numpy" )

  ans,_ = PositiveIntervalPropagator.propagate( gravity, (angle,distance,time) )
  assert Close( ans.nominal_value, 9.80 )
  assert Close( ans.std_dev , 0.25 )
