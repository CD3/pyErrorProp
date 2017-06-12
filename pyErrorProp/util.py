import math, decimal, copy, sys








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

  # convert to decimal. note that the value might be a quantity, and we don't want the units...
  v = decimal.Decimal( str( v ).split()[0] )
  # adjust() returns the position of the first significant figure.
  # but it uses a different sign convension. sigfigs to the right
  # of the decimal are negative, sigfigs to the left are negative.
  # we want the opposite.
  i = -v.adjusted()

  # add offset for the requested sigfig
  i += n-1

  return i

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


  # get a decimal representation of the value
  dv = decimal.Decimal(str(v))

  # get the decimal position that we need to round to
  nd = get_sigfig_decimal_pos( v,n )
  # scale dv so that the last digit we want is in front of the decimal
  dv = dv.scaleb(nd)
  # now round off the decimal place
  dv = dv.quantize(0)
  # and scale it back
  dv = dv.scaleb(-nd)

  try:
    # return the rounded number, but make sure we return the same type
    # this works for any type that can be constructed from a string
    return type(v)( str(dv) )
  except:
    # some types might not be constructable from a string, so we will try
    # a float instead
    return type(v)( float(dv) )


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



