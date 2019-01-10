#!/usr/bin/env python
import rospy
import sys
from std_msgs.msg import Empty,String
import subprocess



def main(path):
    rospy.init_node("ui_navigation")
    path_pub = rospy.Publisher('load_paths', String, queue_size=10)
    result_pub = rospy.Publisher('nav_result', String, queue_size=10)
  

    while not rospy.is_shutdown():
        #waiting for the counter no from ui
        data = rospy.wait_for_message('/counter_no', String)
        if int(data.data) > 3:
            rospy.logerr("Enter counter no between 1-3")
            break
        rospy.loginfo('Recieved conter no '+ data.data)

        # publish the forward movement csv file name
        fwd_path = path + "counter_fwd" + data.data + ".csv"
        path_pub.publish(fwd_path)
        rospy.loginfo('publishing forward command')

        #wait for action to complete
        result1 = rospy.wait_for_message('/way_cmp', String)
        rospy.loginfo('Reached the counter')

        #call subprocess if needed
        rospy.sleep(3)

        # publish the forward movement csv file name
        rev_path = path + "counter_rev" + data.data + ".csv"
        path_pub.publish(rev_path)
        rospy.loginfo('publishing reverse command')

        #wait for action to complete
        result2 = rospy.wait_for_message('/way_cmp', String)
        rospy.loginfo('Reached the Home Position')

        #publish the result
        result_pub.publish("finished")

if __name__=="__main__":
    path = sys.argv[1]
    main(path)
