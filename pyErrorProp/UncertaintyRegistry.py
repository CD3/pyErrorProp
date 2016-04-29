from pint import UnitRegistry

UR = UnitRegistry()

class UncertaintyRegistry(object):

  def __init__(self):

    self._UNITREGISTRY = UR
    self.UncertainQuantity = build_uncertainquantity_class(self, self._UNITREGISTRY)
    self.Quantity = self.UncertainQuantity.Quantity


def build_uncertainquantity_class(reg, ureg):
  from .UncertainQuantity import _UncertainQuantity

  class UncertainQuantity(_UncertainQuantity):
      pass

  UncertainQuantity._REGISTRY = reg
  UncertainQuantity.Quantity  = ureg.Quantity


  
  return UncertainQuantity
