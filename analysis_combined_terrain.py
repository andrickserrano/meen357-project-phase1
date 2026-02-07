
# analysis_rolling_resistance.py
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import matplotlib.pyplot as plt

from subfunctions import F_net, rover, planet, get_gear_ratio
from matplotlib.ticker import FuncFormatter

# rolling resistance array
Crr_array = np.linspace(0.01,0.5,25)
#slope array
slope_array_deg = np.linspace(-15,35,25)
#meshgrid
CRR, SLOPE = np.meshgrid(Crr_array, slope_array_deg)
#start vmax matrix
VMAX = np.zeros(np.shape(CRR), dtype = float)


Ng = get_gear_ratio(rover["wheel_assembly"]["speed_reducer"])
r = rover["wheel_assembly"]["wheel"]["radius"]
omega_lo_default = 0.0
omega_hi_default = float(rover["wheel_assembly"]["motor"]["speed_noload"])


def omega_terminal_bisect(slope_deg, Crr_sample, tol=1e-6, max_iter=200):
  omega_lo = omega_lo_default
  omega_hi = omega_hi_default

  f_lo = F_net(omega_lo, slope_deg, rover, planet, Crr_sample)
  f_hi = F_net(omega_hi, slope_deg, rover, planet, Crr_sample)

    # edge cases + bracket check
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
        fc = F_net(c, slope_deg, rover, planet, Crr_sample)

        if abs(fc) < tol or (b - a) / 2 < tol:
            return c

        if fa * fc < 0.0:
            b = c
        else:
            a = c
            fa = fc

  return 0.5 * (a + b)

N = np.shape(CRR)[0]  # 25
for i in range(N):
    for j in range(N):
        Crr_sample = float(CRR[i, j])
        slope_sample = float(SLOPE[i, j])

        omega_star = omega_terminal_bisect(slope_sample, Crr_sample)

        if np.isnan(omega_star):
            VMAX[i, j] = np.nan
        else:
            # convert motor shaft omega to rover speed
            VMAX[i, j] = (r * omega_star) / Ng


# 3d plot 
fig = plt.figure(figsize=(9, 7))
ax = fig.add_subplot(111, projection='3d')

ax.view_init(elev=30, azim=-135)

surf = ax.plot_surface(
    CRR, SLOPE, VMAX,
    cmap="viridis",
    edgecolor="none"
)

# Labels and label formatting
ax.set_xlabel("Rolling Resistance Coefficient Crr [-]", labelpad=12)
ax.set_ylabel("Terrain Slope Angle [deg]", labelpad=12)
ax.set_zlabel("Maximum Rover Speed [m/s]", labelpad=12)

ax.set_title("Maximum Rover Speed vs. Slope and Rolling Resistance", pad=18)

# Colorbar
cbar = fig.colorbar(surf, ax=ax, shrink=0.6, aspect=12, label="Speed [m/s]")

vmin = np.nanmin(VMAX)
vmax = np.nanmax(VMAX)
# fixing colorbar issues
def flip_labels(x, pos):
    # Relabel tick value x as (vmin+vmax - x)
    return f"{(vmin + vmax - x):.2f}"

cbar.formatter = FuncFormatter(flip_labels)
cbar.update_ticks()

plt.tight_layout()
plt.show()
#print(VMAX)