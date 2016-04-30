from pint import UnitRegistry
from ErrorPropagator import PositiveIntervalPropagator

UR = UnitRegistry()
EP = PositiveIntervalPropagator

class UncertaintyConvention(object):

  def __init__(self):
    self._UNITREGISTRY = UR
    self.UncertainQuantity = build_uncertainquantity_class(self, self._UNITREGISTRY)
    self.Quantity = self.UncertainQuantity.Quantity
    self.ErrorPropagator = EP()

    # we need to modify the quantity magic functions to return NotImplemented on
    # errors so that the UncertainQuantity __r* methods can take over.
    def disable_exceptions(f):
      def new_f(self,other):
        try:
          return f(self, other)
        except:
          return NotImplemented

      return new_f

    self.Quantity.__add__ = disable_exceptions( self.Quantity.__add__ )

  def propagate_error(self, f, args, kwargs = {}):
    '''Propagates error through a function.'''
    self.ErrorPropagator.func = f

    r = self.ErrorPropagator( *args, **kwargs )

    self.ErrorPropagator.func = None

    return self.UncertainQuantity(*r)

  def round( self, uq ):
    '''Round an uncertain quantity.'''
    return uq



def build_uncertainquantity_class(conv, ureg):
  from .UncertainQuantity import _UncertainQuantity

  class UncertainQuantity(_UncertainQuantity):
      pass

  UncertainQuantity._CONVENTION = conv
  UncertainQuantity.Quantity    = ureg.Quantity
  
  return UncertainQuantity
