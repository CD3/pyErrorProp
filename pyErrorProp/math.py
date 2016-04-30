from __future__ import absolute_import
import math
from .UncertaintyConvension import UC

add_quantity_support = UR.wraps
add_uncertainquantity_support = 

# add unit support to math functions
sin  = UR.wraps( UR(""), UR("radian") )(math.sin)
cos  = UR.wraps( UR(""), UR("radian") )(math.cos)
tan  = UR.wraps( UR(""), UR("radian") )(math.tan)
asin = UR.wraps( UR("radian"), UR("") )(math.asin)
acos = UR.wraps( UR("radian"), UR("") )(math.acos)
atan = UR.wraps( UR("radian"), UR("") )(math.atan)
def sqrt(q):
  return q**(0.5)
