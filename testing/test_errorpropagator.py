# -*- coding: utf-8 -*-

import pint, numpy
from pyErrorProp import *
import pytest

ureg = pint.UnitRegistry()
Q_ = ureg.Quantity
UQ_ = ureg.Measurement



def Close( a, b, tol = 0.01 ):
    if isinstance(a,int):
        a = float(a)
    if isinstance(b,int):
        b = float(b)
    return (a - b)**2 / (a**2 + b**2) < 4*tol*tol

def test_simple_error_prop():

  x = UQ_(2.5, 0.1, 'm')
  t = Q_(33,'ms').plus_minus(0.05,relative=True)

  @WithError
  def velocity(x,t):
    return x/t

  v,dv = velocity(x,t)

  nominal_value = 2.5/33e-3
  unc = [ (2.5+0.1)/33e-3 - nominal_value
        ,2.5/(33e-3*(1 + 0.05)) - nominal_value
        ]
  uncertainty_value = numpy.sqrt( sum( [ x*x for x in unc ] ) )
  assert Close( v , Q_(nominal_value,'m/s') )
  assert Close( dv, Q_(uncertainty_value,'m/s') )

def test_doc_example_1():
    # print()

    # CONFIGURATION
    # 
    # measure two angles separated by some distance

    Angle1     = UQ_(60,    1, 'degree' )
    Angle2     = UQ_(180-64,1, 'degree' )
    Seperation = UQ_(140,   5,  'meter' )


    # enable error propgation 
    @WithError
    def calc( theta_1, theta_2, seperation ):
      # Calculate the distance from one observation point to the object
      # using the Law of Sines
      #
      #     d            L
      #  --------     --------
      #  sin(t_1)     sin(t_3)
      #
      # th_3 = 180 - th_1 - th_2
      #
      # L : separation distance
      # th_1 : angle 1
      # th_2 : angle 2
      #
      theta_3 = 180*ureg.degree - theta_1 - theta_2
      return seperation * numpy.sin( theta_1 ) / numpy.sin(theta_3)

    Distance,Uncertainty = calc( theta_1=Angle1, theta_2=Angle2, seperation=Seperation )
    # print(Distance)


@pytest.mark.skipif(True,reason="")
def test_ballistic_pendulum():

  m,M,v0,v,h,g = sympy.symbols('m M v0 v h g')
  eqs = [ m*v0 - (m + M)*v
        , (m + M)*v*v/2. - m*g*h
        ]

  sol = sympy.solve( eqs, v0 )

@pytest.mark.skipif(True,reason="")
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

@pytest.mark.skipif(True,reason="")
def test_auto_propagator():

  Length = Q_(10,'m')
  Width  = Q_(5,'m')

  @WithAutoError()
  def area( l, w ):
    return l*w

  Area = area( Length, Width )

  A0 = Length*Width
  A1 = Length*(Width+Q_(0.01,'m'))
  A2 = (Length+Q_(0.1,'m'))*Width

  U = numpy.sqrt( (A1-A0)**2 + (A2-A0)**2 )

  assert Close( A0, nominal(Area), 0.01 )
  assert Close(  U, uncertainty(Area), 0.01 )

@pytest.mark.skipif(True,reason="")
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
