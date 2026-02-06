# analysis_rolling_resistance.py

import numpy as np
import matplotlib.pyplot as plt

from subfunctions import F_net, rover, planet, get_gear_ratio

# given by assignment
Crr_array = np.linspace(0.01, 0.5, 25)
terrain_angle = 0.0  # degrees (flat ground)\


# conversion constants
Ng = get_gear_ratio(rover["wheel_assembly"]["speed_reducer"])
r = rover["wheel_assembly"]["wheel"]["radius"]
omega_hi_default = float(rover["wheel_assembly"]["motor"]["speed_noload"])
omega_lo_default = 0.0

def bisection_omega_for_Crr(Crr_sample, tol=1e-6, max_iter=200):
    omega_lo = omega_lo_default
    omega_hi = omega_hi_default

    f_lo = F_net(omega_lo, terrain_angle, rover, planet, Crr_sample)
    f_hi = F_net(omega_hi, terrain_angle, rover, planet, Crr_sample)

    if f_lo == 0.0:
        return omega_lo
    if f_hi == 0.0:
        return omega_hi
    if f_lo * f_hi > 0.0:
        return np.nan

    a, b = omega_lo, omega_hi
    fa = f_lo

    for _ in range(max_iter):
        c = 0.5 * (a + b)
        fc = F_net(c, terrain_angle, rover, planet, Crr_sample)

        if abs(fc) < tol or (b - a) / 2 < tol:
            return c

        if fa * fc < 0.0:
            b = c
        else:
            a = c
            fa = fc

    return 0.5 * (a + b)

# storing v_max
v_max = np.zeros_like(Crr_array, dtype=float)

for i, Crr_sample in enumerate(Crr_array):
    omega_star = bisection_omega_for_Crr(float(Crr_sample))

    if np.isnan(omega_star):
        v_max[i] = np.nan
    else:
        v_max[i] = (r * omega_star) / Ng  # convert motor omega to rover speed

# plot
plt.figure()
plt.plot(Crr_array, v_max)
plt.xlabel("Rolling Resistance Coefficient Crr [-]")
plt.ylabel("Maximum Rover Speed [m/s]")
plt.tight_layout()
plt.show()
