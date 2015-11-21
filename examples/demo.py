#! /usr/bin/env python
# -*- coding: utf-8 -*-

from pyErrorProp import *

# The following example calculates the gravitational acceleration constant from
# a set of 10 fall time measurements for a ball bearing dropped from 1.5 m

# RAW DATA
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

# get_UQ will compute an uncertain quantity from an array of quantities.
TimeMeasurement = get_UQ( TimeData )
print 't:', TimeMeasurement
print 't: {:.10f}'.format(TimeMeasurement)
print 

# by default, get_UQ will round the uncertainty to 2 significant figures
# and then round the nominal value to the same precision (decimal precision)
# the number of sigfigs to round to can be specified.
TimeMeasurement = get_UQ( TimeData, sigfigs=3 )
print 't:',TimeMeasurement
print 't: {:.10f}'.format(TimeMeasurement)
print

TimeMeasurement = get_UQ( TimeData, sigfigs=4 )
print 't:',TimeMeasurement
print 't: {:.10f}'.format(TimeMeasurement)
print

# or disabled all together
TimeMeasurement = get_UQ( TimeData, sigfigs=0 )
print 't:',TimeMeasurement
print 't: {:.10f}'.format(TimeMeasurement)
print

TimeMeasurement = get_UQ( TimeData, sigfigs=1 )

HeightMeasurement = UQ_( Q_(1.5,'m'), Q_(1,'cm') )  # UQ_ creates an uncertain quantity
print 'h:',HeightMeasurement
print 'h: {:.10f}'.format(HeightMeasurement)
print


# An object falling at a constant rate does so according to h = 1/2 g t^2, therefore
#
# g = 2 h / t^2
#
# We just need to write a function to calculate g from h and t, and tell pyErrorProp that
# we want to propagate error through it.

@WithError
def Gravity( h, t ):
  return 2*h/t**2

# Now calculate gravitational acceleration with its uncertainty
GravityCalc = Gravity( HeightMeasurement, TimeMeasurement )

print 'g:',GravityCalc
print 'g: {:.10f}'.format(GravityCalc)
print

# pyErrorProp does not round the result. use sigfig_round for that
GravityCalc = sigfig_round( GravityCalc, n=1 )
print 'g:',GravityCalc
print 'g: {:.10f}'.format(GravityCalc)
print

# we can also have the uncertainty contributions from each input quantity returned
@WithUncertainties
def Gravity( h, t ):
  return 2*h/t**2

# Now calculate gravitational acceleration with its uncertainty
GravityCalc,GravityUnc = Gravity( HeightMeasurement, TimeMeasurement )

print 'g:',GravityCalc
print 'g unc:',GravityUnc
print
