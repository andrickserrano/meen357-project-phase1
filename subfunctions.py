import numpy as np
from scipy.special import erf
from scipy.interpolate import interp1d
from scipy.integrate import solve_ivp



# Constants

r = 0.3 #m (wheel radius)
wheel_mass = 1 #kg 
tau_s = 170 #Nm (motor stall torque)
tau_NL = 0 #Nm (motor no-load torque)
omega_NL = 3.8 #rad/s (motor no-load speed)
motor_mass = 5 #kg 
science_payload_mass = 75 #kg
RTG_mass = 90 #kg
chassis_mass = 659 #kg
d_1 = 0.04 #m (speed reducer pinion diameter)
d_2 = 0.07 #m (speed reducer gear diameter)
speed_reducer_mass = 1.5 #kg
g_mars = 3.72 #m/s^2 (acceleration due to gravity on mars)
Crr = 0.15

#Dictionaries

wheel = {"radius": r, 
         "mass" : wheel_mass
         }

speed_reducer = {"type": "reverted",
                 "diam_pinion": d_1,
                 "diam_gear": d_2,
                 "mass": speed_reducer_mass
                }

motor = {"torque_stall": tau_s,
         "torque_noload": tau_NL,
         "speed_noload": omega_NL,
         "mass": motor_mass
         "effcy_tau": np.array([0, 10, 20, 40, 70, 165]),
         "effcy": np.array([0, 0.60, 0.78, 0.73, 0.52, 0.04])
         }

chassis = {"mass": chassis_mass
           }

science_payload = {"mass": science_payload_mass
                   }

power_subsys = {"mass": RTG_mass
                }

planet = {"g": g_mars
          }

wheel_assembly = { "wheel": wheel,
                  "speed_reducer": speed_reducer, 
                  "motor": motor, 

  }

rover = {
    "wheel_assembly": wheel_assembly,
    "chassis": chassis,
    "science_payload": science_payload,
    "power_subsys": power_subsys
}




# get_mass (gives mass of the entire rover)

def get_mass(rover):
    
    if not isinstance(rover, dict):
        raise Exception("Input must be dictionary containing rover specs.")
    
    m = 0
    m += rover["wheel_assembly"]["wheel"]["mass"] * 6
    m += rover["wheel_assembly"]["speed_reducer"]["mass"] * 6
    m += rover["wheel_assembly"]["motor"]["mass"] * 6
    m += rover["chassis"]["mass"]
    m += rover["science_payload"]["mass"]
    m += rover["power_subsys"]["mass"]

    return m

#test code
# m = get_mass(rover)
# print(m,"kg")



# get_gear_ratio (gives gear ratio of the speed reducer)

def get_gear_ratio(speed_reducer):
    
    if not isinstance(speed_reducer, dict):
        raise Exception("Input to get_gear_ratio function must be a dictionary.")

    if "type" not in speed_reducer:
        raise Exception("Speed reducer dictionary must contain a 'type' field.")

    if speed_reducer["type"].lower() != "reverted":
        raise Exception(f"Unsupported speed reducer type '{speed_reducer['type']}'. "
            "Only 'reverted' gear sets are allowed")
    Ng = 0
    Ng += (speed_reducer["diam_gear"]/speed_reducer["diam_pinion"])**2
    return Ng

#test code
# Ng = get_gear_ratio(speed_reducer)
# print(Ng)


# tau_dcmotor (returns motor shaft torque in Nm given shaft speed in rad/s)

def tau_dcmotor(omega, motor):

    if not isinstance(motor, dict):
        raise Exception("motor must be a dictionary")

    if not np.isscalar(omega) and not isinstance(omega, np.ndarray):
        raise Exception("omega must be a scalar or numpy array")

    try:
        omega = np.asarray(omega, dtype=float)
    except Exception:
        raise Exception("omega must contain numeric values")
    
    if omega.ndim > 1:
        raise Exception("omega must be a scalar or 1D array")
    
    scalar_input = omega.ndim == 0

    tau_stall = motor["torque_stall"]
    tau_noload = motor["torque_noload"]
    omega_noload = motor["speed_noload"]

    tau = tau_stall - ((tau_stall - tau_noload) / omega_noload) * omega

    tau = np.where(omega > omega_noload, 0.0, tau)
    tau = np.where(omega < 0, tau_stall, tau)

    return tau.item() if scalar_input else tau



#test code
# omega = np.array([0, 0.1, 0.2, 0.3])
# tau = tau_dcmotor(omega, motor)
# print(tau)


# F_drive (gives combined drive force acting on the rover due to all 6 wheels)

