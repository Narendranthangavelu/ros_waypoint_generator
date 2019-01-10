#!/usr/bin/env python

import threading
import rospy
import actionlib
import csv

from smach import State,StateMachine
from move_base_msgs.msg import MoveBaseAction, MoveBaseGoal
from geometry_msgs.msg import PoseWithCovarianceStamped, PoseArray
from std_msgs.msg import Empty,String

waypoints = []

class FollowPath(State):
    def __init__(self):
        State.__init__(self, outcomes=['success'], input_keys=['waypoints'])
        
        # Get a move_base action client
        self.client = actionlib.SimpleActionClient('move_base', MoveBaseAction)
        rospy.loginfo('Connecting to move_base...')
        self.client.wait_for_server()
        rospy.loginfo('Connected to move_base.')
        

    def execute(self, userdata):
        global waypoints
        # Execute waypoints each in sequence
        for waypoint in waypoints:  
            print(waypoint.target_pose.header.frame_id, waypoint.target_pose.pose.orientation.z)       
            rospy.loginfo('Executing move_base goal to position (x,y): %s, %s' %
                    (waypoint.target_pose.pose.position.x, waypoint.target_pose.pose.position.y))
            rospy.loginfo("To cancel the goal: 'rostopic pub -1 /move_base/cancel actionlib_msgs/GoalID -- {}'")
            self.client.send_goal(waypoint)
            self.client.wait_for_result()
        
        return 'success'



class GetPath(State):
    def __init__(self):
        State.__init__(self, outcomes=['success'], input_keys=['waypoints'], output_keys=['waypoints'])
        self.frame_id = rospy.get_param('~goal_frame_id','map')

        def wait_for_path_reset():
            """thread worker function"""
            global waypoints
            while not rospy.is_shutdown():
                data = rospy.wait_for_message('/path_reset', Empty)
                rospy.loginfo('Recieved path RESET message')
                self.initialize_path_queue()
                rospy.sleep(3) # Wait 3 seconds because `rostopic echo` latches
                               # for three seconds and wait_for_message() in a
                               # loop will see it again.
        reset_thread = threading.Thread(target=wait_for_path_reset)
        reset_thread.start()

    def initialize_path_queue(self):
        global waypoints
        waypoints = [] # the waypoint queue
 
    def execute(self, userdata):
        global waypoints
        self.initialize_path_queue()
        self.path_ready = False
	
# to load points and save in array (waypoints)
        def load_points(path):
            global waypoints
            
            self.initialize_path_queue()
            no_of_points = 0
            
            with open(path.data) as csvfile:
                readCSV = csv.reader(csvfile, delimiter=',')
                for row in readCSV:
                    goal = MoveBaseGoal()
                    goal.target_pose.header.frame_id = self.frame_id
                    goal.target_pose.pose.position.x = float(row[0])
                    goal.target_pose.pose.position.y = float(row[1])
                    goal.target_pose.pose.position.z = float(row[2])
                    goal.target_pose.pose.orientation.x = float(row[3])
                    goal.target_pose.pose.orientation.y = float(row[4])
                    goal.target_pose.pose.orientation.z = float(row[5])
                    goal.target_pose.pose.orientation.w = float(row[6])
                    waypoints.append(goal)
                    no_of_points += 1
            print("{} points are readed".format(no_of_points))
            return

        # Start thread to listen for when the path is ready (this function will end then)
        def wait_for_path_ready():
            """thread worker function"""
            data = rospy.wait_for_message('/path_ready', Empty)
            rospy.loginfo('Recieved path READY message')
            self.path_ready = True
        ready_thread = threading.Thread(target=wait_for_path_ready)
        ready_thread.start()

        topic = "/load_paths"
        #rospy.loginfo("Waiting to recieve waypoints via Pose msg on topic %s" % topic)
        #rospy.loginfo("To start following waypoints: 'rostopic pub /path_ready std_msgs/Empty -1'")

        # Wait for published waypoints
        while not self.path_ready:
            try:
                path = rospy.wait_for_message(topic, String, timeout=1)
                load_points(path)
                self.path_ready = True
            except rospy.ROSException as e:
                if 'timeout exceeded' in e.message:
                    continue  # to check whether follow path command is given
                else:
                    raise e

        # Path is ready! return success and move on to the next state (FOLLOW_PATH)
        return 'success'

class PathComplete(State):
    def __init__(self):
        State.__init__(self, outcomes=['success'])
        self.pub = rospy.Publisher('way_cmp', String, queue_size=10)
    def execute(self, userdata):
        self.pub.publish("finished")
        rospy.loginfo('###############################')
        rospy.loginfo('##### REACHED FINISH GATE #####')
        rospy.loginfo('###############################')
        return 'success'

if __name__ == "__main__":
    rospy.init_node('follow_waypoints')

    sm = StateMachine(outcomes=['success'])

    with sm:
        StateMachine.add('GET_PATH', GetPath(),
                           transitions={'success':'FOLLOW_PATH'},
                           remapping={'waypoints':'waypoints'})
        StateMachine.add('FOLLOW_PATH', FollowPath(),
                           transitions={'success':'PATH_COMPLETE'},remapping={'waypoints':'waypoints'})
                           
        StateMachine.add('PATH_COMPLETE', PathComplete(),
                           transitions={'success':'GET_PATH'})
#
    outcome = sm.execute()
