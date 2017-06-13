#! /usr/bin/env python

from pyErrorProp import *

# we first need to setup an uncertainty convention, which then defines
# in class for uncertain quantities. the uncertain quantity is based
# on a pint Quantity class.
conv = UncertaintyConvention()
UQ_ = conv.UncertainQuantity
Q_ = UQ_.Quantity




# RAW DATA
# Q_ is an alias for pint.Quantity, it creates a quantity with units.
TimeData = Q_([ 0.431
              , 0.603
              , 0.504
              , 0.581
              , 0.588
              , 0.644
              , 0.595
              , 0.534
              , 0.563
              , 0.578 ], 's' ) # time measured in seconds

print 't:',TimeData
print

# conv.calc_UncertainQuantity will compute an uncertain quantity from an array of quantities.
TimeMeasurement = conv.calc_UncertainQuantity( TimeData )
print 't: {}'.format(TimeMeasurement) # this will pretty print the quantity

# UQ_ creates an uncertain quantity from two quantities
HeightMeasurement = UQ_( Q_(1.5,'m'), Q_(1,'cm') )
print 'h: {}'.format(HeightMeasurement)
print


# An object falling at a constant rate does so according to h = 1/2 g t^2, therefore
#
# g = 2 h / t^2
#
# We just need to write a function to calculate g from h and t, and tell pyErrorProp that
# we want to propagate error through it.

@conv.WithError
def CalcGravity( h, t ):
  return 2*h/t**2

# Now calculate gravitational acceleration with its uncertainty
Gravity = CalcGravity( HeightMeasurement, TimeMeasurement )

print 'g: {}'.format(Gravity)
print

# check to see if our measurement is consistent with the accepted value (9.81 m/s^2)
print "consistent:",conv.consistent( Q_(9.8,'m/s^2'), Gravity )