def F_drive(omega, rover):

   
    if not np.isscalar(omega) and not isinstance(omega, np.ndarray):
        raise Exception("Enter omega as a scalar or numpy array")

    if not isinstance(rover, dict):
        raise Exception("enter motor value as a dictionary")

    scalar_input = np.isscalar(omega)

    
    omega = np.asarray(omega, dtype=float)

   
    motor = rover["wheel_assembly"]["motor"]
    tau = tau_dcmotor(omega, motor)

   
    speed_reducer = rover["wheel_assembly"]["speed_reducer"]
    Ng = get_gear_ratio(speed_reducer)



    Fd = 6*(tau*Ng)/(rover["wheel_assembly"]["wheel"]["radius"])

    if scalar_input:
        return Fd.item()
    else:
        return Fd

#test code
# Fd = F_drive(omega, rover)
# print(Fd, "N")


# F_gravity (force due to gravity given the rover mass, planet, and terrain angles)
def F_gravity(terrain_angle, rover, planet):

    if not np.isscalar(terrain_angle) and not isinstance(terrain_angle, np.ndarray):
        raise Exception("terrain angle must be scalar or numpy array")

    if not isinstance(rover, dict):
        raise Exception("rover specs must be a dictionary")

    if not isinstance(planet, dict):
        raise Exception("planet specs must be a dictionary")

    scalar_input = np.isscalar(terrain_angle)

    terrain_angle = np.asarray(terrain_angle, dtype=float)

    if np.any(terrain_angle < -75) or np.any(terrain_angle > 75):
        raise Exception("Terrain angles must be between -75 and 75 degrees.")

    theta_rad = np.deg2rad(terrain_angle)
    
    Fgt = 0
    Fgt += -get_mass(rover)*planet["g"]*np.sin(theta_rad)

    if scalar_input:
        return Fgt.item()
    else:
        return Fgt

#test code
# terrain_angle = np.linspace(-15, 35, 4)
# Fgt = F_gravity(terrain_angle, rover, planet)
# print(Fgt, "N")




# F_rolling

def F_rolling(omega, terrain_angle, rover, planet, Crr):

    omega = np.asarray(omega, dtype=float)
    terrain_angle = np.asarray(terrain_angle, dtype=float)

    if omega.shape != terrain_angle.shape:
        raise Exception("omega and terrain_angle must be the same size")

    if np.any(terrain_angle < -75) or np.any(terrain_angle > 75):
        raise Exception("terrain_angle must be between -75 and +75 degrees")

    speed_reducer = rover["wheel_assembly"]["speed_reducer"]
    Ng = get_gear_ratio(speed_reducer)

    r = rover["wheel_assembly"]["wheel"]["radius"]
    v_rover = (omega*r)/Ng
    theta = np.deg2rad(terrain_angle)

    Fn = get_mass(rover) * planet["g"] * np.cos(theta)
    Frr_simple = Crr * Fn
    Frr = -np.sign(v_rover) * erf(40 * np.abs(v_rover)) * Frr_simple

    return Frr.item() if Frr.ndim == 0 else Frr



# #test code
# Frr = F_rolling(omega,terrain_angle, rover, planet, Crr)
# print(Frr, "N")



# F_net

def F_net(omega, terrain_angle, rover, planet, Crr):

    if not np.isscalar(omega) and not isinstance(omega, np.ndarray):
        raise Exception("omega must be a scalar or numpy array")

    if not np.isscalar(terrain_angle) and not isinstance(terrain_angle, np.ndarray):
        raise Exception("terrain_angle must be a scalar or numpy array")

    if not isinstance(rover, dict):
        raise Exception("rover must be a dictionary")

    if not isinstance(planet, dict):
        raise Exception("planet must be a dictionary")

    if not np.isscalar(Crr) or Crr <= 0:
        raise Exception("Crr must be a positive scalar")

    omega = np.asarray(omega, dtype=float)
    terrain_angle = np.asarray(terrain_angle, dtype=float)

   
    if omega.shape != terrain_angle.shape:
        raise Exception("omega and terrain_angle must be the same size")

    if np.any(terrain_angle < -75) or np.any(terrain_angle > 75):
        raise Exception("terrain_angle must be between -75 and 75 degrees")

    Fd  = F_drive(omega, rover)
    Fgt = F_gravity(terrain_angle, rover, planet)
    Frr = F_rolling(omega, terrain_angle, rover, planet, Crr)

    return Fd + Fgt + Frr


#test code
# Fnet = F_net(omega, terrain_angle, rover, planet, Crr)
# print(Fnet, "N")

# Motor W

