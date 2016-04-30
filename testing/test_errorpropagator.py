# -*- coding: utf-8 -*-

from pyErrorProp import *
import pint, numpy

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

