from pyErrorProp import ErrorPropagator, WithError
from Utils import *

import pint

ureg = pint.UnitRegistry()

Q_  = ureg.Quantity
UQ_ = ureg.Measurement


def test_addition():
  nx = Q_(1.5,'m')
  dx = Q_(1,'cm')
  x = UQ_( nx, dx )

  ny = Q_(3.3,'m')
  dy = Q_(2,'cm')
  y = UQ_( ny, dy )


  @WithError
  def add(x,y):
    return x+y

  z = UQ_(*add(x,y))

  assert Close( z.value, nx + ny, 0.001 )
  assert Close( z.error, (dx**2 + dy**2)**0.5, 0.001 )

def test_subtraction():
  nx = Q_(1.5,'m')
  dx = Q_(1,'cm')
  x = UQ_( nx, dx )

  ny = Q_(3.3,'m')
  dy = Q_(2,'cm')
  y = UQ_( ny, dy )

  @WithError
  def sub(x,y):
    return x-y

  z = UQ_(*sub(x,y))

  assert Close( z.value, nx - ny, 0.001 )
  assert Close( z.error, (dx**2 + dy**2)**0.5, 0.001 )

def test_multiplication():
  nx = Q_(1.5,'m')
  dx = Q_(1,'cm')
  x = UQ_( nx, dx )

  ny = Q_(3.3,'m')
  dy = Q_(2,'cm')
  y = UQ_( ny, dy )

  @WithError
  def mul(x,y):
    return x*y

  z = UQ_(*mul(x,y))

  assert Close( z.value, nx * ny, 0.001 )
  assert Close( z.error, ((ny*dx)**2 + (nx*dy)**2)**0.5, 0.001 )

def test_division():
  nx = Q_(1.5,'m')
  dx = Q_(1,'cm')
  x = UQ_( nx, dx )

  ny = Q_(3.3,'m')
  dy = Q_(2,'cm')
  y = UQ_( ny, dy )

  nz  = nx/ny
  dzx = (nx + dx)/ny - nx/ny
  dzy = nx/(ny+dy) - nx/ny

  @WithError
  def div(x,y):
    return x/y

  z = UQ_(*div(x,y))

  assert Close( z.value, nz,  0.001 )
  assert Close( z.error, (dzx**2 + dzy**2)**0.5, 0.001 )

def test_sum():
  x = UQ_( 2, 0.2, 'm' )

  @WithError
  def sum_(v,N):
    d = [ v ] * N
    return sum(d)

  z = UQ_(*sum_( x, 10 ))

  assert Close( z.value.magnitude, 20 )
  assert Close( z.error.magnitude, 2.0 )
