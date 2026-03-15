#########################################################################################
##
##                     JSBSim Wrapper Block
##
#########################################################################################

# IMPORTS ===============================================================================

from pathsim.blocks import Wrapper
import jsbsim

# BLOCKS ================================================================================

class JSBSimWrapper(Wrapper):
    """A wrapper for the JSBSim flight dynamics model, which allows it to be
    used as a block in PathSim.

    Parameters
    ----------
    T : float
        The time step for the JSBSim model, in seconds. Default is 1/120, which corresponds
        to 120 Hz.
    input_properties : list of str
        A list of JSBSim property names that correspond to the input ports of the block. 
    output_properties : list of str
        A list of JSBSim property names that correspond to the output ports of the block.
    JSBSim_path : str
        The file path to the JSBSim installation. If None, it will look for JSBSim files 
        in the         pip install location.
    aircraft_model : str
        The name of the aircraft model to load in JSBSim. Default is '737'.
    trim_airspeed : float
        The airspeed to use for trimming the aircraft, as KCAS. Default is 200 KCAS.
    trim_altitude : float
        The altitude ASL to use for trimming the aircraft, in feet. Default is 1000 ft ASL.
    trim_gamma : float
        The flight path angle to use for trimming the aircraft, in degrees. Default is 
        0 degrees (level flight).
    """

    input_port_labels = None

    output_port_labels = None

    # TODO: Probably need to add some additional parameters, e.g. ground trim versus 
    # full air trim versus no trim, gear position, flap position.

    def __init__(self, T=1/120, input_properties=None, output_properties=None, JSBSim_path=None,
                 aircraft_model='737', trim_airspeed=200, trim_altitude=1000, trim_gamma=0):
        super().__init__(func=self._func, T=T)

        self.input_properties = input_properties if input_properties is not None else []
        self.output_properties = output_properties if output_properties is not None else []

        # Init JSBSim, load aircraft, trim with initial conditions
        self.init_fdm(JSBSim_path, aircraft_model, T)
        self.trim(trim_airspeed, trim_altitude, trim_gamma)

    def init_fdm(self, JSBSim_path, aircraft_model, T):
        # Avoid flooding the console with log messages
        jsbsim.FGJSBBase().debug_lvl = 0

        # Create a flight dynamics model (FDM) instance. 
        # None for JSBSim_path means it will look for JSBSim files in pip install location.
        self.fdm = jsbsim.FGFDMExec(JSBSim_path)

        # Load the aircraft model
        self.fdm.load_model(aircraft_model)

        # Set the time step
        self.fdm.set_dt(T)

    def trim(self, trim_airspeed, trim_alitude, trim_gamma):
        # Set engines running
        self.fdm['propulsion/set-running'] = -1

        # Set initial conditions for trim
        self.fdm['ic/h-sl-ft'] = trim_alitude
        self.fdm['ic/vc-kts'] = trim_airspeed
        self.fdm['ic/gamma-deg'] = trim_gamma
        self.fdm.run_ic()

        # Calculate trim solution
        self.fdm['simulation/do_simple_trim'] = 1

    def _func(self, *u):
        # PathSim's Wrapper base class passes the input vector as separate arguments, 
        # so we need to collect them into a list

        # Confirm that the input vector u has the expected length
        if len(u) != len(self.input_properties):
            raise ValueError(f"Expected {len(self.input_properties)} inputs, but got {len(u)}")

        # Pass input vector u to JSBSim by setting the corresponding properties
        for i in range(len(u)):
            self.fdm[self.input_properties[i]] = u[i]

        # Run the JSBSim model for one time step
        self.fdm.run()  

        # Extract output properties from JSBSim and return as vector y
        y = []
        for i in range(len(self.output_properties)):
            y.append(self.fdm[self.output_properties[i]])

        return y
