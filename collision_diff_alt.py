import rospy
from mavros_msgs.msg import PositionTarget
from mavros_msgs.srv import CommandBool, SetMode, CommandTOL
from std_msgs.msg import Header
from math import cos, sin, pi

class DroneControlNode:
    def __init__(self):
        # Initialize the ROS node
        rospy.init_node('drone_control_node')

        # Number of copters
        self.num_copters = 4

        # Initialize publishers for sending position targets for each copter
        self.local_position_publishers = [rospy.Publisher('/sitl{}/mavros/setpoint_raw/local'.format(i), PositionTarget, queue_size=10) for i in range(1, self.num_copters + 1)]

        # Initialize service proxies for each copter for arming, changing flight mode, and takeoff
        self.arming_clients = [rospy.ServiceProxy('/sitl{}/mavros/cmd/arming'.format(i), CommandBool) for i in range(1, self.num_copters + 1)]
        self.set_mode_clients = [rospy.ServiceProxy('/sitl{}/mavros/set_mode'.format(i), SetMode) for i in range(1, self.num_copters + 1)]
        self.takeoff_clients = [rospy.ServiceProxy('/sitl{}/mavros/cmd/takeoff'.format(i), CommandTOL) for i in range(1, self.num_copters + 1)]

        # Define the offset for each copter
        self.offsets = [(-(i-1) * 10, 0, 0) for i in range(self.num_copters)]

    # Function to change flight mode for a copter
    def set_flight_mode(self, mode, client):
        rospy.wait_for_service(client.resolved_name)
        try:
            mode_response = client(custom_mode=mode)
            return mode_response.mode_sent
        except rospy.ServiceException as e:
            rospy.logerr("Service call failed: %s", e)

    # Function to arm a copter
    def arm_drone(self, client):
        rospy.wait_for_service(client.resolved_name)
        try:
            arm_response = client(True)
            return arm_response.success
        except rospy.ServiceException as e:
            rospy.logerr("Service call failed: %s", e)

    # Function to takeoff a copter
    def takeoff_drone(self, altitude, client):
        rospy.wait_for_service(client.resolved_name)
        try:
            takeoff_response = client(altitude=altitude)
            return takeoff_response.success
        except rospy.ServiceException as e:
            rospy.logerr("Service call failed: %s", e)

    # Function to move a copter to a specific coordinate
    def move_drone(self, x, y, z, yaw, publisher):
        position_target = PositionTarget()
        position_target.header = Header()
        position_target.header.stamp = rospy.Time.now()
        position_target.coordinate_frame = PositionTarget.FRAME_LOCAL_NED
        position_target.type_mask = PositionTarget.IGNORE_VX | PositionTarget.IGNORE_VY | PositionTarget.IGNORE_VZ | PositionTarget.IGNORE_AFX | PositionTarget.IGNORE_AFY | PositionTarget.IGNORE_AFZ | PositionTarget.FORCE | PositionTarget.IGNORE_YAW_RATE
        position_target.position.x = x
        position_target.position.y = y
        position_target.position.z = z
        position_target.yaw = yaw
        publisher.publish(position_target)

    # Main sequence to control copters
    def control_copters(self):
        try:
            # Set to GUIDED mode, arm, and takeoff for each copter
            for i in range(self.num_copters):
                self.set_flight_mode('GUIDED', self.set_mode_clients[i])
                self.arm_drone(self.arming_clients[i])
                self.takeoff_drone(10, self.takeoff_clients[i])
                
            rospy.sleep(5)
            # Define the positions for the square
            side_length = 10  # Set the side length of the square
            positions_square = [(side_length, 0, 10), (side_length, side_length, 10), (0, side_length, 10), (0, 0, 10)]

            positions_triangle = [(side_length, 0, 10), (side_length/2, side_length, 10), (0, 0, 10), (side_length/2, 0, 10)]

            # Move each copter to its position forming a square
            for i in range(self.num_copters):
                offset_x, offset_y, offset_z = self.offsets[i]
                self.move_drone(0, 0, 10+i, 0, self.local_position_publishers[i])

            rospy.sleep(5) 
            # Move each copter to its position forming a square
            for i in range(self.num_copters):
                offset_x, offset_y, offset_z = self.offsets[i]
                target_x, target_y, target_z = positions_square[i]
                self.move_drone(target_x + offset_x, target_y + offset_y, 10+i, 0, self.local_position_publishers[i])
                
            rospy.sleep(5)  
              
            for i in range(self.num_copters):
                offset_x, offset_y, offset_z = self.offsets[i]
                target_x, target_y, target_z = positions_square[i]
                self.move_drone(target_x + offset_x, target_y + offset_y, target_z + offset_z, 0, self.local_position_publishers[i])

            rospy.sleep(5) 

            for i in range(self.num_copters):
                offset_x, offset_y, offset_z = self.offsets[i]
                target_x, target_y, target_z = positions_square[i]
                self.move_drone(target_x + offset_x, target_y + offset_y, 10+i, 0, self.local_position_publishers[i])

            rospy.sleep(5)

            for i in range(self.num_copters):
                offset_x, offset_y, offset_z = self.offsets[i]
                target_x, target_y, target_z = positions_triangle[i]
                self.move_drone(target_x + offset_x, target_y + offset_y, 10+i, 0, self.local_position_publishers[i])

            rospy.sleep(5)

            for i in range(self.num_copters):
                offset_x, offset_y, offset_z = self.offsets[i]
                target_x, target_y, target_z = positions_triangle[i]
                self.move_drone(target_x + offset_x, target_y + offset_y, target_z + offset_z, 0, self.local_position_publishers[i])

             # Change altitude for each copter
            altitudes = [10, 11, 12, 13]  # Desired altitudes for RTL
            for i in range(self.num_copters):
                # Set RTL_ALTITUDE parameter for each copter
                self.param_set_client('RTL_ALTITUDE', altitudes[i], 0, '/sitl{}/mavros/'.format(i + 1))

            # Set each copter to Return to Launch (RTL) mode
            for i in range(self.num_copters):
                self.set_flight_mode('RTL', self.set_mode_clients[i])

            rospy.spin()

        except rospy.ROSInterruptException:
            pass

if __name__ == '__main__':
    node = DroneControlNode()
    node.control_copters()
