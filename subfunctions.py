import numpy as np
from math import erf

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
    
    if not np.isscalar(omega) and not isinstance(omega, np.ndarray):
        raise Exception("Enter omega as a scalar or numpy array")

    if not isinstance(motor, dict):
        raise Exception("enter motor value as a dictionary")

    scalar_input = np.isscalar(omega)

    omega = np.asarray(omega, dtype=float)

    tau_stall = motor["torque_stall"]
    tau_noload = motor["torque_noload"]
    omega_noload = motor["speed_noload"]

    tau = tau_stall-((tau_stall-tau_noload)/omega_noload)*omega
 
    tau = np.where(omega > omega_noload, 0.0, tau)

    tau = np.where(omega < 0, tau_stall, tau)

    if scalar_input:
        return tau.item()
    else:
        return tau

#test code
# omega = np.array([0, 0.1, 0.2, 0.3])
# tau = tau_dcmotor(omega, motor)
# print(tau)


# F_drive (gives combined drive force acting on the rover due to all 6 wheels)
import numpy as np

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

   
    if (not np.isscalar(omega) and not isinstance(omega, np.ndarray)):
        raise Exception("omega must be a scalar or numpy array")

    if (not np.isscalar(terrain_angle) and not isinstance(terrain_angle, np.ndarray)):
        raise Exception("terrain angle must be a scalar or numpy array")

    if not isinstance(rover, dict):
        raise Exception("rover specs must be a dictionary")

    if not isinstance(planet, dict):
        raise Exception("planet specs must be a dictionary")

    if not np.isscalar(Crr) or Crr <= 0:
        raise Exception("Crr must be a positive scalar")

    omega = np.asarray(omega, dtype=float)
    terrain_angle = np.asarray(terrain_angle, dtype=float)

    if omega.shape != terrain_angle.shape:
        raise Exception("omega and terrain_angle must be the same size.")

    if np.any(terrain_angle < -75) or np.any(terrain_angle > 75):
        raise Exception("Terrain angles must be between -75 and +75 degrees.")
   
    v_rover = omega*rover["wheel_assembly"]["wheel"]["radius"]

    theta = np.deg2rad(terrain_angle)

    Fn = get_mass(rover) * planet["g"] * np.cos(theta)

    Frr_simple = Crr * Fn

    Frr = erf(40*v_rover)*Frr_simple

    return Frr

# #test code
# Frr = F_rolling(omega,terrain_angle, rover, planet, Crr)
# print(Frr, "N")



# F_net

def F_net(omega, terrain_angle, rover, planet, Crr):

    if (not np.isscalar(omega) and not isinstance(omega, np.ndarray)):
        raise Exception("omega must be a scalar or numpy array")

    if (not np.isscalar(terrain_angle) and not isinstance(terrain_angle, np.ndarray)):
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
        raise Exception("omega and terrain_angle must have the same array size")

    if np.any(terrain_angle < -75) or np.any(terrain_angle > 75):
        raise Exception("terrain_angle must be between -75 and 75 degrees")

    
    Fd  = F_drive(omega, rover)                       
    Fgt = F_gravity(terrain_angle, rover, planet)     
    Frr = F_rolling(omega, terrain_angle, rover, planet, Crr)


    Fnet = Fd + Fgt + Frr

    return Fnet


#test code
# Fnet = F_net(omega, terrain_angle, rover, planet, Crr)
# print(Fnet, "N")
