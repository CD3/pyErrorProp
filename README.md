#pyErrorProp

This modules performs various calculations with uncertain quantities, including error propagation, with support for quantities (values with units).

*Features*
- full unit support
- error propagation through arbitrary user-defined functions
- simple function decorator syntax
- support for user-defined error propagation algorithms

##Examples

###Triangulation
Let's say you are performing a triangulation measurement to determine the distance to a far away object. You measure the angle between line of sight to the object and a reference
line from two different positions on the reference line, separate by some distance. You have an uncertainty in both angle measurements, and the distance between your observation
points. Now you want to calculate the distance from one of your observation points to the far away object.

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

which outputs

    (<Measurement(60.00, 1.00, degree)>, <Measurement(116.00, 1.00, degree)>, <Measurement(140.00, 5.00, meter)>)
    ((1.7 +/- 0.8)e+03) meter

###Gravity Measurement
A student performs an experiment to calculate the local acceleration constant by dropping a steel ball bearing from a known height 10 times and
timing how long it takes the ball bearing to hit the ground.

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

    assert Close( nominal(     Gravity ), Q_(7.8,'m/s^2') )
    assert Close( uncertainty( Gravity ), Q_(0.6,'m/s^2') )

which outputs

    (0.622 +/- 0.026) second (1.500 +/- 0.005) meter
    (7.8 +/- 0.6) meter / second ** 2
    3.34356847418 dimensionless
    False
