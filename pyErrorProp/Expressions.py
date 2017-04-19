import UncertainQuantity

class Expression(object):
  def __init__(self,var):
    self.v = var

  def eval(self):
    return self.v

  def nominal(self):
    if isinstance(self.v,UncertainQuantity._UncertainQuantity):
      return self.v.nominal()
    return self.v

  def error(self):
    if isinstance(self.v,UncertainQuantity._UncertainQuantity):
      return self.v.error()
    return self.v

class PlusExpression(Expression):
  def __init__(self, lhs, rhs):
    if not isinstance(lhs,Expression):
      lhs = Expression(lhs)
    if not isinstance(rhs,Expression):
      rhs = Expression(rhs)
    self.lhs = lhs
    self.rhs = rhs

  def eval(self):
    return self.lhs.eval() + self.rhs.eval()
