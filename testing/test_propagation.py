# -*- coding: utf-8 -*-

from pyErrorProp import *
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


def test_ballistic_pendulum():

  m,M,v0,v,h,g = sympy.symbols('m M v0 v h g')
  eqs = [ m*v0 - (m + M)*v
        , (m + M)*v*v/2. - m*g*h
        ]

  sol = sympy.solve( eqs, v0 )


def test_airtrack_examples():
  angle    = Q_( UF_( 2.14 , 0.05 ), units.degree )
  angle.ito(units.radians)
  distance = UF_( 1.00 , 0.01 )* units.meter
  time     = uncertainties.ufloat( 2.338, 0.005)* units.second



  
  g,th,a,x,t = sympy.symbols('g th a x t')
  eqs = [ g*sympy.sin(th) - a, x - a*t*t/2 ]

  sol = sympy.solve(eqs, [g,a])

  gravity = sympy.lambdify( (th,x,t), sol[g], "numpy" )

  ans,_ = PositiveIntervalPropagator.propagate( gravity, (angle,distance,time) )
  assert Close( ans.nominal_value, 9.80 )
  assert Close( ans.std_dev , 0.25 )
