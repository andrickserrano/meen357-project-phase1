import numpy as np
import matplotlib.pyplot as plt
from subfunctions import rover, planet, simulate_rover
from define_experiment import experiment1



# Load the experiment and end_event dictionaries
experiment, end_event = experiment1()

# Override end_event fields per Task 8 instructions
end_event['max_distance']  = 1000
end_event['max_time']      = 10000
end_event['min_velocity']  = 0.01

# Run the rover simulation
rover = simulate_rover(rover, planet, experiment, end_event)

# Extract telemetry data
tel = rover['telemetry']

# Compute energy per distance for the telemetry table
energy_per_distance = tel['battery_energy'] / tel['distance_traveled']

# plotting 3x1 subplot

fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 10), sharex=True)

# Subplot 1: Position vs. Time
ax1.plot(tel['time'], tel['position'], 'b-', linewidth=1)
ax1.set_ylabel('Position [m]')
ax1.set_title('Rover Simulation Results')
ax1.grid(True)

# Subplot 2: Velocity vs. Time
ax2.plot(tel['time'], tel['velocity'], 'g-', linewidth=1)
ax2.set_ylabel('Velocity [m/s]')
ax2.grid(True)

# Subplot 3: Power vs. Time
ax3.plot(tel['time'], tel['power'], 'r-', linewidth=1)
ax3.set_xlabel('Time [s]')
ax3.set_ylabel('Power [W]')
ax3.grid(True)

plt.tight_layout()
plt.savefig('rover_experiment1.png', dpi=150)
plt.show()

# table just in case

#print("\n===== Rover Telemetry Summary =====")
#print(f"  Completion Time:       {tel['completion_time']:.2f} s")
#print(f"  Distance Traveled:     {tel['distance_traveled']:.2f} m")
#print(f"  Max Velocity:          {tel['max_velocity']:.4f} m/s")
#print(f"  Average Velocity:      {tel['average_velocity']:.4f} m/s")
#print(f"  Battery Energy:        {tel['battery_energy']:.2f} J")
#print(f"  Energy per Distance:   {energy_per_distance:.2f} J/m")

# Task 9

#battery_capacity = 0.9072e6  # Joules (Lithium Iron Phosphate battery pack)

#print("\n===== Task 9: Energy Analysis =====")
#print(f"  Battery Capacity:      {battery_capacity:.2f} J")
#print(f"  Energy Required:       {tel['battery_energy']:.2f} J")

#if tel['battery_energy'] <= battery_capacity:
 #   print("  Result: The rover CAN complete the mission with this battery pack.")
#else:
 #   print("  Result: The rover CANNOT complete the mission with this battery pack.")
