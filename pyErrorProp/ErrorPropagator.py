import CorrelationMatrix as CM
import copy


# utility functions

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
      return sum( [x*x for x in uncs.values()] )**0.5

    if isinstance( corr, bool ) and corr:
      return sum( uncs.values() )

    tot = 0
    N = len(uncs)
    for i in range(N):
      for j in range(N):
        tot += corr(i,j) * uncs[i] * uncs[j]
    return tot**0.5


  def __call__(self, *args, **kargs):
    return self.propagate_uncertainties(self.func, *args, **kargs)

  def propagate_uncertainties(self, func, *args, **kargs):
    nominal_value, uncertainties = self.__propagate_uncertainties__( func, *args, **kargs )

    # build the correlation matrix
    corr = CM.CorrelationMatrix( )
    for k in uncertainties.keys():
      if k in kargs:
        corr.queue(kargs[k])
      else:
        corr.queue(args[k])
    corr.make()

    uncertainty = self.total_uncertainty( uncertainties.values(), corr )
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

  def __propagate_uncertainties__(self, func, *args, **kargs):

    # get nominal values for each argument
    nominal_args = []
    for i,a in enumerate(args):
      nominal_args.append( nominal(a) )

    nominal_kargs = dict()
    for k,v in kargs.items():
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


# class AutoErrorPropagator( PositiveIntervalPropagator ):
  # '''An error propagator that automatically propagates error based on a given number of significant figures. For example,
     # by default the propagator determines the uncertainy in the result by assuming all input parameters
     # have 3 significant figures and the last significant figure is uncertain by plus/minus 1.'''
  # def __init__(self, sigfigs = 3, *args, **kargs):
    # self.sigfigs = sigfigs
    # super( AutoErrorPropagator, self ).__init__( *args, **kargs )

  # def __propagate_uncertainties__(self, func, *args, **kargs):
    # new_args = []
    # for i,a in enumerate(args):
      # if not isinstance( a, pint.measurement._Measurement ):
        # a = make_sigfig_UQ( a, self.sigfigs )
      # new_args.append( a )

    # new_kargs = dict()
    # for k,v in kargs.items():
      # if not isinstance( v, pint.measurement._Measurement ):
        # v = make_sigfig_UQ( v, self.sigfigs )
      # new_kargs[k] = v

    # value,uncertainties = super( AutoErrorPropagator, self).__propagate_uncertainties__( *new_args, **new_kargs )

    # return value, uncertainties

def WithError(func):
  propagator = PositiveIntervalPropagator()
  propagator.func = func
  return propagator

# def WithUncertainties(func):
  # propagator = PositiveIntervalPropagator()
  # propagator.func = func
  # propagator.set_return_uncertainties(True)
  # return propagator

# def WithAutoError(sigfigs=3):
  # propagator = AutoErrorPropagator()
  # propagator.sigfigs = sigfigs

  # def Decorator(func):
    # propagator.func = func
    # return propagator

  # return Decorator

# def WithErrorPropagator(propagator=None):
  # if propagator is None:
    # return WithError

  # def Decorator(func):
    # propagator.func = func
    # return propagator

  # return Decorator





