"""Module defining a BetaPERT distribution"""

import scipy.stats
import numpy as np
import pandas as pd

from .fair_exception import FairException


class FairBetaPert(object):
    r"""A PERT distribution for all your pseudoscientific needs.

    FAIR often uses PERT or BetaPERT distributions in order to model skewed
    data that must exist between a fixed lower and upper bound. Because a
    BetaPert distribution a specific type of Beta distribution, it is
    possible to precompute the appropriate BetaPert parameters, and then
    simply create a Beta distribution using those parameters.

    This curve is generated upon instantiation, and random variates are
    then generated by the random_variates() function.

    Parameters
    ----------
    low : float or int
        Lower bound for the distribution below which no values will fall
    mode : float or int
        The most common value in the distribution
    high : float or int
        Higher bound for the distribution above which no values will fall
    gamma : float or int, optional
        A BetaPERT parameter for narrowing peak, default is 4

    Notes
    -----
    `PERT distributions <https://en.wikipedia.org/wiki/PERT_distribution>`_
    are a subset of `Beta distributions
    <https://en.wikipedia.org/wiki/Beta_distribution>`_ that are often used
    in FAIR analysis for a variety of reasons. Scipy has the ability to
    create four parameter beta distributions (alpha, beta, low, and range),
    but it requires that these parameters be constructed in advance. The
    pupose of this clsas is to provide a simplified interface for doing so.
    These parameters can be derived as follows:

    .. math::

        \alpha 
        =
        \frac
            {\text{mean} - \text{low}}
            {\text{high} - \text{low}}
        \times
        \left\{
            (\text{mean} - \text{low})
            \times
            \frac
                {\text{high} - \text{mean}}
                {\text{stdev}^2}
            - 1
        \right\}

    .. math::

        \beta
        =
        \alpha
        \times
        \frac
            {\text{high} - \text{mean}}
            {\text{mean} - \text{low}}

    Where:

    .. math::

        \text{mean}
        =
        \frac
            {\text{low} + \text{gamma} \times \text{mode} + \text{high}}
            {\text{gamma} + 2}

    .. math::

        \text{stdev}
        =
        \frac
            {\text{high} - \text{low}}
            {\text{gamma} + 2}

    And where:

    1) :math:`\text{low}` is the lower bound supplied for the PERT
       distribution; 
    2) :math:`\text{mode}` is the most likely value for the distriubtion;
    3) :math:`\text{high}` is the upper bound supplied for the PERT
       distribution;
    4) :math:`\text{gamma}` is the shape parameter for the distibution;
       and,
    5) :math:`\text{range}` is simply :math:`\text{high} - \text{low}`.

    References
    ----------
    .. [1] Vose, D. (2000) Risk Analysis: A Quantitative Guide. 2nd
           Edition, John Wiley & Sons, Chichester.

    .. [2] Buchsbaum, Paulo. (2012). Modified Pert Simulation.

    .. [3] Malcolm, D., Roseboom, J., Clark, C., & Fazar, W. (1959).
           Application of a Technique for Research and Development Program
           Evaluation. Operations Research, 7(5), 646-669.

    .. [4] Devleesschauwer, Brecht. (2015). prvalence: Tools for Prevalence
           Assessment Studies. R package version v0.4.0.

    .. note:: Though this class is created in contemplation of using the
              class methods attached, it is possible to obtain the raw
              scipy beta distribution itself via the self._beta_curve
              attribute.

    """
    def __init__(self, low, mode, high, gamma=4):
        # Populate object with inputs
        self._low   = low
        self._mode  = mode
        self._high  = high
        self._gamma = gamma
        self._range = high - low
        # Run sanity check
        self._run_range_check()
        # Run mean, alpha, and beta calcs in sequence.
        self._mean  = self._generate_mean()
        self._stdev = self._generate_stdev()
        self._alpha = self._generate_alpha()
        self._beta  = self._generate_beta()
        # Generate curve
        self._beta_curve = scipy.stats.beta(
            self._alpha, 
            self._beta, 
            self._low,
            self._range,
        )

    def _run_range_check(self):
        """Ensures that the distribution range is greater than 0

        Raises
        ------
        FairException
            When low input is not less than high

        """
        if self._range <= 0:
            raise FairException('"low" value must be less than "high" value.')

    def _generate_mean(self):
        """Generate mean for beta distribution"""
        return (
            (self._low + self._gamma * self._mode + self._high)
            /
            (self._gamma + 2)
        )

    def _generate_stdev(self):
        """Generate standard deviation"""
        return (
            (self._high - self._low)
            /
            (self._gamma + 2)
        )

    def _generate_alpha(self):
        """Generate alpha parameter for beta distrubtions"""
        group_1 = (self._mean - self._low) / (self._high - self._low)
        group_2 = ((self._mean - self._low) * (self._high - self._mean)
                  / 
                  (self._stdev ** 2)
        )
        return group_1 * (group_2 - 1)

    def _generate_beta(self):
        """Generate beta parameter for beta distribution"""
        beta_numerator = self._alpha * (self._high - self._mean)
        beta_denominator = self._mean - self._low
        return beta_numerator / beta_denominator

    def random_variates(self, count):
        """Get n PERT-distributed random numbers

        This works by simpling calling the rvs() function of the beta curve
        that is stored at self._beta_curve.

        Parameters
        ----------
        count : int
            The number of random variates that are required to be created

        Returns
        -------
        np.array
            An array of PERT-distributed random variates of size `count`
        
        """
        return self._beta_curve.rvs(count)
