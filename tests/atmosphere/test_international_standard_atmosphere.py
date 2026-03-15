########################################################################################
##
##                                  TESTS FOR
##                      'atmosphere.international_standard_atmosphere.py'
##
########################################################################################

# IMPORTS ==============================================================================

import unittest
from pathsim_flight.atmosphere import ISAtmosphere

# TESTS ================================================================================

class TestISAtmosphere(unittest.TestCase):
    """Test the ISAAtmosphere block."""

    def test_standard_day_sealevel_constants(self):
        """Test standard day sea level constants"""
        isa = ISAtmosphere()
        self.assertEqual(isa.StdSL_pressure, 101325)
        self.assertEqual(isa.StdSL_speed_of_sound, 340.294)

    def test_band_boundaries(self):
        """Test custom initialization with user-specified groups."""
        isa = ISAtmosphere()

        # ISA band boundaries, base temperatures, and base pressures (from standard day) for 0-71 km altitude
        bands = [
            [0,     288.15, 101325.0],
            [11000, 216.65, 22632.0],
            [20000, 216.65, 5474.9],
            [32000, 228.65, 868.02],
            [47000, 270.65, 110.91],
            [51000, 270.65, 66.939],
            [71000, 214.65, 3.9564]
        ]

        for band_info in bands:
            isa.inputs[0] = isa.geometric_altitude(band_info[0])    # altitude
            isa.inputs[1] = 0               # temp deviation

            isa.update(None)

            self.assertAlmostEqual(isa.outputs[0], band_info[2], places=1)  # pressure
            self.assertAlmostEqual(isa.outputs[2], band_info[1], places=1)  # temperature

    def test_input_validation(self):
        """Test input validation."""
        isa = ISAtmosphere()

        # Altitudes out of bounds of the International Standard Atmosphere should raise IndexError
        with self.assertRaises(IndexError):
            isa._eval(-100)
        with self.assertRaises(IndexError):
            isa._eval(90000)

    def test_port_labels(self):
        """Test port label definitions."""
        self.assertEqual(ISAtmosphere.input_port_labels["altitude"], 0)
        self.assertEqual(ISAtmosphere.input_port_labels["temp_deviation"], 1)
        self.assertEqual(ISAtmosphere.output_port_labels["pressure"], 0)
        self.assertEqual(ISAtmosphere.output_port_labels["density"], 1)
        self.assertEqual(ISAtmosphere.output_port_labels["temperature"], 2)
        self.assertEqual(ISAtmosphere.output_port_labels["speed_of_sound"], 3)

    def test_temp_deviation(self):
        """Check that temperature deviation from standard day behaves as expected."""

        altitudes = [0, 5_000, 15_000, 25_000, 35_000, 49_000, 65_000, 75_000]
        isa = ISAtmosphere()

        for altitude in altitudes:
            # No temperature deviation (standard day)
            isa.inputs[0] = altitude
            isa.inputs[1] = 0
            isa.update(None)
            pressure_std_day = isa.outputs[0]
            density_std_day = isa.outputs[1]
            temperature_std_day = isa.outputs[2]

            # Positive temperature deviation of +10K
            isa.inputs[0] = altitude
            isa.inputs[1] = 10
            isa.update(None)
            pressure_pos_dev = isa.outputs[0]
            density_pos_dev = isa.outputs[1]
            temperature_pos_dev = isa.outputs[2]

            # Negative temperature deviation of -10K
            isa.inputs[0] = altitude
            isa.inputs[1] = -10
            isa.update(None)
            pressure_neg_dev = isa.outputs[0]
            density_neg_dev = isa.outputs[1]
            temperature_neg_dev = isa.outputs[2]

            # Checks
            self.assertAlmostEqual(temperature_pos_dev, temperature_std_day + 10)
            self.assertAlmostEqual(temperature_neg_dev, temperature_std_day - 10)

            self.assertAlmostEqual(pressure_pos_dev, pressure_std_day)
            self.assertAlmostEqual(pressure_neg_dev, pressure_std_day)

            self.assertGreater(density_std_day, density_pos_dev)
            self.assertGreater(density_neg_dev, density_std_day)

    def test_spot_altitudes(self):
        """Test pressure, density, temp, speed of sound and spot altitudes."""

        isa = ISAtmosphere()

        # References from - https://aerospaceweb.org/design/scripts/atmosphere/
        references = [
            [    0,  101325,    1.2250,     288.15, 340.294 ],
            [ 5000,  54048,     0.7364,     255.68, 320.545 ],
            [15000,  12112,     0.1948,     216.65, 295.069 ],
            [25000,  2549.2,    0.0401,     221.55, 298.389 ],
            [35000,  574.59,    0.0085,     236.51, 308.299 ],
            [49000,  90.337,    0.0012,     270.65, 329.799 ],
            [65000,  10.930,    0.00016,    233.29, 306.193 ],
            [75000,  2.388,     0.0000399,  208.40, 289.396 ]
        ]

        for ref in references:
            isa.inputs[0] = ref[0] # altitude
            isa.inputs[1] = 0
            isa.update(None)
            pressure = isa.outputs[0]
            density = isa.outputs[1]
            temperature = isa.outputs[2]
            speed_of_sound = isa.outputs[3]

            self.assertAlmostEqual(pressure, ref[1], places=0)
            self.assertAlmostEqual(density, ref[2], places=4)
            self.assertAlmostEqual(temperature, ref[3], places=2)
            self.assertAlmostEqual(speed_of_sound, ref[4], places=3)


# RUN TESTS LOCALLY ====================================================================

if __name__ == '__main__':
    unittest.main(verbosity=2)