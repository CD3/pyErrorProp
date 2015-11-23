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

def test_auto_propagator():

  Length = Q_(10,'m')
  Width  = Q_(5,'m')

  @WithAutoError()
  def area( l, w ):
    return l*w

  Area = area( Length, Width )

  A0 = Length*Width
  A1 = Length*Width*1.01
  A2 = Length*1.01*Width

  U = numpy.sqrt( (A1-A0)**2 + (A2-A0)**2 )

  assert Close( A0, nominal(Area), 0.01 )
  assert Close(  U, uncertainty(Area), 0.01 )

def test_multiple_funcs():

  def Area(l,w):
    return l*w

  @WithError
  def Vol(l,w,h):
    a = Area(l,w)
    return a*h

  Length = UQ_(2.,.1,'m')
  Width  = UQ_(3.,.8,'m')
  Height = UQ_(4.,.4,'m')

  V = (2.0+0.0)*(3.0+0.0)*(4.0+0.0)
  dV1 = (2.0+0.1)*(3.0+0.0)*(4.0+0.0) - V
  dV2 = (2.0+0.0)*(3.0+0.8)*(4.0+0.0) - V
  dV3 = (2.0+0.0)*(3.0+0.0)*(4.0+0.4) - V
  dV = numpy.sqrt( dV1**2 + dV2**2 + dV3**2 )

  Volume = Vol(Length,Width,Height)
  print Volume
  assert Close(  V,     nominal(Volume).magnitude, 0.001 )
  assert Close( dV, uncertainty(Volume).magnitude, 0.001 )
