import math, decimal, copy

#########
# utils 
#########

def get_sigfig_decimal_pos( v, n ):
  '''Determine the decimal position of the n'th significant figure'''
  # The simplest way to identify significant figures is to represent
  # a number in scientific notation.
  #
  # examples:
  #
  # num       sci nota    1st sf    2nd sf
  #
  # 1.234  -> 1.234e+0 ->   0     -> +1
  # 12.34  -> 1.234e+1 ->  -1     ->  0
  # 0.1234 -> 1.234e-1 ->  +1     -> +2

  fmt = '{:.0e}'
  coeff,expo = fmt.format( float(v) ).split( 'e' )

  return -int(expo) + n - 1

def sigfig_round( v, n = 2 ):
  '''Round a number or quantity to given number of significant figures.
  
  params:
    v    the value to round.
    n    the number of significant figures to round to.
  '''

  if n < 1:
    return v

  # if v is a Quantity, we want to round the magnitude
  try:
    vv = copy.deepcopy(v)
    vv._magnitude = sigfig_round(vv._magnitude,n)
    return vv
  except:
    pass

  nd = get_sigfig_decimal_pos( v,n )

  # handle Decimal type special so we don't lose any digits
  if isinstance( v, decimal.Decimal ):
    return (v*10**nd).quantize(decimal.Decimal('1')) / 10**nd

  # get the decimal position of the n'th sigfig and round
  return type(v)(round(v*10**nd))/type(v)(10**nd)





# def make_sigfig_UQ( nom, sigfigs ):
  # '''Create an uncertaint quantity from a quantity and number of sigfigs. The
  # uncertain quantity will have an error that corresponds to the last
  # significant figure plus or minus 1.'''
  # nom = nominal( nom )
  # # round to correct number of sigfigs
  # val = sigfig_round( nom, sigfigs )
  # # get sigfig decimal postion
  # pos = get_sigfig_decimal_pos( magof(nom), sigfigs )
  # # the uncertainty is the last significant figure plus-or-minus 1
  # unc = Q_(pow(10,-pos),unitsof(nom))

  # return UQ_(val, unc)

# def get_UQ( data, sigfigs = 2 ):
  # '''Computes an uncertain quantity from a data set (computes the standard error)'''
  # nominal = numpy.mean( data )
  # std_dev = numpy.std( data )
  # std_err = std_dev / numpy.sqrt( len( data ) )

  # q = make_UQ( nominal, std_err )
  # if sigfigs > 0:
    # q = sigfig_round( q, sigfigs )
  # return q
# calc_UQ = get_UQ

# make_UQ_ = make_UQ  # for the sake of consistency
# get_UQ_ = get_UQ

# def sort_uncertainties(u):
  # '''Sorts a list of uncertainties from largest to smallest'''
  # if isinstance( u, dict ) or isinstance( u, collections.OrderedDict ):
    # return collections.OrderedDict( sorted( u.items() , reverse = True, key = lambda it : numpy.abs( it[1] ) ) )

  # return u



