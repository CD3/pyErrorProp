import math

# Add support for Uncertain Quantities to mathematical functions
#
# For each function we want to support, we need:
#
# 1. A version of the function that accepts and returns pint.Quantity instances.
# 2. A version of the function that accepts and returns UncertainQuantity instances.
#
# The problem is complicated by pints usage of a registry (which we have adopted as well).
# Quantities from different registries are not compatible, so we can't just create a registry
# and wrap all of the functions because the user's registry will not be compatible. So,
# we need a way to get at the user's registries...

# here is an example of how we would "manually" wrap sin

def manual_sin(x):
  f = x._REGISTRY.wraps( x._REGISTRY(""), x._REGISTRY("radian"), False )(math.sin)
  try:
    f = x._CONVENTION.WithError( f )
  except:
    pass

  return f(x)

def WrapNumFunc( func, ounit, iunit ):
  '''Wraps a numerical function to add support for units and uncertainty.'''

  def wrapped_func(x):
    f = func
    if isinstance( f, (str,unicode) ) and hasattr( math, f ):
      f = getattr( math, f )
    else:
      raise AttributeError( "Cannot find suitable function for '%s' in the math module." % f )

    # add unit support
    if hasattr(x,'_REGISTRY'):
      f = x._REGISTRY.wraps( x._REGISTRY(iunit), x._REGISTRY(ounit), False )(f)

    # add uncertainty support. this will fail if x is not an UncertainQuantity
    if hasattr(x,'_CONVENTION'):
      f = x._CONVENTION.WithError( f )

    return f(x)

  return wrapped_func



sin  = WrapNumFunc( 'sin'  , 'radian' , ''       )
cos  = WrapNumFunc( 'cos'  , 'radian' , ''       )
tan  = WrapNumFunc( 'tan'  , 'radian' , ''       )
asin = WrapNumFunc( 'asin' , ''       , 'radian' )
acos = WrapNumFunc( 'acos' , ''       , 'radian' )
atan = WrapNumFunc( 'atan' , ''       , 'radian' )
