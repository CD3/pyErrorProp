# -*- coding: utf-8 -*-

from pyErrorProp import *



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

  v = velocity(x,t)

  nominal_value = 2.5/33e-3
  unc = [ (2.5+0.1)/33e-3 - nominal_value
        ,2.5/(33e-3*(1 + 0.05)) - nominal_value
        ]
  uncertainty_value = numpy.sqrt( sum( [ x*x for x in unc ] ) )
  assert Close( nominal( v ), Q_(nominal_value,'m/s') )
  assert Close( uncertainty( v ), Q_(uncertainty_value,'m/s') )

def test_doc_example_1():
    # print()

    # CONFIGURATION
    # 
    # measure two angles separated by some distance

    Angle1     = UQ_(60,    1)*units.degree
    Angle2     = UQ_(180-64,1)*units.degree
    Seperation = UQ_(140,   5)*units.meter

    # print(Angle1, Angle2, Seperation)


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
      theta_3 = 180*units.degree - theta_1 - theta_2
      return seperation * numpy.sin( theta_1 ) / numpy.sin(theta_3)

    Distance = calc( theta_1=Angle1, theta_2=Angle2, seperation=Seperation )
    # print(Distance)

def test_doc_example_2():
  # print()

  # 10 time measurements
  TimeData = Q_([ 
  0.50,
  0.68,
  0.76,
  0.62,
  0.70,
  0.69,
  0.52,
  0.63,
  0.59,
  0.53], 's')

  # measured time
  Time = get_UQ_( TimeData )
  # all dropped from the same height
  Height = make_UQ_( 1.5*units.meter, 0.5*units.centimeter )

  # a function to calculate the acceleration of gravity
  # from our measurements with error propgation.
  @WithError
  def gravity( h, t ):
    return 2 * h / t**2


  # calculate gravity
  Gravity = gravity( Height, Time )

  # print Time, Height
  # print Gravity

  # compute z-value from accepted value
  # print z(Gravity, Q_(9.8,'m/s^2'))
  # does our value agree with the accepted value?
  # print agree( Gravity, Q_(9.8,'m/s^2') )

  assert Close( nominal(     Gravity ), Q_(7.8,'m/s^2') )
  assert Close( uncertainty( Gravity ), Q_(0.6,'m/s^2') )
  assert Close( z(Gravity, Q_(9.8,'m/s^2')), 3.3 )
  assert not agree( Gravity, Q_(9.8,'m/s^2') )


def test_rounding():
  #                      1 sf     2 sf
  values = [ (1.1      , 1.0    , 1.1     )
           , (1.4      , 1.0    , 1.4     )
           , (1.5      , 2.0    , 1.5     )
           , (1.9      , 2.0    , 1.9     )
           , (0.01     , 0.01   , 0.010   )
           , (0.011    , 0.01   , 0.011   )
           , (0.014    , 0.01   , 0.014   )
           , (0.01501  , 0.02   , 0.015   )
           , (0.019    , 0.02   , 0.019   )
           , (0.001    , 0.001  , 0.0010  )
           , (0.0011   , 0.001  , 0.0011  )
           , (0.0014   , 0.001  , 0.0014  )
           , (0.001501 , 0.002  , 0.0015  )
           , (0.0019   , 0.002  , 0.0019  )
           , (0.0001   , 0.0001 , 0.00010 )
           , (0.00011  , 0.0001 , 0.00011 )
           , (0.00014  , 0.0001 , 0.00014 )
           , (0.0001501, 0.0002 , 0.00015 )
           , (0.00019  , 0.0002 , 0.00019 )
           ]

  for v in values:
    assert Close( v[1], sigfig_round(v[0],1), 0.001 )
    assert Close( v[2], sigfig_round(v[0],2), 0.001 )

