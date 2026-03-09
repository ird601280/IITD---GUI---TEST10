'''
Below are two usage examples of the OC.py Python class for control of the OC range of temperature controllers.

The OC class requires a Python version of 3.10 or greater to run. The class also relies upon an external module,
PySerial (https://pyserial.readthedocs.io/en/latest/pyserial.html#installation), which must be installed 
before the OC class can be used. This can usually be done by either running:

python -m pip install pyserial

or 

conda install pyserial

from the command line (for example, in windows Powershell or with cmd.exe) depending on whether your system uses
pip or conda.

Additionally, the example scripts use both numpy (https://numpy.org/) and matplotlib (https://matplotlib.org/)

'''

import OC
import numpy as np
from datetime import datetime, timedelta
from time import sleep
from matplotlib import pyplot as plt

# Set the com port that the OC is attached to
com_port = 'com3'

# Make a new OC object
oc = OC.OC(com_port)

# --------  Example 1: Temperature stability testing -----------
#
# This example sets the setpoint of the OC controller and enables
# the output and waits for the temperature to stabilise within a 
# given range of the setpoint value, over a predefined period, 
# before concluding that the temperature is stable.
#
# Reading of the state of the OC is done here through a direct call
# to the get_status() method. This requests the status of the 
# controller and heater and places the returned values 

# Define stability criteria
target_temperature = 60 # units: C
stability_range = 0.1 # units: C
stability_time = 20 # units: s

# Set the temperature setpoint
success = oc.set_temperature(target_temperature)

# Enable the output
oc.enable()

# Monitor temperature and test for stability
in_range = False
time_in_range = timedelta()
stable = False


while not stable:
    
    # Get the status of the controller. This will return both the 
    # setpoint that the controller is aiming for, and the current 
    # temperature of the oven.
    oc.get_status()

    # Fault check
    if not (oc.fault_code[0]  == 0):
        # If a fault is seen, it is logged in the fault_queue with the fault type
        # and the time is occured 
        print(*oc.fault_queue, sep = '\n')
        

    print("Setpoint: ", str(oc.setpoint[0]), "C.  Current temperature: ", str(oc.temperature[0]))
    
    temp_diff = abs(oc.temperature[0]-oc.setpoint[0])
    
    if temp_diff <= stability_range:
        if not in_range:
            in_range = True
            restart = True
        
        if in_range and restart:
            t0 = datetime.now()
            restart = False
        else:
            time_in_range = datetime.now() - t0
            
            if time_in_range.seconds >= stability_time:
                stable = True
    else:
        in_range = False
        time_in_range = timedelta()
    
    # Pause for a bit
    sleep(1)    
    
print("Temperature has been within a range of %3.3f C of the setpoint of %3.2f C for %3.3fs. The temperature is stable" % (stability_range, target_temperature, stability_time))

# Clean up

# Return to defaults (40 C setpoint, 100 C/s ramp rate, disabled continuous output, and output disabled.)
oc.reset_defaults()

# Turn off the OC
oc.disable()

# Close the serial port
oc.OC_close()

del oc

# ------- Example 2: Slow temperature ramping with continuous update -----
#
# This example demonstrates the ability of the OC controller to control both 
# rate of change of temperature, as well as the final temperature, and also the 
# continous update function of the OC to relieve the need for continuous polling.
# The computer's serial bus is monitored to see if any bytes are available and, 
# when there are, these bytes are read into the OC object and parsed. When enough
# bytes are received to make a full message from the OC, the message is parsed and
# the relevant properties of the OC object (current temperature, setpoint temperature,
# faults present) are updated as a tuple of their value and the time the message 
# was received. 
# Operating in this way reduces the time spent communicating with the device, freeing
# the resource for other aspects of your program.

# Make an OC object
oc = OC.OC(com_port)

# Define the ramp conditions
ramp_end = 80  # Final temperature of the ramp. Units: C
ramp_rate = 0.1 # Rate of change of temperature. Units C/s

# Make a variable to log temperatures
monitored_temps = []
monitored_times = []

# Make file to log temperatures to
fname = "OC log.csv"
fid = open(fname, mode = "w") # open the file
fid.write("Time, Elasped time [s], Temperature [C] \n") # write the header

# Set the setpoint and ramp rate of the OC
oc.set_temperature(ramp_end)

oc.set_ramp_rate(ramp_rate)

# Enable continuous output
oc.set_continuous_output()

# Enable the OC output
oc.enable()

# Monitor the ramp
while oc.temperature[0] < oc.requested_temperature:
    
    # Check for bytes received from the OC. These are parsed to look for complete messages
    # and then, if a message is available, the message_available property is set to true 
    oc.read_available_bytes()
    
    # Check for new messages
    if oc.message_available:
        oc.read_message()
        oc.parse_message()
        
        print(oc.message.decode('utf-8'))
        
        # Grab the temperature
        monitored_temps.append(oc.temperature[0])
        monitored_times.append(oc.temperature[1])

        # Write to the text file
        dt = oc.temperature[1] - monitored_times[0]
        csv_str = str(oc.temperature[1]) + ", " + str(dt.total_seconds()) + ", " + str(oc.temperature[0]) + "\n"
        fid.write(csv_str)
        
    # Do other things here, read other sensors etc.... 
    sleep(0.1)

# Close the log file
fid.close()

# Return to the defaults
oc.reset_defaults()

# Plot the temperature data and measure the ramping rate
elapsed_seconds = np.ndarray((len(monitored_times)))
for ii, t in enumerate(monitored_times):
    elapsed_seconds[ii] = (monitored_times[ii]-monitored_times[0]).seconds

f1, ax1 = plt.subplots()
ax1.plot(elapsed_seconds, monitored_temps,
         marker = 'o',
         markersize = 1,
         markeredgecolor = 'b',
         markerfacecolor = 'none',
         linestyle = 'none',
         label = "Temperature Ramp")
lin_fit_m, lin_fit_b = np.polyfit(elapsed_seconds, monitored_temps, deg=1)

ax1.axline( xy1 = (0,lin_fit_b), slope = lin_fit_m, 
           color = 'r',
           linestyle = '--',
           label=f'$y = {lin_fit_m:.1f}x {lin_fit_b:+.1f}$')
ax1.legend()
ax1.set_xlabel('Elapsed time [s]')
ax1.set_ylabel('Temperature [C]')
f1.show()