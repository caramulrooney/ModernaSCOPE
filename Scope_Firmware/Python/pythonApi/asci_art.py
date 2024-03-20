from config import N_ELECTRODES
import numpy as np

def art(vals: str) -> str:
    assert len(vals) == N_ELECTRODES
    max_len = 7
    v = [] # must have a one-character name
    for val in vals:
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

print(art(["~ " + str(x) + " ~" for x in range(N_ELECTRODES)]))