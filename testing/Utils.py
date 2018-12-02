import decimal

def Close( a, b, tol = 0.01 ):
  if isinstance(a,(decimal.Decimal)):
    tol = decimal.Decimal(tol)
  return (a - b)**2 <= 4*tol*tol*(a**2 + b**2)


class Approx(object):
  def __init__(self,val):
    self._val = val
    self._epsilon = 0.01
  def epsilon(self,epsilon):
    self._epsilon = epsilon
    return self
  def __eq__(self,other):
    return abs(other - self._val) <= self._epsilon*abs(other + self._val)/2
  def __repr__(self):
    return "{} +/- {}%".format(self._val,self._epsilon*100)

