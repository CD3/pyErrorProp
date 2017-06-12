import math

# Add support for Uncertain Quantities to mathematical functions
#
# For each function we want to support, we need:
#
# 1. A version of the function that accepts and returns pint.Quantity instances.
# 2. A version of the function that accepts and returns UncertainQuantity instances.
#
# The problem is complicated by pint's usage of a registry (which we have adopted as well).
# Quantities from different registries are not compatible, so we can't just create a registry
# and wrap all of the functions because the user's registry will not be compatible. So,
# we need a way to get at the user's registries...

# here is an example of how we would "manually" wrap sin
def manual_sin(x):
  # start with the math module's version
  f = math.sin
  try:
    # if the argument is a pint quantity, or an uncertain quantity, it will have a member named '_REGISTRY'
    # _REGISTRY will have a function named 'wraps()' that we can use to create
    # a unit-aware version of sin
    f = x._REGISTRY.wraps( x._REGISTRY(""), x._REGISTRY("radian"), False )(f)
    try:
      # if the argument is an uncertain quantity, it will have a member named '_CONVENTION', which will
      # have a method named 'WithError()'
      f = x._CONVENTION.WithError( f )
    except:
      pass
  except:
    pass

  return f(x)

# this will wrap functions for us
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

# the problem with the above approach is that a wrapped function is created every time the function is called.
# a better approach might be to create classes to store unit-aware and error propagatoin aware function.

def wrap_functions(REGISTRY):
  # allow a registry, or any object that has a registry to be passed in.
  if not hasattr(REGISTRY,'wraps') and hasattr(REGISTRY,'_REGISTRY'):
    REGISTRY = REGISTRY._REGISTRY

  R = REGISTRY

  import math
  class Funcs():
    pass

  funcs = [ [ 'sin', ['radian'], '' ],
            [ 'cos', ['radian'], '' ],
            [ 'tan', ['radian'], '' ],
            [ 'asin',[''], 'radian' ],
            [ 'acos',[''], 'radian' ],
            [ 'atan',[''], 'radian' ],
            [ 'exp',[''], '' ],
            [ 'log',[''], '' ],
            [ 'log10',[''], '' ],
            [ 'erf',[''], '' ],
            [ 'erfc',[''], '' ],
            [ 'gamma',[''], '' ],
            [ 'lgamma',[''], '' ],
            None
          ]
  for f in funcs:
    if f is not None:
      setattr(Funcs, f[0], staticmethod(R.wraps( f[2], f[1], False)( getattr( math, f[0] ) ) ) )



  return Funcs











