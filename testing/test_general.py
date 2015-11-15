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
    print()

    # CONFIGURATION
    # 
    # measure two angles separated by some distance

    Angle1     = UQ_(60,    1)*units.degree
    Angle2     = UQ_(180-64,1)*units.degree
    Seperation = UQ_(140,   5)*units.meter

    print(Angle1, Angle2, Seperation)


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
    print(Distance)

def test_doc_example_2():
  print()

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

  print Time, Height
  print Gravity

  # compute z-value from accepted value
  print z(Gravity, Q_(9.8,'m/s^2'))
  # does our value agree with the accepted value?
  print agree( Gravity, Q_(9.8,'m/s^2') )

  assert Close( nominal(     Gravity ), Q_(7.8,'m/s^2') )
  assert Close( uncertainty( Gravity ), Q_(0.6,'m/s^2') )
  assert Close( z(Gravity, Q_(9.8,'m/s^2')), 3.3 )
  assert not agree( Gravity, Q_(9.8,'m/s^2') )


