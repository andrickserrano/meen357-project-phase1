# Task 5: creating grpah of motor efficinecy vs torque 

import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
from subfunctions import rover

 
# Extract efficiency data from rover dictionary
effcy_tau = rover['wheel_assembly']['motor']['effcy_tau']  # torque data Nm
effcy     = rover['wheel_assembly']['motor']['effcy']      # efficiency data
 
# Create cubic spline interpolation for efficiency vs. torque
effcy_fun = interp1d(effcy_tau, effcy, kind='cubic') # fit the cubic spline
 
# Evaluate the spline at 100 evenly spaced points between min and max torque
tau_eval = np.linspace(effcy_tau.min(), effcy_tau.max(), 100)
effcy_eval = effcy_fun(tau_eval)
 
# Plot efficiency vs. torque
plt.figure(figsize=(10, 5))
plt.plot(tau_eval, effcy_eval * 100, '-b', linewidth=1.5, label='Cubic Spline Interpolation')
plt.plot(effcy_tau, effcy * 100, 'r*', markersize=12, label='Data Points')
# Format graph for better presentation
plt.xlabel('Motor Torque [N-m]')
plt.ylabel('Efficiency [%]')
plt.title('Motor Efficiency vs. Torque')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig('efficiency_visualization.png', dpi=150)
plt.show()
