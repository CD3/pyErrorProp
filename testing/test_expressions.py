from pyErrorProp.Expressions import *


def test_basics():
  e = Expression(10)
  assert e.eval() == 10

  e = PlusExpression(10,20)
  assert e.eval() == 30

  ee = PlusExpression(30,e)
  assert ee.eval() == 60


