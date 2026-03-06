#########################################################################################
##
##                     International Standard Atmosphere Block
##
#########################################################################################

# IMPORTS ===============================================================================

from pathsim.blocks import Function
import math
from collections import namedtuple

# BLOCKS ================================================================================

class ISAtmosphere(Function):
    """International Standard Atmosphere.

    For a given geometric altitude and temperature deviation from standard day, 
    compute the pressure, density, temperature, and speed of sound.

    See - https://seanmcleod70.github.io/FlightDynamicsCalcs/InternationalStandardAtmosphere.html
    """

    input_port_labels = {
        "altitude": 0,
        "temp_deviation": 1
    }

    output_port_labels = {
        "pressure": 0,
        "density": 1,
        "temperature": 2,
        "speed_of_sound": 3
    }

    def __init__(self):
        super().__init__(func=self._eval)

    # Constants
    R = 287.0528    # Specific gas constant
    g0 = 9.80665    # Gravitational acceleration 
    gamma = 1.4     # Air specific heat ratio
    r0 = 6356766    # Earth radius

    StdSL_pressure = 101325         # Pa
    StdSL_speed_of_sound = 340.294  # m/s

    # Atmosphere bands
    AtmosphereBand = namedtuple('AtmosphereBand', ['start_alt', 'end_alt', 
                                                   'base_temperature', 'base_pressure',
                                                   'lapse_rate'])
    
    atmosphere_bands = [
        AtmosphereBand(0,     11000, 288.15, 101325,    -0.0065),
        AtmosphereBand(11000, 20000, 216.65, 22632,     0.0),
        AtmosphereBand(20000, 32000, 216.65, 5474.9,    0.001),
        AtmosphereBand(32000, 47000, 228.65, 868.02,    0.0028),
        AtmosphereBand(47000, 51000, 270.65, 110.91,    0.0),
        AtmosphereBand(51000, 71000, 270.65, 66.939,    -0.0028),
        AtmosphereBand(71000, 84852, 214.65, 3.9564,    -0.002),
        ]

    def _eval(self, geometric_altitude, delta_temp=0):
        geopot_altitude = self.geopotential_altitude(geometric_altitude)
        band_data = self.get_atmosphere_band(geopot_altitude)
        
        dh = geopot_altitude - band_data.start_alt
        lapse_rate = band_data.lapse_rate
        
        temp = 0
        pressure = 0
        density = 0
        speed_of_sound = 0

        if lapse_rate != 0.0:
            temp = band_data.base_temperature + lapse_rate * dh
            pressure = band_data.base_pressure * math.pow(temp/band_data.base_temperature, -self.g0/(lapse_rate * self.R))
        else:
            temp = band_data.base_temperature
            pressure = band_data.base_pressure * math.exp((-self.g0 * dh)/(self.R * temp))

        density = pressure/(self.R * (temp + delta_temp))
        speed_of_sound = math.sqrt(self.gamma * self.R * (temp + delta_temp))

        return (pressure, density, temp + delta_temp, speed_of_sound)

    def geopotential_altitude(self, geometric_altitude):
        return (geometric_altitude * self.r0)/(self.r0 + geometric_altitude)
    
    def geometric_altitude(self, geopotential_altitude):
        return (self.r0 * geopotential_altitude)/(self.r0 - geopotential_altitude)

    def get_atmosphere_band(self, geopot_altitude):
        for band in self.atmosphere_bands:
            if geopot_altitude >= band.start_alt and geopot_altitude <= band.end_alt:
                return band
        raise IndexError('Altitude out of range')


