import math, decimal, copy








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

  # if v is an int, we need to make it a float
  if isinstance( v, int ):
    v = float(v)

  # get the decimal position of the n'th sigfig and round
  return type(v)(round(v*10**nd))/type(v)(10**nd)

def isuncertain(v):
  if hasattr( v, 'uncertainty' ):
    return True
  
  if hasattr( v, 'error' ):
    return True

  if hasattr( v, 'std_dev' ):
    return True

  return False

def magof(q):
  try:
    return q.magnitude
  except:
    return q

def unitsof(q):
  try:
    return q.units
  except:
    return ""



