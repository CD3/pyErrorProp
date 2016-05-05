import operator, re, decimal
import pint

ureg = pint.UnitRegistry()

class _UncertainQuantity(object):
  '''A quantity with uncertainty.'''

  _REGISTRY = ureg
  Quantity = _REGISTRY.Quantity

  def __init__( self, nom, unc = None, unit = None, corr = None):

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

    # make sure units on unc and nom are compatible
    try:
      tmp = nom + unc
    except Exception as e:
      e.extra_msg = " Nominal value and uncertainty do not have compatible types."
      raise e

      
    self._nom = nom
    self._unc = unc
    self._corr = corr

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


  def correlated( self, var, corr = None, return_None = True, bidirectional = True ):
    '''Get/set the correlation between another variable.'''

    # only support correlation between UncertainQuantity instances
    if not isinstance( var, _UncertainQuantity ):
      return 0.0

    if self._corr == None:
      self._corr = {}

    key = id(var)

    if corr is None:
      if self is var:
        return 1

      return self._corr.get( key, None if return_None else 0 )

    self._corr[key] = corr

    if bidirectional:
      var.correlated(self,corr,bidirectional=False)


  def __repr__(self):
      return "<UncertainQauntity({0:.2f}, {1:.2f}, {2})>".format(self._nom.to(self._unit).magnitude,
                                                                 self._unc.to(self._unit).magnitude,
                                                                 self._unit)

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
    prec -= 1
    if prec < 0:
      prec = 0

    # Rounding based on sigfigs is a little tricky. None of the builtin rounding
    # functions round based on sigfigs. The simplest way to round to a given sigfig
    # is to get a scientific representation of the number, then the first digit displayed
    # is significant. If we want to display the number in fixed decimal representation, then
    # we have to figure out what precision (places after decimal) corresponds to the given
    # significant figure.
    # 
    # Rather than handle all of this manually, we'll use the Decimal class.
    nom = decimal.Decimal( self.nominal.magnitude )
    unc = decimal.Decimal( self.uncertainty.magnitude )
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
      nomu = nomt[1]

    uncv = unc
    uncu = ''
    unct = unc.split()
    if len(unct)>1:
      uncv = unct[0]
      uncu = unct[1]

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




  def to(self,unit):
    return self.make( self._nom.to(unit), self._unc.to(unit) )

  def ito(self,unit):
    self._nom.ito(unit)
    self._unc.ito(unit)
    self._unit = self._nom.units

  def __neg__(self):
    return self.make( -self._nom, self._unc )

  def __add__(self,other):
    return self._CONVENTION.__propagate_error__( operator.__add__, (self,other) )

  __radd__ = __add__

  def __sub__(self,other):
    return self._CONVENTION.__propagate_error__( operator.__sub__, (self,other) )

  def __rsub__(self,other):
    return -self.__sub__(other)

  def __mul__(self,other):
    return self._CONVENTION.__propagate_error__( operator.__mul__, (self,other) )

  def __rmul__(self,other):
    return self._CONVENTION.__propagate_error__( operator.__mul__, (other,self) )

  def __div__(self,other):
    return self._CONVENTION.__propagate_error__( operator.__div__, (self,other) )

  def __rdiv__(self,other):
    return self._CONVENTION.__propagate_error__( operator.__div__, (other,self) )

  def __eq__(self,other):
    return self._CONVENTION.__eq__( self, other )

  def __req__(self,other):
    return self._CONVENTION.__eq__( self, other )

  def __lt__(self,other):
    return self._CONVENTION.__lt__( self, other )

  def __gt__(self,other):
    return self._CONVENTION.__gt__( self, other )

