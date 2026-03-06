#########################################################################################
##
##                     Airspeed conversion Blocks
##
#########################################################################################

# IMPORTS ===============================================================================

from pathsim.blocks import Function
from ..atmosphere import ISAtmosphere
import math

# BLOCKS ================================================================================

class CAStoMach(Function):
    """Convert calibrated airspeed (CAS) to Mach value.
    CAS in m/s altitude in m.
    """

    input_port_labels = {
        "cas": 0,
        "altitude": 1
    }

    output_port_labels = {
        "mach": 0
    }

    def __init__(self):
        super().__init__(func=self._eval)

    def _eval(self, cas, altitude):
        """Convert Calibrated airspeed to Mach value.

        Assume m/s for cas and m for altitude.

        Based on the formulas in the US Air Force Aircraft Performance Flight
        Testing Manual (AFFTC-TIH-99-01), in particular sections 4.6 to 4.8.

        The subsonic and supersonic Mach number equations are used with the simple
        substitutions of (Vc/asl) for M and Psl for P. However, the condition for
        which the equations are used is no longer subsonic (M < 1) or supersonic
        (M > 1) but rather calibrated airspeed being less or greater than the
        speed of sound ( asl ), standard day, sea level (661.48 knots).
        """
        ISA = ISAtmosphere()

        pressure, _, _, _ = ISA._eval(altitude)

        if cas < ISAtmosphere.StdSL_speed_of_sound:
            # Bernoulli's compressible equation (4.11)
            qc = ISAtmosphere.StdSL_pressure * (
                math.pow(1 + 0.2 * math.pow(cas / ISAtmosphere.StdSL_speed_of_sound, 2), 3.5) - 1
            )
        else:
            # Rayleigh's supersonic pitot equation (4.16)
            qc = ISAtmosphere.StdSL_pressure * (
                (
                    (166.9215801 * math.pow(cas / ISAtmosphere.StdSL_speed_of_sound, 7))
                    / math.pow(7 * math.pow(cas / ISAtmosphere.StdSL_speed_of_sound, 2) - 1, 2.5)
                )
                - 1
            )

        # Solving for M in equation (4.11), also used as initial condition for supersonic case
        mach = math.sqrt(5 * (math.pow(qc / pressure + 1, 2 / 7) - 1))

        if mach > 1:
            # Iterate equation (4.22) since M appears on both sides of the equation
            for i in range(7):
                mach = 0.88128485 * math.sqrt((qc / pressure + 1) * math.pow(1 - 1 / (7 * mach * mach), 2.5))

        return mach


class CAStoTAS(Function):
    """Convert calibrated airspeed (CAS) to true airspeed (TAS). 
    CAS and TAS in m/s altitude in m.
    """

    input_port_labels = {
        "cas": 0,
        "altitude": 1
    }

    output_port_labels = {
        "tas": 0
    }

    def __init__(self):
        super().__init__(func=self._eval)

    def _eval(self, cas, altitude):
        """Assume m/s for input and output velocities and m for altitude."""

        mach = CAStoMach()._eval(cas, altitude)
        ISA = ISAtmosphere()
        _, _, _, speed_of_sound = ISA.state(altitude)
        return mach * speed_of_sound


class TAStoCAS(Function):
    """Convert true airspeed (TAS) to calibrated airspeed (CAS).
    TAS and CAS in m/s altitude in m.
    """

    input_port_labels = {
        "tas": 0,
        "altitude": 1
    }

    output_port_labels = {
        "cas": 0
    }

    def __init__(self):
        super().__init__(func=self._eval)

    def _eval(self, tas, altitude):
        """Assume m/s for input and output velocities and m for altitude."""

        ISA = ISAtmosphere()
        pressure, _, _, speed_of_sound = ISA.state(altitude)

        mach = tas / speed_of_sound
        qc = pressure * ( math.pow(1 + 0.2*mach**2, 7/2) - 1)
        cas = ISA.StdSL_speed_of_sound * math.sqrt( 5 * ( math.pow(qc/ISA.StdSL_pressure + 1, 2/7) - 1) ) 
        return cas


class CAStoEAS(Function):
    """Convert calibrated airspeed (CAS) to equivalent airspeed (EAS).
    CAS and EAS in m/s altitude in m.
    """

    input_port_labels = {
        "cas": 0,
        "altitude": 1
    }

    output_port_labels = {
        "eas": 0
    }

    def __init__(self):
        super().__init__(func=self._eval)

    def _eval(self, cas, altitude):
        """Assume m/s for input and output velocities and m for altitude."""
        ISA = ISAtmosphere()
        _, density, _, _ = ISA.state(altitude)
        _, rho0, _, _ = ISA.state(0)  # Standard sea level density
        eas = CAStoTAS()._eval(cas, altitude) * math.sqrt(density / rho0)
        return eas


class EAStoTAS(Function):
    """Convert equivalent airspeed (EAS) to true airspeed (TAS).
    EAS and TAS in m/s altitude in m.
    """

    input_port_labels = {
        "eas": 0,
        "altitude": 1
    }

    output_port_labels = {
        "tas": 0
    }

    def __init__(self):
        super().__init__(func=self._eval)

    def _eval(self, eas, altitude):
        """Assume m/s for input and output velocities and m for altitude."""
        ISA = ISAtmosphere()
        _, density, _, _ = ISA.state(altitude)
        _, rho0, _, _ = ISA.state(0)  # Standard sea level density
        tas = eas * math.sqrt(rho0 / density)
        return tas


class MachtoCAS(Function):
    """Convert Mach value to calibrated airspeed (CAS).
    CAS in m/s altitude in m.
    """

    input_port_labels = {
        "mach": 0,
        "altitude": 1
    }

    output_port_labels = {
        "cas": 0
    }

    def __init__(self):
        super().__init__(func=self._eval)

    def _eval(mach, altitude):
        """Assume m for altitude."""
        ISA = ISAtmosphere()
        _, _, _, speed_of_sound = ISA.state(altitude)
        return TAStoCAS()._eval(mach * speed_of_sound)

