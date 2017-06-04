import operator, re, decimal, copy, sys
import pint


ureg = pint.UnitRegistry()

class _UncertainQuantity(object):
  '''A quantity with uncertainty.'''

  _REGISTRY = ureg
  Quantity = _REGISTRY.Quantity

  def __init__( self, nom, unc = None, unit = None ):
    if unc is None and unit is None and isinstance(nom,(str,unicode)):
      nom,unc = _UncertainQuantity.parse_string( nom )

    if not isinstance( nom, self.Quantity ):
      if unit is None:
        nom = self.Quantity( nom )
      else:
        nom = self.Quantity( nom, unit )

    if not isinstance( unc, self.Quantity ):
      # support for % sign in unit
      if isinstance(unc,(str,unicode)):
        unc = unc.replace('%','percent')
      if unit is None:
        unc = self.Quantity( unc )
      else:
        unc = self.Quantity( unc, unit )

    if str(unc.units) == 'percent':
      unc = nom*unc.to('')

    # handle offset units
    # uncertainties should be "delta" units
    # pint seems to automatically convert any offset units to deltas
    # for derived units, so for now we will just try to convert
    # to a delta unit if possible.
    try:
      unc = self.Quantity(unc.magnitude, self._delta(unc.units) )
    except:
      pass

    # make sure units on unc and nom are compatible
    try:
      tmp = nom + unc
    except Exception as e:
      e.extra_msg = " Nominal value and uncertainty do not have compatible types."
      raise e

      
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
    if self._is_a_delta( self._unc ):
      return self._unc.to(self._delta(self._unit))
    else:
      return self._unc.to(self._unit)
  error = uncertainty

  @property
  def relative_uncertainty(self):
    return self.uncertainty/self.nominal
  relative_error = relative_uncertainty

  @property
  def upper(self):
    return self.nominal + self.uncertainty

  @property
  def lower(self):
    return self.nominal - self.uncertainty

  @property
  def interval(self):
    return 2*self.uncertainty

  def normalize(self,n=None):
    '''Return a normalized uncertain quantatiy with an uncertainty
       rounded to the requested number of significant figures, and
       the nominal value rounded to the same decimal position as the
       uncertainty.'''

    # __format__ already does what we need, so we'll just format
    # ourself and use parse_string to get the nominal and uncertainty values.

    fmtstr = "{"
    if n is not None:
      fmtstr += ":."+str(n)
    fmtstr += "}"

    nom,unc = self.parse_string( fmtstr.format(self) )

    toks = nom.split()
    nomv = toks[0]
    nomu = " ".join(toks[1:])
    nomt = type(self._nom.magnitude)

    toks = unc.split()
    uncv = toks[0]
    uncu = "".join(toks[1:])
    unct = type(self._unc.magnitude)

    nom = self.Quantity(nomt(nomv),nomu)
    unc = self.Quantity(unct(uncv),uncu)

    q = self.make(nom,unc)

    return q

    

  def correlated( self, var, corr ):
    '''Set the correlation between another variable.'''
    self._CONVENTION._CORRREGISTRY.correlated(self,var,corr)


  def correlation( self, var, default = 0.0 ):
    '''Get the correlation between another variable.'''
    return self._CONVENTION._CORRREGISTRY.correlation(self,var,default)


  def __repr__(self):
    nom = self._nom.to(self._unit).magnitude
    if self._is_a_delta( self._unc ):
      unc = self._unc.to(self._delta(self._unit)).magnitude
    else:
      unc = self._unc.to(self._unit).magnitude

    template = "<UncertainQauntity({0}, {1}, {2})>" 
    if 'mpmath' in sys.modules:
      import mpmath
      if not isinstance(nom, mpmath.mpf):
        nom = mpmath.mpmathify(nom)
      if not isinstance(unc, mpmath.mpf):
        unc = mpmath.mpmathify(unc)

      nom_s = mpmath.nstr(nom)
      unc_s = mpmath.nstr(unc)
    else:
      nom_s = "{f}".format(nom)
      unc_s = "{f}".format(unc)

    return template.format(nom_s,unc_s,self._unit)

  def __format__(self, fmtspec):
    # see if formatting is handled by the uncertainty convention
    # so that the user can overload it if they want.
    try:
      return self._CONVENTION.__format_uncertainquantity__(self,fmtspec)
    except:
      pass


    # An uncertain quantity should be formatted so that the
    # nominal value matches the decimal position of the uncertainty (Taylor, 1997).
    #
    # In general, the uncertainty should be rounded to 1 significant figure when displayed (Taylor, 1997).
    #
    # However, if the leading significant figure is '1', two significant figures may be retained (Taylor, 1997).
    #
    # So, for an uncertain quantity, we interpret the precision spec in the format string to be the 
    # number of significant figures that should be displayed in the uncertainty, rather than the number
    # of figures after the decimal point. The nominal value's precision will set to match
    # the uncertainties.
    #
    #
    # Pint already handles formatting of units (and does a nice job), so we just need to format the value portion.
    # 

    # split the format spec into its value specific and unit specific parts
    v_fmtspec = fmtspec.replace('Lx','')
    v_fmtspec = pint.formatting.remove_custom_flags(v_fmtspec)
    u_fmtspec = fmtspec.replace(v_fmtspec,'')


    # determine the precision
    psre = re.compile('\.([0-9]+)')
    match = psre.search( v_fmtspec )
    prec_given = False
    prec = 1
    if match:
      prec_given = True
      prec = match.group(1)
    prec = int(prec)
    prec -= 1 # number of sigfigsis one more than precision.
    if prec < 0:
      prec = 0

    # Rounding based on sigfigs is a little tricky. None of the builtin rounding
    # functions round based on sigfigs. The simplest way to round to a given sigfig
    # is to get a scientific representation of the number, then the first digit displayed
    # is significant. If we want to display the number in fixed decimal representation, then
    # we have to figure out what precision (places after decimal) corresponds to the given
    # significant figure.
    # 
    # We don't want to do this manually. we'll use the Decimal module instead.
    nom = self.nominal.magnitude
    unc = self.uncertainty.magnitude
    if 'mpmath' in sys.modules:
      import mpmath
      nom = mpmath.nstr(nom)
      unc = mpmath.nstr(unc)
    nom = decimal.Decimal( nom )
    unc = decimal.Decimal( unc )
    if prec_given == False and prec == 0 and ('{:e}'.format(unc))[0] == '1':
      # special case: if leading significant figure is 1, then take two
      prec += 1
    unc = ('{:.%de}'%prec).format(unc) # a string rounded to the correct number of sigfigs
    unc = decimal.Decimal(unc)         # back to a decimal
    nom = nom.quantize(unc)
    # now we can remove the precision spec
    # precision will be handled by the Decimal class
    v_fmtspec = psre.sub( '', v_fmtspec )


    # Use pint to create a template string with the units already formatted
    # by creatign a quantity with a string replacement (%s) as a magnitude.
    tmpl = ('{:'+u_fmtspec+'}').format( self.Quantity( '%s', self._unit ) )


    # Format the value
    sepstr = ' +/- '
    if 'Lx' in u_fmtspec:
      sepstr = ' +- '

    valstr = ('{:%s}%s{:%s}'%(v_fmtspec,sepstr,v_fmtspec)).format(nom,unc)
    
    ret = tmpl % valstr

    return ret

  @staticmethod
  def parse_string(text):
    text = text.replace("+/-", "+-")
    text = text.replace("+-", "|")

    tok = text.split('|')
    nom = tok[0]
    unc = tok[1] if len(tok) > 1 else "0"

    # check for units
    nomv = nom
    nomu = ''
    nomt = nom.split()
    if len(nomt)>1:
      nomv = nomt[0]
      nomu = " ".join(nomt[1:])

    uncv = unc
    uncu = ''
    unct = unc.split()
    if len(unct)>1:
      uncv = unct[0]
      uncu = " ".join(unct[1:])

    if nomu == '':
      nomu = uncu

    if nomu == '':
      nomu = 'dimensionless'

    if uncu == '' and not unc[-1] == '%':
      uncu = 'dimensionless'


    nom = '%s %s'%(nomv,nomu)
    unc = '%s %s'%(uncv,uncu)

    # remove extra spaces
    nom = re.sub('\s+',' ',nom.strip())
    unc = re.sub('\s+',' ',unc.strip())

    return (nom,unc)


  def _delta(self,unit):
    return 'delta_'+str(unit)

  def _is_a_delta(self,q):
    return len(q._units) == 1 and str(q.units).startswith('delta_')

  def to(self,unit):
    if self._is_a_delta( self._unc ):
      return self.make( self._nom.to(unit), self._unc.to(self._delta(unit)) )
    else:
      return self.make( self._nom.to(unit), self._unc.to(unit) )

  def ito(self,unit):
    self._nom.ito(unit)
    self._unc.ito(unit)
    self._unit = self._nom.units

  def __neg__(self):
    return self._CONVENTION.__propagate_error__( operator.__sub__, (0,self) )

  def __abs__(self):
    if self.nominal.magnitude >= 0:
      return self._CONVENTION.__propagate_error__( operator.__add__, (0,self) )
    else:
      return self._CONVENTION.__propagate_error__( operator.__sub__, (0,self) )

  def __add__(self,other):
    return self._CONVENTION.__propagate_error__( operator.__add__, (self,other) )

  __radd__ = __add__

  def __sub__(self,other):
    return self._CONVENTION.__propagate_error__( operator.__sub__, (self,other) )

  def __rsub__(self,other):
    return self._CONVENTION.__propagate_error__( operator.__sub__, (other,self) )
    return -self.__sub__(other)

  def __mul__(self,other):
    return self._CONVENTION.__propagate_error__( operator.__mul__, (self,other) )

  def __rmul__(self,other):
    return self._CONVENTION.__propagate_error__( operator.__mul__, (other,self) )

  def __div__(self,other):
    return self._CONVENTION.__propagate_error__( operator.__div__, (self,other) )

  def __rdiv__(self,other):
    return self._CONVENTION.__propagate_error__( operator.__div__, (other,self) )

  def __pow__(self,other):
    return self._CONVENTION.__propagate_error__( operator.__pow__, (self,other) )



  def consistent(self,other):
    return self._CONVENTION.consistent( self, other )

  def __lt__(self,other):
    return self._CONVENTION.__lt__( self, other )

  def __gt__(self,other):
    return self._CONVENTION.__gt__( self, other )

