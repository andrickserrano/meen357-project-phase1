#basci imports needed for plotting
import numpy as np
import matplotlib.pyplot as plt
from subfunctions import tau_dcmotor, get_gear_ratio, rover


# gear ratio (import rover, grab sr dict)
Ng = get_gear_ratio(rover["wheel_assembly"]["speed_reducer"])

# input to speed reducer is motor shaft
omega_in = np.linspace(0.0, rover["wheel_assembly"]["motor"]["speed_noload"], 500)
tau_in = tau_dcmotor(omega_in, rover["wheel_assembly"]["motor"])

# speed reducer output
omega_out = omega_in / Ng
tau_out = Ng * tau_in
P_out = tau_out * omega_out  # P = tau * omega

plt.figure(figsize=(7, 10))

plt.subplot(3, 1, 1)
plt.plot(tau_out, omega_out)
plt.xlabel("Speed Reducer Output Torque [Nm]")
plt.ylabel("Speed Reducer Output Speed [rad/s]")

plt.subplot(3, 1, 2)
plt.plot(tau_out, P_out)
plt.xlabel("Speed Reducer Output Torque [Nm]")
plt.ylabel("Speed Reducer Output Power [W]")

plt.subplot(3, 1, 3)
plt.plot(omega_out, P_out)
plt.xlabel("Speed Reducer Output Speed [rad/s]")
plt.ylabel("Speed Reducer Output Power [W]")


plt.tight_layout()
plt.show()
