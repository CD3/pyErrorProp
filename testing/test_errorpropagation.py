from pyErrorProp import UncertaintyConvention

uconv = UncertaintyConvention()
UQ_ = uconv.UncertainQuantity
Q_  = UQ_.Quantity

def Close( a, b, tol = 0.01 ):
    if isinstance(a,int):
        a = float(a)
    if isinstance(b,int):
        b = float(b)
    return (a - b)**2 / (a**2 + b**2) < 4*tol*tol


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
