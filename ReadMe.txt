Software Name: OC.py

Version: 1.0

Description:

The python class OC.py enables control and query of a limited subset of the functions available within the OC series firmware. Using the class, the user is able to carry out all actions available from the unit’s front panel, namely turn the output from the OC (heating current to the oven/heater) on and off, and set the setpoint temperature. In addition to this the user can also set the ramp rate of the temperature, i.e. change how quickly the temperature setpoint is achieved, and enable the ‘continuous output’ mode of the controller whereby the status of the controller is sent from the unit at a rate of 1 Hz and does not need to be requested by the user. The class allows querying of the actual temperature, the setpoint temperature, and for the presence of any faults reported by the unit.

Requirements:

Python, version 3.10 or greater.
PySerial module (https://pyserial.readthedocs.io/en/latest/pyserial.html#installation)
