
def Close( a, b, tol = 0.01 ):
    return (a - b)**2 <= 4*tol*tol*(a**2 + b**2)

