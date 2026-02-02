import numpy as np
from scipy.special import erf

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
Crr = 0.15 # (coefficient of rolling resistance)
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
    m = 0
    m += rover["wheel_assembly"]["wheel"]["mass"] * 6
    m += rover["wheel_assembly"]["speed_reducer"]["mass"] * 6
    m += rover["wheel_assembly"]["motor"]["mass"] * 6
    m += rover["chassis"]["mass"]
    m += rover["science_payload"]["mass"]
    m += rover["power_subsys"]["mass"]

    return m


m = get_mass(rover)
print(m,"kg")



# get_gear_ratio (gives gear ratio of the speed reducer)

def get_gear_ratio(speed_reducer):
  if isinstance(speed_reducer, dict):
    Ng = 0
    Ng += (speed_reducer["diam_gear"]/speed_reducer["diam_pinion"])**2
    return Ng
  else:
    raise Exception('Invalid Input for get_gear_ratio')
Ng = get_gear_ratio(speed_reducer)
print(Ng)


# tau_dcmotor (gives motor shaft torque given shaft speed and motor specs)
def tau_dcmotor(omega, motor):
    tau = 0
    tau += motor["torque_stall"]
    tau -= ((motor["torque_stall"] - motor["torque_noload"])/(motor["speed_noload"]))*omega
    return tau

omega = np.array([0, 0.1, 0.2, 0.3]) 
tau = tau_dcmotor(omega, motor)

print(tau, "Nm")



# F_drive (gives combined drive force acting on the rover due to all 6 wheels)
def F_drive(omega, rover):
    Fd = 0 
    Fd += (tau/rover["wheel_assembly"]["wheel"]["radius"])*6
    return Fd
Fd = F_drive(omega, rover)
print(Fd, "N")


# F_gravity (force due to gravity given the rover mass, planet, and terrain angles)
def F_gravity(terrain_angle, rover, planet):
    Fgt = 0
    Fgt += m*planet["g"]*np.sin(terrain_angle)
    return Fgt
    
terrain_angle = np.linspace(-15, 35, 4)
Fgt = F_gravity(terrain_angle, rover, planet)
print(Fgt, "N")

# F_rolling
def F_rolling(omega, terrain_angle, rover, planet, Crr):
    Fn = 0
    Fn += m*planet["g"]*np.cos(terrain_angle)
    Frr_simple = 0
    Frr_simple += Crr*Fn
    Frr = 0
    Frr += erf(40*v_rover)*Frr_simple
    return Frr

v_rover = omega*rover["wheel_assembly"]["wheel"]["radius"]
Frr = F_rolling(omega,terrain_angle, rover, planet, Crr)
print(Frr, "N")



# F_net

def F_net(omega, terrain_angle, rover, planet, Crr):
    F_net = 0
    F_net += Fd - Fgt - Frr
    return F_net

Fnet = F_net(omega, terrain_angle, rover, planet, Crr)
print(Fnet, "N")
