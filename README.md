#pyErrorProp

`pyErrorProp` is a python module that performs various calculations with uncertain quantities, including error propagation.
The module uses `pint` to provide full support for physical quantities. 

**Features**
- Unit support
  - An uncertaint quantity is a nominal quantity with an associated uncertain quantity. Both the nominal and uncertain quantities are
    stored as `pint` quantities, so all unit conversions supported by `pint` can be performed on the nominal and uncertainty quantities.
  - Nominal and uncertainty quantities can be given in different (compatible) units. You define your uncertain quantities in whatever units are convienent.
- Uncertainty calculations
  - The underlying numeric types can be stored as `decimal.Decimal`, which allows precise, reproducable, rounding rules to be implemented.
- Error propagation
  - A simple function decorator syntax is used to enable error propagation through arbitrary, user-defined function.
  - Error propagation through basic math operations ( addition, subtraction, multiplication, etc) is handled automatically.
  - Uncertainty aware versions of several math functions (sin, cos, tan, etc) are provided to allow automatic error propagation through calculations using these functions.
  - Uncertain quantities are separate from error propagation. Error propagation is implemented through a callback method that can easily be modfied or replaced.

**Comparison to `pint.Measurement`**
`pint` already has support for uncertainty calculations via the `uncertainties` module. The `pint.Measurement` class is basically a wrapper around `uncertainties.ufloat` similar to a `pint.Quantity`
that uses `uncertainties.ufloat` as its magnitude type.

