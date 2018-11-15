import aguaclara.core.physchem as pc
import aguaclara.design.human_access as ha
from aguaclara.core.units import unit_registry as u
from onshapepy import Part

import math


# Unused constants - START \/

FREEBOARD = 10 * u.cm

# From slope peak to weir
FLOC_BLANKET_H = 0.25 * u.m

# Distance that the rapid mix coupling extends into the first floc channel
# so that the RM orifice place can be fixed in place.
COUPLING_EXT_L = 5 * u.cm

# The minor loss coefficient is 2. According to measurements at Agalteca
# and according to
# https://confluence.cornell.edu/display/AGUACLARA/PAHO+Water+Treatment+Publications
# (page 100 in chapter on flocculation)
OPTION_H = 0

# Increased both to provide a safety margin on flocculator head loss and
# to simultaneously scale back on the actual collision potential we are
# trying to achieve.
BAFFLE_MINOR_LOSS = 2.5

BAFFLE_SET_BACK_PLASTIC_S = 2 * u.cm

# Target flocculator collision potential basis of design

BOD_GT = 75 * u.m ** (2 / 3)

# Ratio of the width of the gap between the baffle and the wall and the
# spacing between the baffles.
BAFFLE_RATIO = 1

# Max energy dissipation rate in the flocculator, basis of design.
BOD_ENERGY_DISSIPATION_MAX = 10 * u.mW / u.kg

DRAIN_TIME = 15 * u.min

MOD_ND = 0.5 * u.inch

SPACER_ND = 0.75 * u.inch

MOD_EDGE_LAST_PIPE_S = 10 * u.cm

RM_RESTRAINER_ND = 0.5 * u.inch

# Height that the drain stub extends above the top of the flocculator wall
DRAIN_STUB_EXT_H = 20 * u.cm

MOD_PIPE_EDGE_S = 10 * u.cm

BAFFLE_THICKNESS = 2 * u.mm

BAFFLE_RIGID_H_THICKNESS = 15*u.cm  # Is this a height or a thickness?

# The piping size for the main part of the floc modules
MODULES_MAIN_ND = (1/2)*u.inch

# The diameter of the oversized cap used to assemble the floc modules
MODULES_LARGE_ND = 1.5*u.inch

# Unused constants - END /\


