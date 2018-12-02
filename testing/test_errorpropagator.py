# -*- coding: utf-8 -*-

import pint, numpy
from pyErrorProp import *
import pytest
from Utils import Close
from inspect import signature 
import sympy

ureg = pint.UnitRegistry()
Q_ = ureg.Quantity
UQ_ = ureg.Measurement




def test_error_prop_decorator_signatures():

  @WithError
  def func(x,y):
    return x*y

  assert len(signature(func).parameters) == 2
  assert list(signature(func).parameters)[0] == 'x'
  assert list(signature(func).parameters)[1] == 'y'




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

def test_simple_error_prop_with_kwargs():
  x = UQ_(2.5, 0.1, 'm')
  t = Q_(33,'ms').plus_minus(0.05,relative=True)

  @WithError
  def velocity(x,t):
    return x/t

  v,dv = velocity(x=x,t=t)

  nominal_value = 2.5/33e-3
  unc = [ (2.5+0.1)/33e-3 - nominal_value
        ,2.5/(33e-3*(1 + 0.05)) - nominal_value
        ]
  uncertainty_value = numpy.sqrt( sum( [ x*x for x in unc ] ) )
  assert Close( v , Q_(nominal_value,'m/s') )
  assert Close( dv, Q_(uncertainty_value,'m/s') )

def test_offset_units():
  pass
  # todo: test @WithError function that takes temperature as an argument.
  # todo: test @WithError function that takes temperature difference as an argument.



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

  ans,unc = gravity(angle=angle,distance=distance,time=time)

  assert Close( ans, Q_(9.80,'m/s^2') )
  assert Close( unc , Q_(0.25,'m/s^2') )

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

  Volume,VolumeUnc = Vol(Length,Width,Height)
  assert Close(  V,     Volume.magnitude, 0.001 )
  assert Close( dV,     VolumeUnc.magnitude, 0.001 )

