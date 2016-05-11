Package: fullpage

~TexRaw
\newcommand{\nom}[1]{\bar{#1}}
\newcommand{\unc}[1]{\Delta{#1}}
\newcommand{\uq}[1]{\nom{#1} \pm \unc{#1}}
\newcommand{\upp}[1]{\nom{#1} + \unc{#1}}
\newcommand{\low}[1]{\nom{#1} - \unc{#1}}
\newcommand{\ex}[1]{\langle #1 \rangle}
\newcommand{\avg}[1]{\frac{1}{N} \sum_i^N #1}
~

# Background

"Error propagation" refers to the task of determining the uncertainty (or error) in a quantity that is calculated from one or more quantities with uncertainty. For example, given two quantities
with uncertainty, $x$ and $y$, what is the uncertainty in the product $xy$? In general, if we have $z = f(x,y)$, we want to determine the uncertainty in $z$. The most common definition used
for the uncertainty in a quantity is the standard deviation[^stddev]:
$$
  \sigma_x = \sqrt{ \ex{ (x - \nom{x})^2 } } = \unc{x}
$$

So, if we have an uncertain quantity $x = \uq{x}$ and a calculation $z = f(x)$, the uncertainty in $z$ is defined as
$$
  \unc{z} = \sqrt{ \ex{ (z - \nom{z})^2 } }.
$$

If $x$ is the result of multiple measurements, ${x_i}$, then we could simple calculate $\unc{z}$ directly,
~Equation {#gendefs;}
\begin{aligned}
  \nom{z} &= \avg{ f(x_i) },\\
  \unc{z} &= \sqrt{ \avg{ (f(x_i) - \nom{z})^2 } }.
\end{aligned}
~
This would give the standard error of the mean for $z$ based on the measured data. However, if $x$ is a random variable described by a probability distribution, then the expectation values should
be evaluated in the limit $N \rightarrow \infty$. And even if we have ${x_i}$ measurements, $x$ can be considered a random variable that we have approximated using sample statistics.

There are two commonly used methods for determining the uncertainty in a calculation involving uncertain quantities. The most common method is based on a first-order approximation to the function $f$.
The Taylor Series expansion of $f$ about $\nom{x}$ is:
$$
f(x) = f(\nom{x}) + f^{\prime}(\nom{x})(x - \nom{x}) + \mathcal{O}( (x-\nom{x})^2)
$$
With this approximation, the expectation values for $z$ can be evaluated
~Equation {#1stodefs;}
\begin{aligned}
  \nom{z} &= \ex{ f(x) } \approx f(\nom{x}), \\
  \unc{z} &= \sqrt{ \ex{ (f(x) - \nom{z})^2 } } \approx \sqrt{ \ex{ \left( f^\prime(\nom{x}) (x - \nom{x}) \right)^2 } } } = \sqrt{ (f^{\prime}(\nom{x}) \unc{x})^2 } = | f^{\prime}(\nom{x}) \unc{x} |. \\
\end{aligned}
~
This method is of course an approximation, but it in most cases it is sufficient because the uncertainty $\unc{x}$ should be small if $x$ is supposed to be a measurement (if it isn't, then our measurement isn't very good).
There are known issues with this method, for example the uncertainty in $\sin(x)$ is zero if $\nom{x} = n\pi/2$ and it may not be possible to compute the derivatives of $f(x)$, but it is clearly the "standard" method.

The other most common method for calculating $\unc{z}$ is based on Monte Carlo. Values for $x$ are drawn from its distribution and used to calculate multiple values of $z$ which are then used to calculate the average and standard
deviation. While this method is more accurate (it works for arbitrary, non-linear functions), it is also more time consuming and may not be feasible.

Other methods for error propagation based on the Taylor Series expansion of the function $f$ exist (all you have to do is keep more terms), but they are much less common because they require higher moments of $x$ to be known, which
is often not the case.

If $f$ is a function of two variables, $x$ and $y$, then the Taylor Series expansion of the function truncated to first order can still be used and the nominal value for $z$ is a straight forward generalization of Equation [#1stodefs].
However, since $\unc{z}$ is the expected value of $z - \nom{z}$ squared, it will contain cross terms of $x$ and $y$. The formulas are:
~Equation {#1sto2ddefs;}
\begin{aligned}
  \nom{z} &= \ex{ f(x,y) } \approx f(\nom{x},\nom{y}), \\
  \unc{z} &= \sqrt{ \ex{ (f(x,y) - \nom{z})^2 } } \approx \sqrt{ (f^{\prime}_x(\nom{x},\nom{y}) \unc{x})^2 + (f^{\prime}_y(\nom{x},\nom{y}) \unc{y})^2 + 2f^{\prime}_{x}(\nom{x},\nom{y})f^{\prime}_{y}(\nom{x},\nom{y})\sigma_{x,y} }. \\
\end{aligned}
~
where $f^\prime_x$ and $f^\prime_y$ indicate the partial derivatives of $f$. The $\sigma_{x,y}$ in the cross term is called covariance, and is defined as the expectation value of the product of the $x$ and $y$ deviations:
$$
\sigma_{x,y} = \ex{ (x-\nom{x})(y-\nom{y}) }.
$$
the *correlation* is defined as the covariance normalized to $\unc{x}\unc{y}$:
~Equation {#correlation;}
r_{x,y} = \frac{ \ex{ (x-\nom{x})(y-\nom{y}) } }{\unc{x}\unc{y}}.
~
The two quantities, $x$ and $y$ are said to be *uncorrelated* if their deviations are independent of each other. In this case, positive and negative deviations in both $x$ and $y$ happen at random, and on average will all cancel
such that $\sigma_{x,y}$ (and $r_{x,y}$) will be zero.


# Numerical Method

The method implemented by this module differs slightly from the first-order method. Rather than computing the derivatives of $f(x)$ at $\nom{x}$, we simply evaluate $f(x)$ at $\nom{x}$ and $\unc{x}$ and take the difference:
$$
\begin{aligned}
  \nom{z} &\approx f(\nom{x}), \\
  \unc{z} &\approx f(\upp{x}) - \nom{x}.
\end{aligned}
$$
This has the advantage of being very simple, and can be performed by hand if needed. In fact, that is the original motivation for this module. I needed to determine the uncertainty in a calculation so that I could check the uncertainty
calculated by students in a physic laboratory class. This method makes intuitive sense (we just want to see how much different our answer would be if $x$ increased by its uncertainty), but it is not without justification. The first-order
error propagation method is based on the approximation
$$
f(x) = f(\nom{x}) + f^{\prime}(\nom{x})(x - \nom{x}).
$$
Rewriting $x$ here as $\upp{x}$ gives
$$
\begin{aligned}
f(\upp{x}) &= f(\nom{x}) + f^{\prime}(\nom{x})\unc{x} \\
f^{\prime}(\nom{x})\unc{x} &= f(\upp{x}) - f(\nom{x})
\end{aligned}
$$
So, to first-order, our calculation agrees with the derivative based method.

We can do the same for functions of two (or more) quantities, but we must take care of correlations. Using the first-order approximation, we can show that
$$
\begin{aligned}
f^{\prime}_x(\nom{x},\nom{y})\unc{x} = f(\upp{x},\nom{y}) - f(\nom{x},\nom{y})\\
f^{\prime}_y(\nom{x},\nom{y})\unc{y} = f(\nom{x},\upp{y}) - f(\nom{x},\nom{y})
\end{aligned}
$$
Now, let $\unc{z}_x$ and $\unc{z}_y$ be the uncertainties in $z$ caused by the uncertainty in $x$ and $y$ separately,
$$
\begin{aligned}
\unc{z}_{x} &= f^{\prime}_x(\nom{x},\nom{y})\unc{x} =  f(\upp{x},\nom{y}) - f(\nom{x},\nom{y})\\
\unc{z}_{y} &= f^{\prime}_y(\nom{x},\nom{y})\unc{y} =  f(\nom{x},\upp{y}) - f(\nom{x},\nom{y})
\end{aligned}
$$
Then the total uncertainty $\unc{z}$ can be written as (from Equation [#1sto2ddefs]):

$$
\begin{aligned}
\unc{z} = \sqrt{ \unc{z}_{x}^2 + \unc{z}_{y}^2 + 2\unc{z}_{x}\unc{z}_{y} r_{x,y}
\end{aligned}
$$
If the correlation coefficient is negative, it is possible for the total uncertainty in $z$ to be zero.

[^stddev]: The uncertainty in experimental measurements is commonly taken to be the standard error in the mean. Since standard error is the standard deviation of the sampling distribution, all of the calculations involving the standard deviation will also apply to standard error.


# Correlations

When a calculation involves more than one uncertain quantity, then correlations between the quantities in the calculation must be considered. In simple experiments (like those performed in an undergraduate physics lab), the
quantities measured in the experiment are not correlated and correlations involving the measurements can safely ignore correlation. **However**, if a series of calculations are performed with the measurements, then the results
of these calculations *will* be correlated, and additional calculations that involve the result *cannot* ignore correlation. Basically, if you have a set of uncorrelated measurements and you do not want to deal with correlation,
then you must evaluate the uncertainty of all of your calculations directly from the uncertainty of the measurements. The following example illustrates this.


## Determining the Correlation Coefficients

The correlation between two measurements can be directly calculated from Equation [#correlation], it is the average of the product of their deviations. However, if we perform a calculation that involves a measured quantity, then
the result of the calculation will be correlated to the measurement and we must take this into account if other calculations involving the result are done.

We first consider the one dimensional case, $z = f(x)$. The correlation coefficient $r_{z,x}$ is defined as
$$
r_{z,x} = \frac{ \ex{ (z-\nom{z})(x-\nom{x}) } }{\unc{z}\unc{x}}.
$$
Replacing $z$ with its first order approximation gives
$$
\ex{ (z-\nom{z})(x-\nom{x})}  = \ex{ f^{\prime}(\nom{x})(x-\nom{x})(x-\nom{x}) } = f^{\prime}(\nom{x})\ex{ (x-\nom{x})^2 } = f^{\prime}(\nom{x})\unc{x}^2
$$
Recall that $\unc{z} = |f^{\prime}(\nom{x})\unc{x}|$, so the correlation coefficient can be written as 
$$
r_{z,x} = \frac{ \pm\unc{z} \unc{x} }{\unc{z}\unc{x}} = \pm 1.
$$
So, the correlation coefficient for $z$ and $x$ will be plus or minus 1, depending on the sign of the derivative $f^{\prime}$. If the derivative is positive, then the correlation will be positive. This
indicates that $x$ and $z$ are directly correlated, which makes since if $z$ is directly calculated from $x$.

If $z$ is a function of two (or more) quantities, then we need to determine the correlation coefficient between $z$ and each of the quantities it depends on. The procedure is generally the same.
Let $z = f(x,y)$. Then, to first order, we can write
$$
f(x,y) = f(\nom{x},\nom{y})
      +  f^{\prime}_x(\nom{x},\nom{y}) (x-\nom{x})
      +  f^{\prime}_y(\nom{x},\nom{y}) (y-\nom{y})
$$
With this, the covariance of $z$ and $x$ is 
$$
\begin{aligned}
\ex{(z-\nom{z})(x-\nom{x})} &= \ex{ (f^{\prime}_x(\nom{x},\nom{y}) (x-\nom{x}) +  f^{\prime}_y(\nom{x},\nom{y}) (y-\nom{y}))(x - \nom{x}) } \\
                            &= \ex{ (f^{\prime}_x(\nom{x},\nom{y}) (x-\nom{x})(x - \nom{x} )} + \ex{ f^{\prime}_y(\nom{x},\nom{y}) (y-\nom{y}))(x - \nom{x}) } \\
                            &= (f^{\prime}_x(\nom{x},\nom{y}) \ex{ (x-\nom{x})^2} +  f^{\prime}_y(\nom{x},\nom{y})\ex{ (y-\nom{y}))(x - \nom{x}) } \\
                            &= f^{\prime}_x(\nom{x},\nom{y}) \unc{x}^2 + f^{\prime}_y(\nom{x},\nom{y})\sigma_{y,x}
\end{aligned}
$$
And the correlation coefficient is (recall that $\unc{z}_x = f^{\prime}_x(\nom{x},\nom{y}) \unc{x}$)
$$
\begin{aligned}
r_{z,x} &= \frac{f^{\prime}_x(\nom{x},\nom{y}) \unc{x}^2}{\unc{z}\unc{x}} + \frac{f^{\prime}_y(\nom{x},\nom{y})\sigma_{y,x}}{\unc{z}\unc{x}} \\
        &= \frac{\unc{z}_x\unc{x}}{\unc{z}\unc{x}} + \frac{f^{\prime}_y(\nom{x},\nom{y})\unc{y}\sigma_{y,x}}{\unc{z}\unc{y}\unc{x}}  \\
        &= \frac{\unc{z}_x\unc{x}}{\unc{z}\unc{x}} + \frac{\unc{z}_y\sigma_{y,x}}{\unc{z}\unc{y}\unc{x}}  \\
        &= \frac{\unc{z}_x}{\unc{z}} + \frac{\unc{z}_y\sigma_{y,x}}{\unc{z}\unc{y}\unc{x}}  \\
        &= \frac{\unc{z}_x}{\unc{z}} + \frac{\unc{z}_y}{\unc{z}}r_{y,x} 
\end{aligned}
$$
The correlation between $z$ and $y$ is obtained in the same way
$$
r_{z,y} = \frac{\unc{z}_y}{\unc{z}} + \frac{\unc{z}_x}{\unc{z}}r_{x,y}.
$$
So, the correlation between $z$ and the quantities it is calculated from depends on the correlation between the quantities themselves. If all quantities are uncorrelated, then
$z$ will be correlated to each. However, if two or more quantities are correlated, then $z$ could be uncorrelated with them.

It is possible for the uncertainty in $z$ to be zero if $x$ and $y$ are correlated, in which case the denominator will be zero. We need to handle this case seprately.
$$
r_{z,x} &= \frac{\unc{z}_x + \unc{z}_y r_{y,x}}{\unc{z}}
        &= \frac{\unc{z}_x + \unc{z}_y r_{y,x}}{\sqrt{ \unc{z}_{x}^2 + \unc{z}_{y}^2 + 2\unc{z}_{x}\unc{z}_{y} r_{x,y} } }
$$
There the denominator will be zero if $-2\unc{z}_x\unc{z}_yr_{x,y} = \unc{z}_x^2 + \unc{z}_x^2$. This will
$$
r_{z,x} &= \frac{\unc{z}_x - \unc{z}_y }{\sqrt{ \unc{z}_{x}^2 + \unc{z}_{y}^2 - 2\unc{z}_{x}\unc{z}_{y} } }.
$$

# Summary

In general, assume we have a calculation we need to perform that is a function of several uncertain quantities:
$$
z = f(x,y,w,\ldots)
$$
The nominal value for $z$ is
$$
\nom{z} = f(\nom{x},\nom{y},\nom{w},\ldots)
$$
The individual uncertainties are
$$
\begin{aligned}
\unc{z}_x &= f(\upp{x},\nom{y},\nom{w},\ldots) - \nom{z} \\
\unc{z}_y &= f(\nom{x},\upp{y},\nom{w},\ldots) - \nom{z} \\
\unc{z}_w &= f(\nom{x},\nom{y},\upp{w},\ldots) - \nom{z} \\
\ldots
\end{aligned}
$$
The total uncertainty is
$$
\unc{z} &= \sqrt{ \unc{z}_x^2 + 2\unc{x}\unc{y}\;r_{x,y} + \unc{z}_y^2 + 2\unc{y}\unc{w}\;r_{y,w} + \unc{z}_w^2 + \ldots}.
$$
The quantity $z$ will be correlated to the inputs of $f$. The correlation coefficients are
$$
\begin{aligned}
r_{z,x} &= \frac{\unc{z}_x}{\unc{z}}
         + \frac{\unc{z}_y}{\unc{z}}r_{y,x}
         + \frac{\unc{z}_w}{\unc{z}}r_{w,x}
         + \ldots \\
r_{z,y} &= \frac{\unc{z}_x}{\unc{z}}r_{x,y}
         + \frac{\unc{z}_y}{\unc{z}}
         + \frac{\unc{z}_w}{\unc{z}}r_{w,y}
         + \ldots \\
r_{z,w} &= \frac{\unc{z}_x}{\unc{z}}r_{x,w}
         + \frac{\unc{z}_y}{\unc{z}}r_{y,w}
         + \frac{\unc{z}_w}{\unc{z}}
         + \ldots \\
\ldots
\end{aligned}
$$
If the input quantities are not correlated, then the total uncertainty will simplify
$$
\unc{z} &= \sqrt{ \unc{z}_x^2 + \unc{z}_y^2 + \unc{z}_w^2 + \ldots}
$$
as will the correlations
$$
\begin{aligned}
r_{z,x} &= \frac{\unc{z}_x}{\unc{z}} \\
r_{z,y} &= \frac{\unc{z}_y}{\unc{z}} \\
r_{z,w} &= \frac{\unc{z}_w}{\unc{z}} \\
\ldots
\end{aligned}
$$
