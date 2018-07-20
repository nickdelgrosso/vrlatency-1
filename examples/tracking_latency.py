import vrlatency as vrl
import natnetclient as natnet
import numpy as np
import matplotlib.pyplot as plt


# connect to device
myarduino = vrl.Arduino.from_experiment_type(experiment_type='Tracking', port='COM9', baudrate=250000)

# specify the object that is being tracked
client = natnet.NatClient()
led = client.rigid_bodies['LED']

myexp = vrl.TrackingExperiment(arduino=myarduino,
                               rigid_body=led,
                               trials=100)

myexp.run()

# get the data (start_time, time, led_pos, trial_number)
dd = np.array(myexp.data.values).reshape(-1, 4)

# plot the data
plt.scatter(dd[:, 1]/1000, dd[:, 2])
for x_val in dd[:, 0]:
    plt.axvline(x=x_val/1000)

plt.xlabel('Time (ms)')
plt.show()