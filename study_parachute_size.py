import numpy as np
import matplotlib.pyplot as plt


from define_edl_system import define_edl_system_1
from define_planet import define_planet
from define_mission_events import define_mission_events
from subfunctions_EDL import simulate_edl
from redefine_edl_system import redefine_edl_system


mars = define_planet()
mission_events = define_mission_events()

tmax = 2000  


diameters = np.arange(14, 19.5, 0.5)


termination_time = []
landing_velocity = []
landing_success = []


for D in diameters:

    
    edl_system = define_edl_system_1()
    edl_system = redefine_edl_system(edl_system)

    
    edl_system['altitude'] = 11000
    edl_system['velocity'] = -590

    edl_system['rocket']['on'] = False
    edl_system['parachute']['deployed'] = True
    edl_system['parachute']['ejected'] = False
    edl_system['heat_shield']['ejected'] = False
    edl_system['sky_crane']['on'] = False
    edl_system['speed_control']['on'] = False
    edl_system['position_control']['on'] = False

    
    edl_system['parachute']['diameter'] = D


    t, Y, edl_system = simulate_edl(edl_system, mars, mission_events, tmax, False)


    t_end = t[-1]
    v_end = Y[0, -1]  
    altitude_end = Y[1, -1]

    termination_time.append(t_end)
    landing_velocity.append(v_end)

   
    if edl_system['rover']['on_ground'] and abs(v_end) <= abs(edl_system['sky_crane']['danger_speed']):
        landing_success.append(1)
    else:
        landing_success.append(0)


termination_time = np.array(termination_time)
landing_velocity = np.array(landing_velocity)
landing_success = np.array(landing_success)


fig, axs = plt.subplots(3, 1, figsize=(8, 12))


axs[0].plot(diameters, termination_time, 'o-')
axs[0].set_xlabel('Parachute Diameter (m)')
axs[0].set_ylabel('Termination Time (s)')
axs[0].set_title('Simulation Time vs Parachute Diameter')
axs[0].grid()


axs[1].plot(diameters, landing_velocity, 'o-')
axs[1].set_xlabel('Parachute Diameter (m)')
axs[1].set_ylabel('Landing Velocity (m/s)')
axs[1].set_title('Landing Velocity vs Parachute Diameter')
axs[1].grid()


axs[2].plot(diameters, landing_success, 'o-')
axs[2].set_xlabel('Parachute Diameter (m)')
axs[2].set_ylabel('Landing Success (1=Success, 0=Failure)')
axs[2].set_title('Landing Success vs Parachute Diameter')
axs[2].grid()

plt.tight_layout()
plt.show()