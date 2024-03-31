# Import libraries
import serial
import json
from numpy.random import rand
import numpy as np
import time

N_ELECTRODES = 96

which_electrode = 68 # electrode id to plot
electrode_reading_delay = 1.5 # seconds
measurement_interval = electrode_reading_delay + 1 # seconds

def request_electrode_data(n_tries = 5):
    # with serial.Serial('/dev/ttyUSB0', 115200, timeout=1) as ser: # TO DO: change serial port
    # for i in range(n_tries):
    #     try:
    #         with serial.Serial('COM4', 115200, timeout=1) as ser: # TO DO: change serial port
    #             ser.write(b'e') # send request for electrode data
    #             plt.pause(electrode_reading_delay)
    #             response = ser.readline().decode().strip() # read response
    #             print(response)
    #             electrode_data = json.loads(response) # parse json data
    #             # print("Electrode voltages: ", electrode_data)
    #             print("Returning electrode voltages")
    #             return electrode_data
    #     except UnicodeDecodeError:
    #         pass
    print("Returning random numbers")
    return rand(96).tolist()

def electrode_ascii_art(vals: any) -> str:
    """
    Draw a diagram of the electrode using ASCII art, with a certain string being displayed for each electrode. As input, take a list of N_ELECTRODES strings, each of which must be at most 7 characters long. Return a multi-line string containing the ASCII art.
    """
    assert len(vals) == N_ELECTRODES

    max_len = 7
    v = [] # must have a one-character name
    for val in vals:
        if val is None:
            val = "."
        if not isinstance(vals, str):
            vals = str(vals)
        assert len(val) <= max_len
        v.append(" " * int(np.ceil((max_len - len(val)) / 2)) + val + " " * int(np.floor((max_len - len(val)) / 2)))

    return f"""
               1       2      3        4       5       6       7       8       9       10      11      12
          _______________________________________________________________________________________________________
         /                                                                                                       |
        /                                                                                                        |
  A    /    {v[ 0]} {v[ 1]} {v[ 2]} {v[ 3]} {v[ 4]} {v[ 5]} {v[ 6]} {v[ 7]} {v[ 8]} {v[ 9]} {v[10]} {v[11]}      |
      /                                                                                                          |
  B   |     {v[12]} {v[13]} {v[14]} {v[15]} {v[16]} {v[17]} {v[18]} {v[19]} {v[20]} {v[21]} {v[22]} {v[23]}      |
      |                                                                                                          |
  C   |     {v[24]} {v[25]} {v[26]} {v[27]} {v[28]} {v[29]} {v[30]} {v[31]} {v[32]} {v[33]} {v[34]} {v[35]}      |
      |                                                                                                          |
  D   |     {v[36]} {v[37]} {v[38]} {v[39]} {v[40]} {v[41]} {v[42]} {v[43]} {v[44]} {v[45]} {v[46]} {v[47]}      |
      |                                                                                                          |
  E   |     {v[48]} {v[49]} {v[50]} {v[51]} {v[52]} {v[53]} {v[54]} {v[55]} {v[56]} {v[57]} {v[58]} {v[59]}      |
      |                                                                                                          |
  F   |     {v[60]} {v[61]} {v[62]} {v[63]} {v[64]} {v[65]} {v[66]} {v[67]} {v[68]} {v[69]} {v[70]} {v[71]}      |
      |                                                                                                          |
  G   |     {v[72]} {v[73]} {v[74]} {v[75]} {v[76]} {v[77]} {v[78]} {v[79]} {v[80]} {v[81]} {v[82]} {v[83]}      |
      |                                                                                                          |
  H   |     {v[84]} {v[85]} {v[86]} {v[87]} {v[88]} {v[89]} {v[90]} {v[91]} {v[92]} {v[93]} {v[94]} {v[95]}      |
      |                                                                                                          |
      |__________________________________________________________________________________________________________|
"""


if __name__ == "__main__":
    while True:
        data = request_electrode_data()
        art = electrode_ascii_art([str(np.round(val, 3)) for val in data])
        print(art)
        time.sleep(measurement_interval)



