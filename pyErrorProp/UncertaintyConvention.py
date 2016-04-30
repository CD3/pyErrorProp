import pint
from pint import UnitRegistry
from ErrorPropagator import PositiveIntervalPropagator

UR = UnitRegistry()
EP = PositiveIntervalPropagator

class UncertaintyConvention(object):

  def __init__(self):
    self._UNITREGISTRY = UR
    self.UncertainQuantity = build_uncertainquantity_class(self, self._UNITREGISTRY)
    self.ErrorPropagator = EP()

    # we need to modify the quantity magic functions to return NotImplemented if
    # the other type is an uncertain quantity so that the UncertainQuantity __r* methods can take over.
    UQ_ = self.UncertainQuantity
    def disable_for_UQ(f):
      def new_f(self,other):
        if type(other) is UQ_:
          return NotImplemented
        return f(self, other)

      return new_f

    self.UncertainQuantity.Quantity.__add__ = disable_for_UQ( self.UncertainQuantity.Quantity.__add__ )
    self.UncertainQuantity.Quantity.__sub__ = disable_for_UQ( self.UncertainQuantity.Quantity.__sub__ )
    self.UncertainQuantity.Quantity.__mul__ = disable_for_UQ( self.UncertainQuantity.Quantity.__mul__ )
    self.UncertainQuantity.Quantity.__div__ = disable_for_UQ( self.UncertainQuantity.Quantity.__div__ )

  def __propagate_error__(self, f, args, kwargs = {}):
    '''Propagates error through a function.'''
    self.ErrorPropagator.func = f

    r = self.ErrorPropagator( *args, **kwargs )

    self.ErrorPropagator.func = None

    return self.UncertainQuantity(*r)

  def __round__( self, uq ):
    '''Round an uncertain quantity.'''
    return uq



def build_uncertainquantity_class(conv, ureg):
  from .UncertainQuantity import _UncertainQuantity

  class UncertainQuantity(_UncertainQuantity):
      pass

  UncertainQuantity._CONVENTION = conv
  UncertainQuantity.Quantity    = ureg.Quantity
  
  return UncertainQuantity
