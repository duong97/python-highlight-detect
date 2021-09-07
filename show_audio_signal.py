import matplotlib.pyplot as plt
import numpy as np
from scipy.io import wavfile
# %matplotlib inline

plt.rcParams['figure.dpi'] = 100
plt.rcParams['figure.figsize'] = (9, 7)

sampFreq, sound = wavfile.read('../soundlong.wav')
print(sound.shape)

length_in_s = sound.shape[0] / sampFreq
print(length_in_s)
plt.subplot(2,1,1)
plt.plot(sound[:,0], 'r')
plt.xlabel("left channel, sample #")
plt.subplot(2,1,2)
plt.plot(sound[:,1], 'b')
plt.xlabel("right channel, sample #")
plt.tight_layout()
plt.show()