def motorW(v, rover):
    
    """
    computes he rotational speed of the motor shaft [rad/s] given the translational 
    velocity of the rover and the rover dictionary.

   Input:
   v : float or numpy.ndarray
       Rover velocity in m/s.
   rover : dict
       Dictionary containing rover parameters.

  Output:
   w : float or numpy.ndarray
       Motor shaft angular speed in rad/s.
   """

    if not isinstance(rover, dict):
        raise Exception("input must be a rover dictionary.")

    if not np.isscalar(v) and not isinstance(v, np.ndarray):
        raise Exception("input must be a scalar or a numpy array.")

    try:
        v = np.asarray(v, dtype=float)
    except:
        raise Exception("Velocity input must contain numeric values.")

    if v.ndim > 1:
        raise Exception("Velocity input must be a scalar or 1D numpy array.")

    scalar_input = v.ndim == 0

    r = rover["wheel_assembly"]["wheel"]["radius"]
    Ng = get_gear_ratio(rover["wheel_assembly"]["speed_reducer"])

    w = (v / r) * Ng


    return w.item() if scalar_input else w


# Rover Dynamics

def rover_dynamics(t, y, rover, planet, experiment):
    """
    the derivative of the state vector (state vector is: [velocity, position]) for the rover given its
    current state. It requires rover and experiment dictionary input parameters. 
    It is intended to be passed to an ODE solver.

    Input:
    t : float
        Current simulation time (s)
    y : numpy.ndarray
        y[0] = rover velocity (m/s)
        y[1] = rover position (m)
    rover : dict
        Rover parameters
    planet : dict
        Planet parameters
    experiment : dict
        Terrain and experiment 

    Output
    dydt : numpy.ndarray
        Derivative of state vector [acceleration, velocity]
    """

    if not np.isscalar(t):
        raise Exception("t must be a scalar")

    y = np.asarray(y, dtype=float)

    if y.size != 2:
        raise Exception("y must contain [velocity, position]")

    if not isinstance(rover, dict):
        raise Exception("rover must be a dictionary")

    if not isinstance(planet, dict):
        raise Exception("planet must be a dictionary")

    if not isinstance(experiment, dict):
        raise Exception("experiment must be a dictionary")


    v = y[0]
    x = y[1]

    alpha_dist = np.array(experiment["alpha_dist"])
    alpha_deg = np.array(experiment["alpha_deg"])

    alpha_fun = interp1d(alpha_dist, alpha_deg, kind = 'cubic', fill_value="extrapolate")

    

    omega = motorW(v, rover)
    
    if isinstance (omega, np.ndarray):
        terrain_angle = alpha_fun(x)
    else:
        terrain_angle = float(alpha_fun(x))

    Crr = experiment["Crr"]

    Fnet_val = F_net(omega, terrain_angle, rover, planet, Crr)

    m = get_mass(rover)

    a = Fnet_val / m

    dydt = np.array([a, v])

    return dydt

# Mechpower

def mechpower(v, rover):

    """
    Computes the instantaneous mechanical power output by a single DC motor at each point in a given
    velocity profile.


    Input:
    v : float or numpy.ndarray
        Rover velocity (m/s)
    rover : dict
        Dictionary containing rover parameters

    Output:
    P : float or numpy.ndarray
        Mechanical power produced by the motor (W)
    """

    if not np.isscalar(v) and not isinstance(v, np.ndarray):
        raise Exception("input must be a scalar or a numpy array.")

    if not isinstance(rover, dict):
        raise Exception("input must be a rover dictionary.")

    try:
        v = np.asarray(v, dtype=float)
    except:
        raise Exception("Velocity input must contain numeric values.")

    if v.ndim > 1:
        raise Exception("Velocity input must be a scalar or 1D numpy array.")

    scalar_input = v.ndim == 0

    omega = motorW(v, rover)

    motor = rover["wheel_assembly"]["motor"]
    tau = tau_dcmotor(omega, motor)

    P = tau * omega

    return float(P) if scalar_input else P

# Battery Energy


