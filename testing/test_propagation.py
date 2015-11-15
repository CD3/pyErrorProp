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
  angle    = UQ_( 2.14 , 0.05, 'degree' )
  distance = UQ_( 1.00 , 0.01 , 'm')
  time     = UQ_( 2.338, 0.005, 's' )

  
  @WithError
  def gravity(angle, distance, time):
    g,th,a,x,t = sympy.symbols('g th a x t')
    eqs = [ g*sympy.sin(th) - a, x - a*t*t/2 ]
    sol = sympy.solve(eqs, [g,a])
    g_ = sympy.lambdify( (th,x,t), sol[g], "numpy" )
    return g_(angle, distance, time)

  ans = gravity(angle=angle,distance=distance,time=time)

  assert Close( nominal(ans), Q_(9.80,'m/s^2') )
  assert Close( uncertainty(ans) , Q_(0.25,'m/s^2') )
