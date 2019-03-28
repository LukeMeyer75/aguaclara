from aguaclara.core.units import unit_registry as u
import numpy as np
import pandas as pd
import os

# pump rotor radius based on minimizing error between predicted and measured
# values
R_pump = 1.62 * u.cm
# empirically derived correction factor due to the fact that larger diameter
# tubing has more loss due to space smashed by rollers
k_nonlinear = 13


def vol_per_rev_3_stop(color="", inner_diameter=0):
    """Return the volume per revolution of an Ismatec 6 roller pump
    given the inner diameter (ID) of 3-stop tubing. The calculation is
    empirically derived from the table found at
    http://www.ismatec.com/int_e/pumps/t_mini_s_ms_ca/tubing_msca2.htm.

    Note: either input a string as the tubing color code or a number as the
    tubing inner diameter. If both are given, the function will default to using
    the color.

    :param color: Color code of the Ismatec 3-stop tubing
    :type color: string
    :param inner_diameter: Inner diameter of the Ismatec 3-stop tubing
    :type inner_diameter: float

    :return: Volume per revolution output by a 6-roller pump through the 3-stop tubing (mL/rev)
    :rtype: float

    :Examples:

    >>> from aguaclara.research.peristaltic_pump import vol_per_rev_3_stop
    vol_per_rev(2.79*u.mm)
    0.4005495805189351 milliliter/rev
    >>> vol_per_rev(1.52*u.mm)
    0.14884596727278446 milliliter/rev
    >>> vol_per_rev(0.51*u.mm)
    0.01943899117521222 milliliter/rev
    """
    if color != "":
        inner_diameter = ID_colored_tube(color)
    term1 = (R_pump * 2 * np.pi - k_nonlinear * inner_diameter) / u.rev
    term2 = np.pi * (inner_diameter ** 2) / 4
    return (term1 * term2).to(u.mL/u.rev)


def ID_colored_tube(color):
    """Look up the inner diameter of Ismatec 3-stop tubing given its color code.

    :param color: Color of the 3-stop tubing
    :type color: string

    :returns: Inner diameter of the 3-stop tubing (mm)
    :rtype: float

    :Examples:

    >>> from aguaclara.research.peristaltic_pump import ID_colored_tube
    ID_colored_tube("yellow-blue")
    1.52 millimeter
    >>> ID_colored_tube("orange-yellow")
    0.51 millimeter
    >>> ID_colored_tube("purple-white")
    2.79 millimeter
    """
    tubing_data_path = os.path.join(os.path.dirname(__file__), "data",
        "3_stop_tubing.txt")
    df = pd.read_csv(tubing_data_path, delimiter='\t')
    idx = df["Color"] == color
    return df[idx]['Diameter (mm)'].values[0] * u.mm


def vol_per_rev_LS(id_number):
    """Look up the volume per revolution output by a Masterflex L/S pump
    through L/S tubing of the given ID number.

    :param id_number: Identification number of the L/S tubing, between 13 and 18
    :type id_number: int

    :return: Volume per revolution output by a Masterflex L/S pump through the L/S tubing
    :rtype: float

    :Examples:

    >>> from aguaclara.research.peristaltic_pump import vol_per_rev_LS
    vol_per_rev_LS(13)
    <Quantity(0.06, 'milliliter / turn')>
    """
    tubing_data_path = os.path.join(os.path.dirname(__file__), "data",
        "LS_tubing.txt")
    df = pd.read_csv(tubing_data_path, delimiter='\t')
    idx = df["Number"] == id_number
    return df[idx]['Flow (mL/rev)'].values[0] * u.mL/u.rev


def flow_rate(vol_per_rev, rpm):
    """Return the flow rate from a pump given the volume of fluid pumped per
    revolution and the desired pump speed.

    :param vol_per_rev: Volume of fluid output per revolution (dependent on pump and tubing)
    :type vol_per_rev: float
    :param rpm: Desired pump speed in revolutions per minute
    :type rpm: float

    :return: Flow rate of the pump (mL/s)
    :rtype: float

    :Examples:

    >>> from aguaclara.research.peristaltic_pump from flow_rate
    flow_rate(3*u.mL/u.rev, 5*u.rev/u.min)
    <Quantity(0.25, 'milliliter / second')>
    """
    return (vol_per_rev * rpm).to(u.mL/u.s)
