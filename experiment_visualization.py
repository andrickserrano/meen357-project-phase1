
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
from define_experiment import experiment1
 
# Load experiment data
experiment, end_event = experiment1()
 
# Extract terrain data from the experiment dictionary
alpha_dist = experiment['alpha_dist']  # distance data points [m]
alpha_deg  = experiment['alpha_deg']   # terrain angle data points [deg]
 
# Create cubic spline interpolation function for terrain angle vs. distance
alpha_fun = interp1d(alpha_dist, alpha_deg, kind='cubic', fill_value='extrapolate')
 
# Evaluate the spline at 100 evenly spaced points across the terrain
x_eval = np.linspace(alpha_dist.min(), alpha_dist.max(), 100)
alpha_eval = alpha_fun(x_eval)
 
# Plot terrain angle vs. position
plt.figure(figsize=(10, 5))
plt.plot(x_eval, alpha_eval, '-b', linewidth=1.5, label='Cubic Spline Interpolation')
plt.plot(alpha_dist, alpha_deg, 'r*', markersize=12, label='Data Points')
plt.xlabel('Position [m]')
plt.ylabel('Terrain Angle [deg]')
plt.title('Terrain Angle vs. Position')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig('experiment_visualization.png', dpi=150)
plt.show()
 