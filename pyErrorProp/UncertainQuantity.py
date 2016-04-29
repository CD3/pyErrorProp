
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

  # Error Propagation
  def __propagate_error__( self, f, x ):
    nom = f(x.nominal)
    upp = f(x.upper)
    unc = upp - nom

    return UncertainQuantity(nom,unc)


