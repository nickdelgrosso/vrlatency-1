import vrlatency as vrl
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns


# specify and connect to device
myarduino = vrl.Arduino.from_experiment_type(experiment_type='Display', port='COM9', baudrate=250000)

# create a stimulus
mystim = vrl.Stimulus(position=(955, 447), size=500)

# create an experiment
myexp = vrl.DisplayExperiment(arduino=myarduino,
                              trials=100,
                              fullscreen=True, screen_ind=1,
                              stim=mystim,
                              on_width=.1,
                              off_width=[.1, .3])

myexp.run()

# get the data
dd = np.array(myexp.data.values).reshape(-1, 3)

# plot the data
# NOTE: The time reported by Arduino is in microseconds. and the time reported by Python in seconds
plt.plot(dd[:, 0]/1000, dd[:, 1])
plt.xlabel('Time (ms)')
plt.show()

# get the latency values
latencies = myexp.data.get_latency(experiment_type='Display',
                                   shape=(-1, 3), effect_index=1, trial_index=2, time_index=0)

# plot the histogram of the latency values
sns.distplot(latencies)
plt.show()
