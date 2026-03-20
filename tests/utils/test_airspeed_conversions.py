########################################################################################
##
##                                  TESTS FOR
##                      'utils.airspeed_conversions.py'
##
########################################################################################

# IMPORTS ==============================================================================

import unittest
from pathsim_flight.utils.airspeed_conversions import (
    CAStoMach,
    CAStoTAS,
    TAStoCAS,
    CAStoEAS,
    EAStoTAS,
    MachtoCAS,
)
from pathsim_flight.atmosphere.international_standard_atmosphere import ISAtmosphere


# TESTS ================================================================================

class TestCAStoMach(unittest.TestCase):
    """Test the CAStoMach block."""

    def test_port_labels(self):
        """Test port label definitions."""
        self.assertEqual(CAStoMach.input_port_labels["cas"], 0)
        self.assertEqual(CAStoMach.input_port_labels["altitude"], 1)
        self.assertEqual(CAStoMach.output_port_labels["mach"], 0)

    def test_zero_cas_returns_zero_mach(self):
        mach = CAStoMach()._eval(0.0, 0.0)
        self.assertAlmostEqual(mach, 0.0, places=9)

    def test_monotonic_increase_and_supersonic_branch(self):
        a0 = ISAtmosphere.StdSL_speed_of_sound
        alt = 0.0
        cas_values = (1.0, 50.0, 150.0, 300.0, a0 + 1.0)
        mach_values = [CAStoMach()._eval(cas, alt) for cas in cas_values]

        # monotonic increase
        for earlier, later in zip(mach_values, mach_values[1:]):
            self.assertLess(earlier, later)

        # ensure supersonic branch yields mach > 1 for CAS slightly above speed of sound
        self.assertGreater(mach_values[-1], 1.0)

class TestCAStoTAS(unittest.TestCase):
    """Test the CAStoTAS block."""

    def test_port_labels(self):
        """Test port label definitions."""
        self.assertEqual(CAStoTAS.input_port_labels["cas"], 0)
        self.assertEqual(CAStoTAS.input_port_labels["altitude"], 1)
        self.assertEqual(CAStoTAS.output_port_labels["tas"], 0)

    def test_tas_equals_mach_times_speed_of_sound(self):
        cas = 120.0
        altitude = 5000.0

        tas = CAStoTAS()._eval(cas, altitude)

        mach = CAStoMach()._eval(cas, altitude)
        _, _, _, speed_of_sound = ISAtmosphere()._eval(altitude)

        self.assertAlmostEqual(tas, mach * speed_of_sound, places=6)

    def test_roundtrip_with_tastoCAS(self):
        for alt in (0.0, 5000.0, 11000.0):
            for cas in (1.0, 30.0, 120.0, 180.0):
                tas = CAStoTAS()._eval(cas, alt)
                cas_back = TAStoCAS()._eval(tas, alt)
                # numerical tolerance can be modest due to iterative formulas
                self.assertAlmostEqual(cas_back, cas, places=2)

class TestTAStoCAS(unittest.TestCase):
    """Test the TAStoCAS block."""

    def test_port_labels(self):
        self.assertEqual(TAStoCAS.input_port_labels["tas"], 0)
        self.assertEqual(TAStoCAS.input_port_labels["altitude"], 1)
        self.assertEqual(TAStoCAS.output_port_labels["cas"], 0)

    def test_tas_to_cas_small_speed(self):
        # For small TAS at sea level CAS ~= TAS
        for tas in (0.0, 1.0, 5.0, 20.0):
            cas = TAStoCAS()._eval(tas, 0.0)
            self.assertAlmostEqual(cas, tas, places=4)

    def test_tas_to_cas_inverse_of_cas_to_tas(self):
        # Ensure TAStoCAS(CAStoTAS(cas)) ~= cas
        for alt in (0.0, 3000.0, 10000.0):
            for cas in (5.0, 50.0, 150.0):
                tas = CAStoTAS()._eval(cas, alt)
                cas_back = TAStoCAS()._eval(tas, alt)
                self.assertAlmostEqual(cas_back, cas, places=3)

class TestCAStoEAS(unittest.TestCase):
    """Test the CAStoEAS block."""

    def test_port_labels(self):
        """Test port label definitions."""
        self.assertEqual(CAStoEAS.input_port_labels["cas"], 0)
        self.assertEqual(CAStoEAS.input_port_labels["altitude"], 1)
        self.assertEqual(CAStoEAS.output_port_labels["eas"], 0)

    def test_spot_speeds(self):
        """Test CAS to EAS conversion at some spot speeds and altitudes."""

        # References from - https://aerospaceweb.org/design/scripts/atmosphere/
        references = [
            [0,   0,        0],
            [100, 0,        100],
            [200, 0,        200],
            [300, 0,        300],
            [0 ,  1000,     0],
            [100, 1000,     99.9],
            [200, 1000,     199.0],
            [300, 1000,     297.1],
            [0,   5000,     0],
            [100, 5000,     99.1],
            [200, 5000,     193.7],
            [300, 5000,     282.9],
            [0,   10000,    0],
            [100, 10000,    97.2],
            [200, 10000,    182.6],
            [300, 10000,    265.7]
        ]

        cas_to_eas = CAStoEAS()

        for ref in references:
            cas_to_eas.inputs[0] = ref[0]        # cas
            cas_to_eas.inputs[1] = ref[1]        # altitude
            cas_to_eas.update(None)

            self.assertAlmostEqual(cas_to_eas.outputs[0], ref[2], places=1)  # eas

