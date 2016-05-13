#pyErrorProp

`pyErrorProp` is a python module that performs various calculations with
uncertain quantities, including error propagation.  The module uses `pint` to
provide full support for physical quantities and provides a few benefits over `pint`'s
`Measurement` class.

**Motivation**

This module was created to perform error analysis calculations that we teach to students in undergraduate Physics I/II courses. Rather than have student perform derivatives (which they cannot do in the
algebra based course), we teach a method that only requires the function they are propagating
error through to be calculated. The function is first evaluated using the nominal values for all
input variables. The uncertainty in the result due to each input variable is then determined by
evaluating the same function, but using the input variable's nominal value plus its uncertainty.
The total uncertainty is then calculated by adding each individual uncertainty in quadrature.

For example, if we have a function that depends on two measured quantities that both have uncertainty,
we calculate the uncertainty in the result of the function as follows.

![alg](./doc/images/error_prop_algorithm.png)

This assumes that the input variables are uncorrelated, which is usually the
case when the input variables are measured quantities.

There are other packages that do error propagation:

- `uncertainties`(https://github.com/lebigot/uncertainties) Uses first-order error propagation..
  Derivatives of expressions are computed analytically and it handles correlation.
- `soerp`(https://github.com/tisimst/soerp) Uses second-order error propgation. 
  Derivatives of expressions are computed analytically and it handles correlation.
- `mcerp` (https://github.com/tisimst/mcerp) Uses monte-carlo method to compute distribution
  of the result of a calculation from the distributions of the inputs.

However, I needed an implementation that would
reproduce what the students would calculate by hand in order to write keys to assigned problems.



**Features**
- Unit support
  - An uncertainty quantity is a nominal quantity with an associated uncertain quantity. Both the nominal and uncertain quantities are
    stored as `pint` quantities, so all unit conversions supported by `pint` can be performed on the nominal and uncertainty quantities.
  - Nominal and uncertainty quantities can be given in different (compatible) units. You define your uncertain quantities in whatever units are convenient.
- Uncertainty calculations
  - The underlying numeric types can be stored as `decimal.Decimal`, which allows precise, reproducible, rounding rules to be implemented.
  - Two uncertain quantities can be compared (greater than or less than) with the result of the comparison being "statistically significant".
- Error propagation
  - A simple function decorator syntax is used to enable error propagation through arbitrary, user-defined function.
  - Error propagation through basic math operations ( addition, subtraction, multiplication, etc) is handled automatically.
  - Uncertainty aware versions of several math functions (sin, cos, tan, etc) are provided to allow automatic error propagation through calculations using these functions.
  - Uncertain quantities are separate from error propagation. Error propagation is implemented through a callback method that can easily be modified or replaced.

**Note on Performance** The `uncertainties` module is *much* faster that this module. 
While a slight performance hit may be expected with the addition of unit an dimensional
analysis, this is not the cause. Simple calculations with uncertain quantities
can be orders of magnitude slower with this module. This is mainly because the `uncertainties`
module does not explicitly calculate uncertainties at each step. Rather it stores information
that would be needed to calculate the uncertainties and does this at the end, when the user
asks for it. This module does calculate uncertainty for each intermediate step in a calculation.
No optimization has been done yet, so perhaps this could be improved in the future, but if you
need high performance uncertainty calculations, you should use the `uncertainties` module.

**Comparison to `pint.Measurement`**
`pint` already has support for uncertainty calculations via the `uncertainties`
module. The `pint.Measurement` class is basically a wrapper around
`uncertainties.ufloat` similar to a `pint.Quantity` that uses
`uncertainties.ufloat` as its magnitude type. This module provides error
propagation functions that will work with the `pint.Measurement` class. In
fact, it was originally written to do just that, but eventually I found a few
limitations with `pint.Measurement`.

The `pint.Measurement` class allows you to
use different types for the numeric value of a quantity, which is not possible
with `pint.Measurement`. Since the `pint.Measurement` class uses the `ufloat`
type, all uncertain quantities must be represented as floats.  It is not
possible, for example, to use the `decimal.Decimal` type to store numeric
values.  The other issue is that, since `pint.Measurement` stores a `ufloat`
and attached units to it, the units for the quantities nominal value and
uncertainty are the same. At first this doesn't appear to be much of an issue at all, except
that it would be nice to be able to specify the uncertainty of a length in centimeters
while its nominal value is given in meters. However, `pint` knows about offset units, such as
temperature, and it is not possible to add two offset units together. If you try to add
10 Celsius to 37 Celsius, you will get a unit error. So, it is not possible to add
an uncertain quantities nominal value and uncertainty. In terms of what `pint` expects,
an uncertain temperature should have a "delta" unit for its uncertainty.

This module provides an `UncertainQuantity` class that overcomes these issues. It stores
the nominal value and uncertainty as instances of `pint.Quantity`, so they can be given
in any units that support addition.