def battenergy(t, v, rover):
    """
    computes the total electrical energy consumed from the rover battery pack over a simulation profile,
    defined as time-velocity pairs. This function assumes all 6 motors are driven from the same 
    battery pack.
    This function accounts for energy consumed by all motors).


    Input:
    t : numpy.ndarray
        Time array (s)
    v : numpy.ndarray
        Rover velocity array (m/s)
    rover : dict
        Rover parameter dictionary

    Output:
    E : float
        Total battery energy consumed (J)
    """

    if (isinstance(rover, dict) and isinstance(v, np.ndarray) and isinstance(t, np.ndarray)) == False:
        raise Exception("Rover must be a dict and v and t must be numpy arrays")
    
    if len(v) != len(t):
        raise Exception("v and t must be equal size numpy arrays")



    P_mech = mechpower(v, rover)


    omega = motorW(v, rover)
    motor = rover["wheel_assembly"]["motor"]
    tau = tau_dcmotor(omega, motor)

    effcy_tau = rover["wheel_assembly"]["motor"]["effcy_tau"]
    effcy = rover["wheel_assembly"]["motor"]["effcy"]
    effcy_fun = interp1d(effcy_tau, effcy, kind = 'cubic')

    y = P_mech / effcy_fun(tau)
    E = np.trapz(y, x = t) * 6
    return E


# Simulate Rover
def simulate_rover(rover, planet, experiment, end_event):
    
    """
   This function integrates the trajectory of a rover.

   Inputs:
   rover : dict
       Dictionary containing rover parameters.

   planet : dict
       Dictionary containing planetary parameters (e.g., gravity).

   experiment : dict
       Dictionary containing experiment parameters including:
       - time_range
       - initial_conditions
       - terrain distance and angles
       - rolling resistance coefficient

   end_event : dict
       Dictionary containing mission termination conditions:
       - max_distance
       - max_time
       - min_velocity

   Outputs:
   rover : dict
       The rover dictionary with a telemetry field added containing:

       telemetry["time"] : numpy.ndarray
           Time history of the simulation (s)

       telemetry["velocity"] : numpy.ndarray
           Rover velocity over time (m/s)

       telemetry["position"] : numpy.ndarray
           Rover position over time (m)

       telemetry["power"] : numpy.ndarray
           Mechanical power output of the motors (W)

       telemetry["battery_energy"] : float
           Total battery energy consumed (J)

       telemetry["completion_time"] : float
           Total mission time (s)

       telemetry["distance_traveled"] : float
           Total distance traveled (m)

       telemetry["max_velocity"] : float
           Maximum rover velocity (m/s)

       telemetry["average_velocity"] : float
           Average rover velocity (m/s)
   """

    if not isinstance(rover, dict):
        raise Exception("rover must be a dictionary")

    if not isinstance(planet, dict):
        raise Exception("planet must be a dictionary")

    if not isinstance(experiment, dict):
        raise Exception("experiment must be a dictionary")

    if not isinstance(end_event, dict):
        raise Exception("end_event must be a dictionary")


    
    t0, tf = experiment["time_range"]
    v0, x0 = experiment["initial_conditions"]

    y0 = np.array([float(v0), float(x0)], dtype=float)


  
    event_fun = end_of_mission_event(end_event)

    
    event_fun.terminal = True
    event_fun.direction = 0

 
    sol = solve_ivp(
        fun=lambda t, y: rover_dynamics(t, y, rover, planet, experiment),
        t_span=(t0, tf),
        y0=y0,
        method="RK45",
        events=event_fun,
        max_step=0.1      
    )

   
    time     = sol.t
    velocity = sol.y[0]
    position = sol.y[1]

   
    power  = mechpower(velocity, rover)
    energy = battenergy(time, velocity, rover)


    rover["telemetry"] = {
        "time": time,
        "velocity": velocity,
        "position": position,
        "power": power,
        "battery_energy": float(energy),
        "completion_time": float(time[-1]),
        "distance_traveled": float(position[-1]),
        "max_velocity": float(np.max(velocity)),
        "average_velocity": float(np.mean(velocity)),
    }

    return rover


def end_of_mission_event(end_event):
    """
    Defines an event that terminates the mission simulation. Mission is over
    when rover reaches a certain distance, has moved for a maximum simulation 
    time or has reached a minimum velocity.            
    """
    
    mission_distance = end_event['max_distance']
    mission_max_time = end_event['max_time']
    mission_min_velocity = end_event['min_velocity']
    
    # Assume that y[1] is the distance traveled
    distance_left = lambda t,y: mission_distance - y[1]
    distance_left.terminal = True
    
    time_left = lambda t,y: mission_max_time - t
    time_left.terminal = True
    
    velocity_threshold = lambda t,y: y[0] - mission_min_velocity;
    velocity_threshold.terminal = True
    velocity_threshold.direction = -1
    
    # terminal indicates whether any of the conditions can lead to the
    # termination of the ODE solver. In this case all conditions can terminate
    # the simulation independently.
    
    # direction indicates whether the direction along which the different
    # conditions is reached matters or does not matter. In this case, only
    # the direction in which the velocity treshold is arrived at matters
    # (negative)
    
    events = [distance_left, time_left, velocity_threshold]
    
    return events
