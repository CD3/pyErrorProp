import operator

class _UncertainQuantity(object):
  '''A quantity with uncertainty.'''

  def __init__( self, nom, unc, unit = ''):
    if not isinstance( nom, self.Quantity ):
      nom = self.Quantity( nom, unit )

    if not isinstance( unc, self.Quantity ):
      nom = self.Quantity( unc, unit )
      
    self._nom = nom
    self._unc = unc

    self._unit = self._nom.units

  def make(self,*args,**kwargs):
    '''Create an instance of the class, using the uncertainty convension if necessary.'''
    try:
      return self._CONVENTION.UncertainQuantity(*args,**kwargs)
    except:
      return _UncertainQuantity(*args,**kwargs)


  @property
  def nominal(self):
    return self._nom.to(self._unit)
  value = nominal

  @property
  def uncertainty(self):
    return self._unc.to(self._unit)
  error = uncertainty

  @property
  def upper(self):
    return self.nominal + self.uncertainty

  @property
  def lower(self):
    return self.nominal - self.uncertainty

  @property
  def interval(self):
    return 2*self.uncertainty



  def __repr__(self):
      return "<UncertainQauntity({0:.2f}, {1:.2f}, {2})>".format(self._nom.to(self._unit).magnitude,
                                                                 self._unc.to(self._unit).magnitude,
                                                                 self._unit)

  def to(self,unit):
    return self.make( self._nom.to(unit), self._unc.to(unit) )

  def ito(self,unit):
    self._nom.ito(unit)
    self._unc.ito(unit)
    self._unit = self._nom.units

  def __neg__(self):
    return self.make( -self._nom, self._unc )

  def __add__(self,other):
    return self._CONVENTION.propagate_error( operator.__add__, (self,other) )

  __radd__ = __add__

  def __sub__(self,other):
    return self._CONVENTION.propagate_error( operator.__sub__, (self,other) )

  def __rsub__(self,other):
    return -self.__sub__(other)

  def __mul__(self,other):
    return self._CONVENTION.propagate_error( operator.__mul__, (self,other) )

  def __rmul__(self,other):
    return self._CONVENTION.propagate_error( operator.__mul__, (other,self) )

  def __div__(self,other):
    return self._CONVENTION.propagate_error( operator.__div__, (self,other) )

  def __rdiv__(self,other):
    return self._CONVENTION.propagate_error( operator.__div__, (other,self) )








# def get_sigfig_decimal_pos( v, n ):
  # '''Determine the decimal position of the n'th significant figure'''
  # # The simplest way to identify significant figures is to represent
  # # a number in scientific notation.
  # #
  # # examples:
  # #
  # # num       sci nota    1st sf    2nd sf
  # #
  # # 1.234  -> 1.234e+0 ->   0     -> +1
  # # 12.34  -> 1.234e+1 ->  -1     ->  0
  # # 0.1234 -> 1.234e-1 ->  +1     -> +2

  # fmt = '{:.0e}'
  # coeff,expo = fmt.format( float(v) ).split( 'e' )

  # return -int(expo) + n - 1

# def sigfig_round( v, n = 2, u = None ):
  # '''Round a number or quantity to given number of significant figures.
  
  # params:
    # v    the value to round.
    # n    the number of significant figures to round to.
    # u    an uncertainty to round to.
    
    # if an uncertainty is given, it is rounded to n significant figures and the value v
    # is rounded to the same decimal postion as the result.
    
    # Notes:

    # If v is a measurment, its uncertainty is used for u.
    # '''

  # if n < 1:
    # return v

  # # need to check for Measurement class first because a Measurement is a Quantity
  # if isinstance( v, pint.measurement._Measurement):
    # nom = nominal(v)
    # unc = uncertainty(v)
    # nom,unc = sigfig_round(nom,n,unc)
    # return UQ_( nom,unc )

  # if isinstance( v, pint.quantity._Quantity ):
    # unit  = v.units
    # value = v.magnitude
    # unc   = u.to(unit).magnitude if not u is None else None
    # return Q_( sigfig_round(value,n,unc), unit )


  # if not u is None:
    # # An uncertainty was given, and we want to round this
    # # uncertainty to the specified number of significant figures
    # # and then round the value to the same decimal position.
    # nd = get_sigfig_decimal_pos( u,n )
    # return type(v)( round(float(v), nd ) ), type(u)( round(float(u), nd ) )



  # # get the decimal position of the n'th sigfig and round
  # nd = get_sigfig_decimal_pos( v,n )
  # return type(v)( round(float(v), nd ) )





# def make_UQ( nom, unc ):
  # '''Create an uncertain quantity from two quantities'''
  # if isinstance( nom, pint.quantity._Quantity ):
    # u   = nom.units
    # nom = nom.magnitude
    # if isinstance( unc, pint.quantity._Quantity ):
      # # check if uncertainty is a delta unit
      # if len(unc._get_delta_units()) > 0:
        # # unc is a delta unit, check that it is the correct
        # # unit for nom
        # if unc._has_compatible_delta(str(u)):
          # # it is. convert it to an absolute unit
          # unc = Q_(0,u) + unc
      # unc = unc.to(u).magnitude
    # else:
      # # TODO: check nom for non-multiplicable units (temperature)
      # unc = nom*unc
      
    # return UQ_(nom, unc, u)
    
  # return UQ_(nom,unc)


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


