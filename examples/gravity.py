#! /usr/bin/env python
# -*- coding: utf-8 -*-

import sys
sys.path.append('../')
import StringIO
import pylatex as pl
from pyErrorProp import *

pl.base_classes.LatexObject._escape = False

# RAW DATA
DataTable = StringIO.StringIO('''
Eric-1.5m CD-1.5m Eric-2.0m CD-2.0m
0.43      0.50    0.64      0.72
0.60      0.68    0.57      0.61
0.50      0.76    0.58      0.71
0.58      0.62    0.68      0.69
0.58      0.70    0.57      0.76
0.64      0.69    0.65      0.69
0.59      0.52    0.58      0.76
0.53      0.63    0.64      0.77
0.56      0.59    0.72      0.65
0.57      0.53    0.76      0.65
''')

TimeData = numpy.loadtxt( DataTable, skiprows=2, unpack=True )
TimeData = { 'Eric-1.5m' : Q_(TimeData[0], 's')
           ,   'CD-1.5m' : Q_(TimeData[1], 's')
           , 'Eric-2.0m' : Q_(TimeData[2], 's')
           ,   'CD-2.0m' : Q_(TimeData[3], 's') }


# MEASUREMENTS
TimeMeasurements = dict()
for key in TimeData.keys():
  TimeMeasurements[key] = get_UQ( TimeData[key], sigfigs=1 )

HeightMeasurements = dict()
HeightMeasurements['Eric-1.5m'] = UQ_( Q_(1.5,'m'), Q_(1,'cm') )
HeightMeasurements[  'CD-1.5m'] = UQ_( Q_(1.5,'m'), Q_(1,'cm') )
HeightMeasurements['Eric-2.0m'] = UQ_( Q_(2.0,'m'), Q_(1,'cm') )
HeightMeasurements[  'CD-2.0m'] = UQ_( Q_(2.0,'m'), Q_(1,'cm') )

# CALCULATIONS
@WithUncertainties
def Gravity( h, t ):
  return 2*h/t**2

GravityCalculations =  dict()
GravityUncertainties = dict()
for key in TimeData.keys():
  GravityCalculations[key],GravityUncertainties[key] = Gravity( HeightMeasurements[key], TimeMeasurements[key] )
  print '{:.5f}'.format(TimeMeasurements[key]), HeightMeasurements[key], '{:.5f}'.format(GravityCalculations[key])
  print GravityUncertainties[key]


# generage a latex document with our results
doc = pl.Document()
doc.packages.append( pl.Package( 'siunitx' ) )

with doc.create(pl.Section('Raw Data')):
  doc.append( 'Data was collected by dropping a steal ball bearing from a givin height 10 times and timing the fall.\n' )
  with doc.create(pl.Tabular('llll')) as table:
    table.add_row(('Eric \SI{1.5}{\meter} (s)', 'C.D. \SI{1.5}{\meter} (s)', 'Eric \SI{2}{\meter} (s)', 'C.D. \SI{2}{\meter} (s)'))
    table.add_hline()
    for i in range(10):
      r = []
      for k in ['Eric-1.5m','CD-1.5m','Eric-2.0m','CD-2.0m']:
        r.append( str( TimeData[k][i].to('s').magnitude ) )
      table.add_row( r )
  
  doc.append( '\nUncertainy for each time measurement is taken as the standard error of the 10 trials. Uncertainty for all heights was taken to be \SI{1}{\centi\meter}.\n' )
  with doc.create(pl.Tabular(pl.NoEscape('r@{: }l'))) as table:
    table.add_row(('Eric \SI{1.5}{\meter}', '{:.1uLx}'.format(TimeMeasurements['Eric-1.5m'])))
    table.add_row(('C.D. \SI{1.5}{\meter}', '{:.1uLx}'.format(TimeMeasurements['CD-1.5m'])))
    table.add_row(('Eric \SI{2}{\meter}', '{:.1uLx}'.format(TimeMeasurements['Eric-2.0m'])))
    table.add_row(('C.D. \SI{2}{\meter}', '{:.1uLx}'.format(TimeMeasurements['CD-2.0m'])))


  doc.append( '\nGravitational acceleration was calculated for each drop height.rror of the 10 trials.\n' )
  with doc.create(pl.Tabular(pl.NoEscape('r@{: }l'))) as table:
    table.add_row(('Eric \SI{1.5}{\meter}', '{:.1uLx}'.format(GravityCalculations['Eric-1.5m'])))
    table.add_row(('C.D. \SI{1.5}{\meter}', '{:.1uLx}'.format(GravityCalculations['CD-1.5m'])))
    table.add_row(('Eric \SI{2}{\meter}', '{:.1uLx}'.format(GravityCalculations['Eric-2.0m'])))
    table.add_row(('C.D. \SI{2}{\meter}', '{:.1uLx}'.format(GravityCalculations['CD-2.0m'])))




doc.generate_pdf()
