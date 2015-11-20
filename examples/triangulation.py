#! /usr/bin/env python
# -*- coding: utf-8 -*-

from pyErrorProp import *

print()
# CONFIGURATION
# 
# measure two angles separated by some distance

Angle1     = UQ_(93.5, 0.8)*units.degree
Angle2     = UQ_(83.1, 0.8)*units.degree
Seperation = UQ_(460., 4.)*units.foot

print(Angle1, Angle2, Seperation)


# enable error propgation 
prop = PositiveIntervalPropagator()
prop.set_return_uncertainties(True)
@WithErrorPropagator(prop)
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
  theta_3 = 180*units.degree - theta_1 - theta_2
  return seperation * numpy.sin( theta_1 ) / numpy.sin(theta_3)

Distance,Unc = calc( theta_1=Angle1, theta_2=Angle2, seperation=Seperation )
print(Distance.to('foot'))
print(Unc)