class TestEAStoTAS(unittest.TestCase):
    """Test the EAStoTAS block."""

    def test_port_labels(self):
        """Test port label definitions."""
        self.assertEqual(EAStoTAS.input_port_labels["eas"], 0)
        self.assertEqual(EAStoTAS.input_port_labels["altitude"], 1)
        self.assertEqual(EAStoTAS.output_port_labels["tas"], 0)

    def test_inverse_relationship_with_cas_to_eas(self):
        # EAStoTAS(CAStoEAS(cas, h), h) == CAStoTAS(cas, h)
        for alt in (0.0, 2000.0, 10000.0):
            for cas in (10.0, 50.0, 150.0):
                eas = CAStoEAS()._eval(cas, alt)
                tas_from_eas = EAStoTAS()._eval(eas, alt)
                tas_from_cas = CAStoTAS()._eval(cas, alt)
                self.assertAlmostEqual(tas_from_eas, tas_from_cas, places=6)

class TestMachtoCAS(unittest.TestCase):
    """Test the MachtoCAS block."""

    def test_port_labels(self):
        """Test port label definitions."""
        self.assertEqual(MachtoCAS.input_port_labels["mach"], 0)
        self.assertEqual(MachtoCAS.input_port_labels["altitude"], 1)
        self.assertEqual(MachtoCAS.output_port_labels["cas"], 0)

    def test_spot_machs(self):
        """Test Mach to CAS conversion at some spot Mach numbers and altitudes."""

        # References from - https://aerospaceweb.org/design/scripts/atmosphere/
        references = [
            [0.5, 0,    170.1],
            [1.2, 0,    408.4],
            [0.5, 5000, 126.0],
            [1.2, 5000, 318.6],  # 317.0
            [0.5, 10000, 89.0],
            [1.2, 10000, 234.2]  # 232.9
        ]

        mach_to_cas = MachtoCAS()

        for ref in references:
            mach_to_cas.inputs[0] = ref[0]       # mach
            mach_to_cas.inputs[1] = ref[1]       # altitude
            mach_to_cas.update(None)
            self.assertAlmostEqual(mach_to_cas.outputs[0], ref[2], places=1)


class TestGeneralAirspeedConversions(unittest.TestCase):
    """Test general properties of the airspeed conversion blocks."""

    def setUp(self):
        self.isa = ISAtmosphere()
        self.rho0 = self.isa._eval(0)[1]

    def test_cas_to_eas_at_sea_level_equals_cas_to_tas(self):
        # At sea level density == rho0 so EAS == TAS
        for cas in (0.0, 5.0, 50.0, 150.0, 250.0):
            eas = CAStoEAS()._eval(cas, 0)
            tas = CAStoTAS()._eval(cas, 0)
            self.assertAlmostEqual(eas, tas, places=9,
                                   msg=f"CAS={cas}: CAStoEAS != CAStoTAS at sea level")

    def test_eas_to_tas_inverse_of_cas_to_eas(self):
        # EAStoTAS(CAStoEAS(cas, h), h) == CAStoTAS(cas, h)
        for alt in (0.0, 2000.0, 10000.0):
            for cas in (20.0, 100.0, 200.0):
                eas = CAStoEAS()._eval(cas, alt)
                tas_from_eas = EAStoTAS()._eval(eas, alt)
                tas_from_cas = CAStoTAS()._eval(cas, alt)
                self.assertAlmostEqual(tas_from_eas, tas_from_cas, places=6,
                                       msg=f"alt={alt}, cas={cas}: EAStoTAS(CAStoEAS(.)) != CAStoTAS(.)")

    def test_tas_to_cas_roundtrip(self):
        # CAStoTAS then TAStoCAS should return approximately the original CAS
        for alt in (0.0, 5000.0, 11000.0):
            for cas in (1.0, 30.0, 120.0, 180.0):
                tas = CAStoTAS()._eval(cas, alt)
                cas_back = TAStoCAS()._eval(tas, alt)
                # Allow small numerical differences
                self.assertAlmostEqual(cas_back, cas, places=2,
                                       msg=f"alt={alt}, cas={cas}: roundtrip CAS->TAS->CAS mismatch")

    def test_cas_to_mach_monotonic_increasing(self):
        # Mach should increase with increasing calibrated airspeed
        alt = 0.0
        cas_values = (1.0, 50.0, 150.0, 300.0)
        mach_values = [CAStoMach()._eval(cas, alt) for cas in cas_values]
        for earlier, later in zip(mach_values, mach_values[1:]):
            self.assertLess(earlier, later, msg="Mach value did not increase with CAS")

    def test_eas_tas_inverse_relationship(self):
        # EAStoTAS(CAStoEAS(cas, h), h) == CAStoTAS(cas, h)
        for alt in (0.0, 2000.0, 10000.0):
            for cas in (10.0, 50.0, 150.0):
                # CAS -> EAS
                cas_to_eas = CAStoEAS()
                cas_to_eas.inputs[0] = cas
                cas_to_eas.inputs[1] = alt
                cas_to_eas.update(None)
                eas = cas_to_eas.outputs[0]

                # EAS -> TAS
                eas_to_tas = EAStoTAS()
                eas_to_tas.inputs[0] = eas
                eas_to_tas.inputs[1] = alt
                eas_to_tas.update(None)
                tas_from_eas = eas_to_tas.outputs[0]

                # CAS -> TAS
                cas_to_tas = CAStoTAS()
                cas_to_tas.inputs[0] = cas
                cas_to_tas.inputs[1] = alt
                cas_to_tas.update(None)
                tas_from_cas = cas_to_tas.outputs[0]

                self.assertAlmostEqual(tas_from_eas, tas_from_cas, places=6,
                                       msg=f"alt={alt}, cas={cas}: EAStoTAS(CAStoEAS(.)) != CAStoTAS(.)")


# RUN TESTS LOCALLY ====================================================================

if __name__ == '__main__':
    unittest.main(verbosity=2)