class Flocculator:
    """Calculates physical dimensions of an AguaClara flocculator.

    Constant instance attributes
    ----------------------------
    - BAFFLE_K (K or K_baffle): float
        - The minor loss coefficient of the flocculator baffles.
    - HL (h_L_floc): float * u.cm
        - The target head loss in the flocculator.
    - GT (G-bar-Theta): float
        - The target collision potential of particles in the flocculator.
    - END_WATER_H (H): float * u.m
        - The height of water at the end of the flocculator.
    - CHANNEL_N_MIN (n_{Min, channel}): int
        - The minimum number of flocculator channels.
    - HS_RATIO_MIN (Pi_{HS}): float
        - The minimum ratio between expansion height and baffle spacing
    - HS_RATIO_MAX (Pi_{HS}): float
        - The maximum ratio between expansion height and baffle spacing
    - CAD: Part
        - URL to the flocculator 3D model in Onshape
    """

    BAFFLE_K = 2.56
    HL = 40 * u.cm
    GT = 37000
    END_WATER_H = 2 * u.m
    CHANNEL_N_MIN = 2
    HS_RATIO_MIN = 3
    HS_RATIO_MAX = 6

    CAD = Part(
        'https://cad.onshape.com/documents/b4cfd328713460beeb3125ac/w/3928b5c91bb0a0be7858d99e/e/6f2eeada21e494cebb49515f'
    )

    def __init__(self, q=20 * u.L/u.s, temp=25 * u.degC,
                 sed_tank_l_max=6 * u.m):
        """Instantiate a Flocculator object, representing a real flocculator
        component.

        :param q: Flow rate of water through the flocculator.
        :type q: float * u.L/u.s
        :param temp: Water temperature of the flocculator.
        :type temp: float * u.degC
        :param sed_tank_l_max: Maximum length of the sedimentation tank, used
        to calculate the length of the adjacent flocculator.
        :type sed_tank_l_max: float * u.m
        :returns: object
        :rtype: Flocculator
        """
        self.q = q
        self.temp = temp
        self.sed_tank_l_max = sed_tank_l_max

    @property
    def vel_grad_avg(self):
        """Calculate the average velocity gradient (G-bar) of water flowing
        through the flocculator.

        :returns: Average velocity gradient (G-bar)
        :rtype: float * 1 / second
        """
        return ((pc.gravity * self.HL) /
               (pc.nu(self.temp) * self.GT)).to(u.s ** -1)

    @property
    def retention_time(self):
        """Calculate the retention time of flocs in a flocculator.

        :returns: Retention time of flocs (:math:`\theta`)
        :rtype: float * second
        """
        return self.GT / self.vel_grad_avg

    @property
    def vol(self):
        """Calculate the target volume of the flocculator.

        :returns: Target volume
        :rtype: float * meter ** 3
        """
        return (self.q * self.retention_time).to(u.m ** 3)

    @property
    def l_max_vol(self):
        """Calculate the maximum flocculator channel length that achieves the
        target volume, while still allowing human access.

        :returns: Maximum length based off of volume
        :rtype: float * meter
        """
        return (self.vol /
               (self.CHANNEL_N_MIN * ha.HUMAN_W_MIN * self.END_WATER_H)
               ).to(u.m)

    @property
    def channel_l(self):
        """Calculate the length of the flocculator channel that allows for the
        target volume, while at the same time, allowing for human access.

        :returns: Channel length
        :rtype: float * meter
        """
        return min(self.sed_tank_l_max, self.l_max_vol)

    @property
    def w_min_hs_ratio(self):
        """Calculate the minimum flocculator channel width, given the minimum
        ratio between expansion height (H) and baffle spacing (S).

        :returns: Minimum channel width given H_e/S
        :rtype: float * centimeter
        """

        return ((self.HS_RATIO_MIN * self.q.to(u.m ** 3 / u.s) / self.END_WATER_H) *
               (self.BAFFLE_K /
               (2 * self.END_WATER_H * pc.nu(self.temp) * self.vel_grad_avg ** 2)) ** (1/3)
               ).to(u.cm)

    @property
    def w_min(self):
        """Calculate the minimum channel width required to remain within the
        H_e/S ratio range and human access requirements.

        :returns: Minimum channel width
        :rtype: float * centimeter
        """
        return max(self.w_min_hs_ratio, ha.HUMAN_W_MIN)

    @property
    def num_channel(self):
        """Return the number of channels in the entrance tank/flocculator (ETF).

        This takes the total width of the flocculator and divides it by the
        minimum channel width. A floor function is used to ensure that there
        are an even number of channels.        ?

        Examples
        --------
        num_channel(20*u.L/u.s, 40*u.cm, 37000, 25*u.degC, 20*u.m, 2*u.m)
        2

        """
        # Unimplemented
        pass

    @property
    def d_exp_max(self):
        """"Return the maximum distance between expansions for the largest
        allowable H/S ratio.

        Examples
        --------
        exp_dist_max(20*u.L/u.s, 40*u.cm, 37000, 25*u.degC, 2*u.m)
        0.375 meter
        """
        G = self.vel_grad_avg
        nu = pc.nu(self.temp)
        pi = self.HS_RATIO_MAX
        w = self.channel_w
        k = self.BAFFLE_K
        q = self.q

        return ((k / (2*nu*(G**2))) * ((q*pi/w)**3)) ** (1/4)

    @property
    def channel_w(self):
        """
        The channel width of the flocculator.  See section 'Flocculation
        Design' of textbook'
        """
        w_min_human = ha.HUMAN_W_MIN
        # just assume it's 6
        # perf_metric is (d between flow exp / baffle_spacing)
        perf_metric = 6
        w_min_perf_metric = (
            (perf_metric * self.q / self.END_WATER_H)
            * (
                    self.BAFFLE_K / (
                    2 * self.END_WATER_H
                    * pc.nu(self.temp)
                    * (self.vel_grad_avg ** 2)
                )
            ) ** (1/3)
        )

        w_min = self.w_min
        w_tot = self.vol / (self.channel_l * self.END_WATER_H)
        n_chan = w_tot / w_min
        w_chan = w_tot / n_chan
        return w_chan

    @property
    def exp_n(self):
        """Return the minimum number of expansions per baffle space."""
        return math.ceil(self.END_WATER_H / self.d_exp_max)

    @property
    def expansions_h(self):
        """Returns the height between flow expansions."""
        return self.END_WATER_H / self.exp_n

    @property
    def baffles_s(self):
        """Return the spacing between baffles.

        Examples
        --------
        baffles_s(20*u.L/u.s, 40*u.cm, 37000, 25*u.degC, 2*u.m)
        0.063 meter
        ."""
        return (
            (
                self.BAFFLE_K
                / (
                    2 * self.d_exp_max
                    * (self.vel_grad_avg ** 2)
                    * pc.nu(self.temp)
                )
            ) ** (1/3)
            * self.q / ha.HUMAN_W_MIN
        )

    @property
    def baffles_n(self):
        """Return the number of baffles a channel can contain.

        Examples
        --------
        baffles_n(20*u.L/u.s, 40*u.cm, 37000, 25*u.degC, 2*u.m, 2*u.m, 2*u.m)
        0
        baffles_n(20*u.L/u.s, 20*u.cm, 37000, 25*u.degC, 2*u.m, 2*u.m, 21*u.m)
        -1
        """
        return self.END_WATER_H / self.baffles_s - 1

    def draw(self):
        self.CAD.params = {
            'channel_l': self.channel_l,
            'channel_w': self.channel_w,
            'channel_h': self.END_WATER_H,
            'channel_pairs': self.channel_n / 2,
            'baffle_s': self.baffle_s,
        }