# Dynamic formation management and collision avoidance



## SITL

To set up sitl for 4 copters in the same instance , we use the following command
```
sim_vehicle.py -v ArduCopter --map --console --count 4 --auto-sysid --auto-offset-line 90,10 -L iitk

```
We use the auto-offset-line argument to make sure the copters do not spawn on top of each other, and --auto-sysid for giving each copter a different tgt_system component in the launch file.


## Connecting MAVROS to SITL

After the SITL interface launches , you should see 4 copters seperated by some distance on the map window . Then we need to use mavros but first use this command to launch ROS
```
roscore
```
Then we need to make a mavros instance for each drone using the below commands.
```
roslaunch mavros apm_drone1.launch
roslaunch mavros apm_drone2.launch
roslaunch mavros apm_drone3.launch
roslaunch mavros apm_drone3.launch
```
Idealy you should run these commands in seperate terminal windows. If the command is successful , you should see "Got HEARTBEAT" on the screen.

# Using scripts to takeoff and get into formation

After taking the above steps, we can directly launch the Python files using the commands below. The first script, named formation.py, doesn't use collision avoidance and allows the drones to take off and enter a square formation. 

The second script, named collision_diff_alt.py, uses altitude difference and formation change to avoid potential collisions. The drones first take off to altitude 10. Then, before trying to get into square formation, they all move to a different altitude, 9,10,11,12, respectively. Then, they get into square formation and come back to altitude 10. After that, to get into triangle formation, it does the same thing: different altitudes, getting into formation, and finally getting to the target altitude.
```
python3 formation.py
python3 collision_diff_alt.py
```
