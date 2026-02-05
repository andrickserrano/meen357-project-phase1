# analysis_terrain_slope.p
# Determines rover terminal speed vs terrain slope using a root-finding method
# No console output

import numpy as np
import matplotlib.pyplot as plt
from subfunctions import F_net, rover, planet, Crr, get_gear_ratio, motor

slope_array_deg = np.linspace(-15,35,25)
v_max = np.zeros_like(slope_array_deg, dtype=float)
Ng = get_gear_ratio(rover["wheel_assembly"]["speed_reducer"])
r = rover["wheel_assembly"]["wheel"]["radius"]


def bisection_speed_of_rover(terrain_angle, tol=1e-6, max_iter=200):

  omega_lo = 0.0
  omega_hi = float(rover["wheel_assembly"]["motor"]["speed_noload"])

  f_lo = F_net(omega_lo, terrain_angle, rover, planet, Crr)
  f_hi = F_net(omega_hi, terrain_angle, rover, planet, Crr)

  #handling possible edge cases and checking for root

  if f_lo == 0.0:
    return omega_lo
  if f_hi == 0.0:
    return omega_hi
  if f_lo * f_hi > 0.0:
    return np.nan

  # loop for bisection

  a, b = omega_lo, omega_hi
  fa, fb = f_lo, f_hi

  for i in range(max_iter):
    c = 0.5*(a+b)
    fc = F_net(c, terrain_angle, rover, planet, Crr)

    #stopping condition
    if abs(fc) < tol or (b-a) / 2 < tol:
      return c
    
    if fa * fc < 0:
            b = c
            fb = fc
    else:
        a = c
        fa = fc

  return 0.5 * (a + b)

# storiung values into v_max
for i, slope in enumerate(slope_array_deg):
    omega_star = bisection_speed_of_rover(float(slope))

    if np.isnan(omega_star):
        v_max[i] = np.nan
    else:
        v_max[i] = (r * omega_star) / Ng

# plot
plt.figure()
plt.title("Maximum Rover Speed vs Terrain Slope")
plt.plot(slope_array_deg, v_max)
plt.xlabel("Terrain Slope Angle [deg]")
plt.ylabel("Maximum Rover Speed [m/s]")
plt.tight_layout()
plt.show()

#checking the v_max vector to  makje sure it looks good 
#print(v_max)