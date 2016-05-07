from pyErrorProp import UncertaintyConvention
from Utils import *

uconv = UncertaintyConvention()
UQ_ = uconv.UncertainQuantity
Q_  = UQ_.Quantity


def test_addition():
  nx = Q_(1.5,'m')
  dx = Q_(1,'cm')
  x = UQ_( nx, dx )

  ny = Q_(3.3,'m')
  dy = Q_(2,'cm')
  y = UQ_( ny, dy )

  # check that two uncertain quantities can be added
  z = x + y
  assert Close( z.nominal, nx + ny, 0.001 )
  assert Close( z.uncertainty, (dx**2 + dy**2)**0.5, 0.001 )

  # check that a quantity can be added to an uncertain quantity
  z = x + ny
  assert Close( z.nominal, nx + ny, 0.001 )
  assert Close( z.uncertainty, dx, 0.001 )

  # check that an uncertain quantity can be added to a quantity
  z = nx + y
  assert Close( z.nominal, nx + ny, 0.001 )
  assert Close( z.uncertainty, dy, 0.001 )

def test_subtraction():
  nx = Q_(1.5,'m')
  dx = Q_(1,'cm')
  x = UQ_( nx, dx )

  ny = Q_(3.3,'m')
  dy = Q_(2,'cm')
  y = UQ_( ny, dy )

  # check that two uncertain quantities can be subtracted
  z = x - y
  assert Close( z.nominal, nx - ny, 0.001 )
  assert Close( z.uncertainty, (dx**2 + dy**2)**0.5, 0.001 )

  # check that a quantity can be subtracted from an uncertain quantity
  z = x - ny
  assert Close( z.nominal, nx - ny, 0.001 )
  assert Close( z.uncertainty, dx, 0.001 )

  # check that an uncertain quantity can be subtracted from a quantity
  z = nx - y
  assert Close( z.nominal, nx - ny, 0.001 )
  assert Close( z.uncertainty, dy, 0.001 )

def test_multiplication():
  nx = Q_(1.5,'m')
  dx = Q_(1,'cm')
  x = UQ_( nx, dx )

  ny = Q_(3.3,'m')
  dy = Q_(2,'cm')
  y = UQ_( ny, dy )

  # check that two uncertain quantities can be multiplied
  z = x * y
  assert Close( z.nominal, nx * ny, 0.001 )
  assert Close( z.uncertainty, ((ny*dx)**2 + (nx*dy)**2)**0.5, 0.001 )

  # check that an uncertain quantity can be multiplied by a quantity
  z = x * ny
  assert Close( z.nominal, nx * ny, 0.001 )
  assert Close( z.uncertainty, ny*dx, 0.001 )

  # check that a quantity can be multiplied by an uncertain quantity
  z = nx * y
  assert Close( z.nominal, nx * ny, 0.001 )
  assert Close( z.uncertainty, nx*dy, 0.001 )


  # multiplication by a number should also work
  z = 2 * x
  assert Close( z.nominal, 2*nx, 0.001 )
  assert Close( z.uncertainty, dx*2, 0.001 )

  z = x * 2
  assert Close( z.nominal, 2*nx, 0.001 )
  assert Close( z.uncertainty, dx*2, 0.001 )

  z = 1.5 * x
  assert Close( z.nominal, 1.5*nx, 0.001 )
  assert Close( z.uncertainty, dx*1.5, 0.001 )

  z = x * 1.5
  assert Close( z.nominal, 1.5*nx, 0.001 )
  assert Close( z.uncertainty, dx*1.5, 0.001 )

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

  # check that two uncertain quantities can be divided
  z = x / y
  assert Close( z.nominal, nz,  0.001 )
  assert Close( z.uncertainty, (dzx**2 + dzy**2)**0.5, 0.001 )

  # check that an uncertain quantity can be divided by a quantity
  z = x / ny
  assert Close( z.nominal, nz, 0.001 )
  assert Close( z.uncertainty, abs(dzx), 0.001 )

  # check that a quantity can be subtracted from an uncertain quantity
  z = nx / y
  assert Close( z.nominal, nz, 0.001 )
  assert Close( z.uncertainty, abs(dzy), 0.001 )


  # division by a number should also work
  z = 2 / x
  dz = 2/(nx+dx) - 2/nx
  assert Close( z.nominal, 2/nx, 0.001 )
  assert Close( z.uncertainty, abs(dz), 0.001 )

  z = x / 2
  dz = (nx+dx)/2 - nx/2
  assert Close( z.nominal, nx/2, 0.001 )
  assert Close( z.uncertainty, abs(dz), 0.001 )

  z = 1.5 / x
  dz = 1.5/(nx+dx) - 1.5/nx
  assert Close( z.nominal, 1.5/nx, 0.001 )
  assert Close( z.uncertainty, abs(dz), 0.001 )

  z = x / 1.5
  dz = (nx+dx)/1.5 - nx/1.5
  assert Close( z.nominal, nx/1.5, 0.001 )
  assert Close( z.uncertainty, abs(dz), 0.001 )

def test_sum():
  data = [ UQ_( 1, 0.1, 'm' )
         , UQ_( 2, 0.2, 'm' )
         , UQ_( 3, 0.3, 'm' )
         ]

  x = sum( data )

  assert Close( x.nominal.magnitude    , 6 )
  assert Close( x.uncertainty.magnitude, (0.1**2 + 0.2**2 + 0.3**2)**0.5 )


  data = [ UQ_( 1, 0.1, 'm' )
         , -UQ_( 2, 0.2, 'm' )
         , UQ_( 3, 0.3, 'm' )
         ]

  x = sum( data )

  assert Close( x.nominal.magnitude    , 2 )
  assert Close( x.uncertainty.magnitude, (0.1**2 + 0.2**2 + 0.3**2)**0.5 )

def test_correlation():
  x = UQ_( '2.5 +/- 0.5 m' )
  y = UQ_( '2.5 +/- 0.5 m' )
  w = x

  # make x and y directly correlated
  x.correlated(y,1.0)

  # check that correlated vals reduce uncertainty
  z = x - y

  assert z.nominal.magnitude == 0
  assert z.uncertainty.magnitude == 0

  # make sure that a variable is correlated to itself
  z = x - x

  assert z.nominal.magnitude == 0
  assert z.uncertainty.magnitude == 0

  # and references to itself
  z = x - w

  assert z.nominal.magnitude == 0
  assert z.uncertainty.magnitude == 0


  w = -x
  z = x+w
  assert z.nominal.magnitude == 0
  assert z.uncertainty.magnitude == 0


def test_sum():
  nx = Q_(1.5,'m')
  dx = Q_(1,'cm')
  x = UQ_( nx, dx )

  ny = Q_(3.3,'m')
  dy = Q_(2,'cm')
  y = UQ_( ny, dy )

  z = sum([x,y])
  zz = x+y
  assert Close( z.nominal, nx + ny, 0.001 )
  assert Close( z.uncertainty, (dx**2 + dy**2)**0.5, 0.001 )
  assert Close( z.nominal, zz.nominal, 0.001 )
  assert Close( z.uncertainty, zz.uncertainty, 0.001 )

  z = sum([x,x])
  zz = x + x
  assert Close( z.nominal, zz.nominal, 0.001 )
  assert Close( z.uncertainty, zz.uncertainty, 0.001 )

  z = sum( [ UQ_('2 +/- 0.1 m') ] * 10 )
  assert Close( z.nominal.magnitude, 20, 1e-5 )
  assert Close( z.uncertainty.magnitude, 1, 0.001 )
