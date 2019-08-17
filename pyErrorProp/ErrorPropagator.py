import copy
from .util import *
from .decorator import decorate


#########
# utils 
#########

def nominal( x ):
  '''Return the nominal value of an uncertainty quantity.
     This free function allows multiple uncertain quantity types to be supported
     in a generic way.'''
  try:
    # UncertainQuantity support
    return x.nominal
  except AttributeError:
    try:
      # pint.Measurement support
      return x.value
    except AttributeError:
      return x

def uncertainty( x ):
  '''Returns the uncertainty of an uncertain quantity.
     This free function allows multiple uncertain quantity types to be supported
     in a generic way.'''
  try:
    return x.uncertainty
  except AttributeError:
    try:
      return x.error
    except AttributeError:
      return 0

def upper( x ):
  '''Returns the upper extreme of an uncertain quantity.
     This free function allows multiple uncertain quantity types to be supported
     in a generic way.'''
  try:
    return x.upper
  except:
    try:
      return x.value + x.error
    except:
      return x

def lower( x ):
  '''Returns the lower extreme of an uncertain quantity.
     This free function allows multiple uncertain quantity types to be supported
     in a generic way.'''
  try:
    return x.lower
  except:
    try:
      return x.value - x.error
    except:
      return x






class ErrorPropagator(object):
  def __init__(self, func = None):
    self.func = func
    self.return_all_uncertainties = False

  def total_uncertainty( self, uncs, corr = None ):
    '''Compute and return the total uncertainty from individual uncertainty contributions.  '''

    if corr is None:
      return sum( [x*x for x in uncs] )**0.5

    if isinstance( corr, bool ) and corr:
      return sum( uncs )

    tot = 0
    N = len(uncs)
    for i in range(N):
      for j in range(N):
        tot += corr(i,j) * uncs[i] * uncs[j]
    return tot**0.5


  def __call__(self, *args, **kargs):
    return self.propagate_errors(self.func, *args, **kargs)

  def propagate_errors(self, func, *args, **kargs):
    '''Propagates error through a function returning the nominal value, total uncertainty (ignoring correlation)
       and (optionally) each uncertainty component. If correlations are needed, call __propagate_errors__
       instead and use the total_uncertainty method to calculate the total uncertainty with correlation.'''
    nominal_value, uncertainties = self.__propagate_errors__( func, *args, **kargs )
    uncertainty = self.total_uncertainty( list(uncertainties.values()) )

    if self.return_all_uncertainties:
      return ( nominal_value, uncertainty, uncertainties)
    else:
      return ( nominal_value, uncertainty )

class PositiveIntervalPropagator( ErrorPropagator ):
  '''A simple, yet powerful, error propagation method
     that evaluates the function at the nominal
     and upper extreme value for each argument.'''

  def __init__(self, *args, **kargs):
    super( PositiveIntervalPropagator, self ).__init__( *args, **kargs )

  def __propagate_errors__(self, func, *args, **kargs):
    # get nominal values for each argument
    nominal_args = []
    for i,a in enumerate(args):
      nominal_args.append( nominal(a) )

    nominal_kargs = dict()
    for k,v in list(kargs.items()):
      nominal_kargs[k] = nominal( v )

    # calculate the nominal value of the function
    nominal_value = func(*nominal_args,**nominal_kargs)



    # calculate the uncertainties
    uncertainties = dict()

    # we need a copy of the nominal args/kargs so we can
    # adjust one arg/karg at a time.
    evalargs  = copy.copy(nominal_args )
    evalkargs = copy.copy(nominal_kargs)

    for i in range(len(args)):
      evalargs[i]      = upper( args[i] )
      uncertainties[i] = func(*evalargs,**nominal_kargs) - nominal_value
      evalargs[i]      = nominal_args[i]

    for i in kargs:
      evalkargs[i]     = upper( kargs[i] )
      uncertainties[i] = func(*nominal_args,**evalkargs) - nominal_value
      evalkargs[i]     = nominal_kargs[i]


    return (nominal_value, uncertainties)


def WithError(func):
  propagator = PositiveIntervalPropagator()

  def wrapper(f,*args,**kwargs):
    propagator.func = f
    return propagator(*args,**kwargs)

  return decorate(func,wrapper)