def test_sf_dec_count():
  assert get_sigfig_decimal_pos(1.2345, 1) == 0
  assert get_sigfig_decimal_pos(1.2345, 2) == 1
  assert get_sigfig_decimal_pos(1.2345, 3) == 2
  assert get_sigfig_decimal_pos(1.2345, 4) == 3
  assert get_sigfig_decimal_pos(1.2345, 5) == 4

  assert get_sigfig_decimal_pos(12.345, 1) == -1
  assert get_sigfig_decimal_pos(12.345, 2) == 0
  assert get_sigfig_decimal_pos(12.345, 3) == 1
  assert get_sigfig_decimal_pos(12.345, 4) == 2
  assert get_sigfig_decimal_pos(12.345, 5) == 3

  assert get_sigfig_decimal_pos(0.12345, 1) == 1
  assert get_sigfig_decimal_pos(0.12345, 2) == 2
  assert get_sigfig_decimal_pos(0.12345, 3) == 3
  assert get_sigfig_decimal_pos(0.12345, 4) == 4
  assert get_sigfig_decimal_pos(0.12345, 5) == 5

  assert get_sigfig_decimal_pos(0.000012345, 1) == 5
  assert get_sigfig_decimal_pos(0.000012345, 2) == 6
  assert get_sigfig_decimal_pos(0.000012345, 3) == 7
  assert get_sigfig_decimal_pos(0.000012345, 4) == 8
  assert get_sigfig_decimal_pos(0.000012345, 5) == 9

def test_unc_round():

  val,unc = sigfig_round( 1.234567890, u=0.2345678, n=2 )

  assert Close( 0.23, unc, 0.0001 )
  assert Close( 1.23, val, 0.0001 )


  val,unc = sigfig_round( 1.234567890, u=0.0345678, n=2 )

  assert Close( 0.035, unc, 0.0001 )
  assert Close( 1.235, val, 0.0001 )


  val,unc = sigfig_round( 1.234567890, u=0.0045678, n=2 )

  assert Close( 0.0046, unc, 0.0001 )
  assert Close( 1.2346, val, 0.0001 )

  val,unc = sigfig_round( 1.234567890, u=0.0005678, n=2 )

  assert Close( 0.00057, unc, 0.0001 )
  assert Close( 1.23467, val, 0.0001 )

def test_quantity_rounding():

  q = Q_(1.23456789, 'm/s')
  assert Close( Q_(1.00,'m/s'), sigfig_round(q,1), 0.00001 )
  assert Close( Q_(1.20,'m/s'), sigfig_round(q,2), 0.00001 )
  assert Close( Q_(1.23,'m/s'), sigfig_round(q,3), 0.00001 )

  q = Q_(100.23456789, 'm/s')
  assert Close( Q_(100,'m/s'), sigfig_round(q,1), 0.00001 )
  assert Close( Q_(100,'m/s'), sigfig_round(q,2), 0.00001 )
  assert Close( Q_(100,'m/s'), sigfig_round(q,3), 0.00001 )

  q = Q_(0.000000123456789, 'm/s')
  assert Close( Q_(0.000000100,'m/s'), sigfig_round(q,1), 0.00001 )
  assert Close( Q_(0.000000120,'m/s'), sigfig_round(q,2), 0.00001 )
  assert Close( Q_(0.000000123,'m/s'), sigfig_round(q,3), 0.00001 )

def test_measurement_rounding():
  q = UQ_( 1.2345678, 0.234567, 'N/m' )
  qr = sigfig_round( q )
  assert Close( Q_(1.23,'N/m'),     nominal(qr), 0.00001 )
  assert Close( Q_(0.23,'N/m'), uncertainty(qr), 0.00001 )
  
  q = UQ_( 1.2345678, 0.234567, 'N/m' )
  qr = sigfig_round( q, 3 )
  assert Close( Q_(1.235,'N/m'),     nominal(qr), 0.00001 )
  assert Close( Q_(0.235,'N/m'), uncertainty(qr), 0.00001 )

def test_data_based_calcs():
  # a time data set
  # average: 3.17647058824 s
  # std dev: 1.09733871213 s
  # std err: 0.266143730423 s
  TimeData = [ 1,2,3,4,2,3,3,4,2,4,3,5,3,4,2,4,5 ]*units.second

  Time = get_UQ_(TimeData)
  assert Close( Q_(3.18,'s'),     nominal(Time), 0.00001 )
  assert Close( Q_(0.27,'s'), uncertainty(Time), 0.00001 )

def test_quantity_formatting():
  x = Q_(1.23456789, 'kg m^2 / s^2')

  assert '{:.3}'.format( x )  ==  r'1.23 kilogram * meter ** 2 / second ** 2'
  assert '{:.3L}'.format( x ) ==  r'1.23 \frac{kilogram \cdot meter^{2}}{second^{2}}'
  assert '{:.3Lx}'.format( x ) == r'\SI{1.23}{\kilo\gram\meter\squared\per\second\squared}'
  

def test_decimal():
  x = Q_(1.234, 'kg m^2 / s^2')
  
