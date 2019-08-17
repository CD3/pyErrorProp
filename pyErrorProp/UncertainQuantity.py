from __future__ import division
import operator, re, decimal, copy, sys
import pint

from .unicode import *


ureg = pint.UnitRegistry()

class _UncertainQuantity(object):
  '''A quantity with uncertainty.'''

  _REGISTRY = ureg
  Quantity = _REGISTRY.Quantity
  Decimal = decimal.Decimal

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

  def __round__(self,n=None):
    return self._CONVENTION.__round__(self,n)

  def normalize(self,n=None):
    '''Normalized the uncertain quantatiy in place with an uncertainty
       rounded to the requested number of significant figures, and
       the nominal value rounded to the same decimal position as the
       uncertainty.'''

    # __round__ already does what we need, we just need to do it in place.
    tmp = self.__round__(n)
    self._nom = tmp._nom
    self._unc = tmp._unc

    return self

    

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

    template = "<UncertainQuantity({0}, {1}, {2})>" 

    nom_s = str(nom)
    unc_s = str(unc)

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
    # The __round__ function already does this. It uses the Decimal type internally, but converts
    # back to the actual type used for storing the nominal and uncertainty values. So, if
    # we just create an uncertain quantity that uses Decimal and round it, we will have
    # what we need.
    #
    #
    # Pint already handles formatting of units (and does a nice job), so we just need to format the value portion.
    # 

    # split the format spec into its value specific and unit specific parts
    v_fmtspec = fmtspec.replace('Lx','')
    v_fmtspec = pint.formatting.remove_custom_flags(v_fmtspec)
    u_fmtspec = fmtspec.replace(v_fmtspec,'')


    # get number of sigfigs requested
    psre = re.compile(r'\.([0-9]+)')
    match = psre.search( v_fmtspec )
    nsig = None
    if match:
      nsig = match.group(1)
      nsig = int(nsig)
      if nsig < 0:
        nsig = 0

    # now we can remove the precision spec
    v_fmtspec = psre.sub( r'', v_fmtspec )

    # create an uncertain quantity that uses Decimal for storate and round
    units = self.nominal.units
    nom = self.Quantity( decimal.Decimal(str(self.nominal.magnitude)), units )
    unc = self.Quantity( decimal.Decimal(str(self.error.to(units).magnitude)), units )
    uq = self.make( nom, unc ).__round__(nsig)

    # now get the nominal and uncertainty values
    nom = uq.nominal.magnitude
    unc = uq.error.magnitude

    # Use pint to create a template string with the units already formatted
    # by creating a quantity with a string replacement (%s) as a magnitude.
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
    nom = re.sub(r'\s+',' ',nom.strip())
    unc = re.sub(r'\s+',' ',unc.strip())

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
    return self._CONVENTION.__propagate_errors__( operator.__sub__, (0,self) )

  def __abs__(self):
    if self.nominal.magnitude >= 0:
      return self._CONVENTION.__propagate_errors__( operator.__add__, (0,self) )
    else:
      return self._CONVENTION.__propagate_errors__( operator.__sub__, (0,self) )

  def __add__(self,other):
    return self._CONVENTION.__propagate_errors__( operator.__add__, (self,other) )

  __radd__ = __add__

  def __sub__(self,other):
    return self._CONVENTION.__propagate_errors__( operator.__sub__, (self,other) )

  def __rsub__(self,other):
    return self._CONVENTION.__propagate_errors__( operator.__sub__, (other,self) )
    return -self.__sub__(other)

  def __mul__(self,other):
    return self._CONVENTION.__propagate_errors__( operator.__mul__, (self,other) )

  def __rmul__(self,other):
    return self._CONVENTION.__propagate_errors__( operator.__mul__, (other,self) )

  def __truediv__(self,other):
    return self._CONVENTION.__propagate_errors__( operator.__truediv__, (self,other) )

  def __rtruediv__(self,other):
    return self._CONVENTION.__propagate_errors__( operator.__truediv__, (other,self) )

  def __div__(self,other):
    return self._CONVENTION.__propagate_errors__( operator.__div__, (self,other) )

  def __rdiv__(self,other):
    return self._CONVENTION.__propagate_errors__( operator.__div__, (other,self) )


  def __pow__(self,other):
    return self._CONVENTION.__propagate_errors__( operator.__pow__, (self,other) )



  def consistent(self,other):
    return self._CONVENTION.consistent( self, other )

  def __lt__(self,other):
    return self._CONVENTION.__lt__( self, other )

  def __gt__(self,other):
    return self._CONVENTION.__gt__( self, other )

