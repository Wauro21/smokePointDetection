import numpy as np
import os
import re
from scipy.fft import fft, fftfreq
import matplotlib.pyplot as plt

def getTime(array):
    times = array[:,0] # Time array in format HH:MM:SS
    times = np.char.replace(times,'+','') # Remove '+'
    ms_vals = array[:,1].astype(int) # ms array
    ret_vals = np.zeros(times.shape)
    for i in range(times.size):
        HH, MM, SS = times[i].split(':')
        ms = ((((int(HH)*60) + int(MM))*60) + int(SS))*1000
        time_in_ms = ms + ms_vals[i] # Converted time and ms to ms final values
        ret_vals[i] = time_in_ms
    return ret_vals

def getVoltage(array):
    # convert colon to point
    array = np.char.replace(array, ',','.')
    return array.astype(float)

def loadPhotoCases(path):
    ret_dict = dict()
    if not(os.path.isdir(path)):
        print("[ERROR] Provided directory doesn't exists!")
        exit(1)
    else:
        key_counter = 0
        files = os.listdir(path)
        for file in files:
            with open(os.path.join(path,file)) as loaded_file:
                # Data has this structure = {main_time, ms, V}
                temp_data = np.loadtxt(loaded_file, delimiter='\t', skiprows=2, dtype=str)
                time_vector = getTime(temp_data) # Convert columns 0-1 to ms
                voltage_vector = getVoltage(temp_data[:,2])
                ret_dict[key_counter] = {'time':time_vector, 'voltage':voltage_vector}
                key_counter +=1
    return ret_dict

def main():
    photodiode_path = "/mnt/shared/Linux/Smoke_point_Butano_corriente/DAQ/ASCII"
    photo_cases = loadPhotoCases(photodiode_path)

    # FFT per case
    fig, ax = plt.subplots(2)
    ax_c = 0
    for i in [0,8]:
        caso = photo_cases[i] # for testing
        N = 25000 # Fix this to be more robust
        T = 4e-3 #
        caso_fft = fft(caso['voltage'])
        freqs = fftfreq(N, T)
        ax[ax_c].plot(freqs, 10*np.log10(np.abs(caso_fft)))
        ax[ax_c].grid()
        ax_c +=1

    plt.show()
if __name__ == '__main__':
    main()
