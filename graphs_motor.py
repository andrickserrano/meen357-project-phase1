#basci imports needed for plotting
import numpy as np
import matplotlib.pyplot as plt
from subfunctions import tau_dcmotor, motor

omega = np.linspace(0.0, motor["speed_noload"], 500)
tau = tau_dcmotor(omega, motor)
P = tau * omega

plt.figure(figsize=(7, 9))


plt.subplot(3,1,1)
plt.plot(tau, omega)
plt.xlabel("Motor Shaft Torque [Nm]")
plt.ylabel("Motor Shaft Speed [rad/s]")

plt.subplot(3,1,2)
plt.plot(tau, P)
plt.xlabel("Motor Shaft Torque [Nm]")
plt.ylabel("Motor Power [W]")

plt.subplot(3,1,3)
plt.plot(omega, P)
plt.xlabel("Motor Shaft Speed [rad/s]")
plt.ylabel("Motor Power [W]")

plt.tight_layout()

plt.show()
