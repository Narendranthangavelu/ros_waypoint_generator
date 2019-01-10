#include <ros/ros.h>

#include <nav_msgs/Odometry.h>
#include <geometry_msgs/PoseWithCovarianceStamped.h>
#include <std_msgs/Empty.h>
#include <interactive_markers/interactive_marker_server.h>
#include <interactive_markers/menu_handler.h>
#include <visualization_msgs/InteractiveMarkerInit.h>
#include <visualization_msgs/MarkerArray.h>
#include <tf/transform_broadcaster.h>
#include <tf/tf.h>
#include <ros/package.h>
#include <math.h>
#include <string>
#include <iostream>
#include <sstream>
#include <fstream>
#include <boost/tokenizer.hpp>
#include <boost/shared_array.hpp>
#include <boost/program_options.hpp>
#include <boost/date_time.hpp>

#include <ros_waypoint_generator/WaypointArray.h>

bool compareInteractiveMarker(visualization_msgs::InteractiveMarker left,
                              visualization_msgs::InteractiveMarker right)
{
  return std::stoi(left.name) < std::stoi(right.name);
}

std::string timeToStr()
{
    std::stringstream msg;
    const boost::posix_time::ptime now=
        boost::posix_time::second_clock::local_time();
    boost::posix_time::time_facet *const f=
        new boost::posix_time::time_facet("%Y-%m-%d-%H-%M-%S");
    msg.imbue(std::locale(msg.getloc(),f));
    msg << now;
    return msg.str();
}

class WaypointSaver
{
public:

  ros::Publisher pub;
  std_msgs::Empty myMsg;

  WaypointSaver(const std::string& waypoints_file):
    waypoints_file_(waypoints_file), saved_waypoints_(false)
  {
    ros::NodeHandle n;
    pub = n.advertise<std_msgs::Empty>("reset_path", 5);
    waypoints_sub_ = n.subscribe("/waypoints", 1, &WaypointSaver::waypointsCallback, this);
    ROS_INFO("Waiting for waypoints");
  }

  void waypointsCallback(ros_waypoint_generator::WaypointArray waypoints)
  {
    ROS_INFO("Received waypoints : %d", (int)waypoints.waypoints.size());

    std::ofstream savefile(waypoints_file_.c_str(), std::ios::out);
    //std::sort(all_markers.markers.begin(), all_markers.markers.end(), compareInteractiveMarker);
    size_t size = waypoints.waypoints.size();
    for(unsigned int i = 0; i < size; i++){
      //３次元の位置の指定
      savefile << waypoints.waypoints[i].pose.position.x << ","
               << waypoints.waypoints[i].pose.position.y << ","
               << 0 << ","
               << waypoints.waypoints[i].pose.orientation.x << ","
               << waypoints.waypoints[i].pose.orientation.y << ","
               << waypoints.waypoints[i].pose.orientation.z << ","
               << waypoints.waypoints[i].pose.orientation.w << ","
               << waypoints.waypoints[i].is_search_area << ","
               << waypoints.waypoints[i].reach_tolerance * 2.0 << std::endl;
      ROS_INFO_STREAM("Num: " << waypoints.waypoints[i].number);
    }
    saved_waypoints_ = true;
    ROS_INFO_STREAM("Saved to : " << waypoints_file_);
    
    pub.publish(myMsg);
  }
  
  std::string waypoints_file_;
  ros::Subscriber waypoints_sub_;
  bool saved_waypoints_;
};

int main(int argc, char** argv)
{
  
  ros::init(argc, argv, "waypoint_saver");
  //std::string path = ros::package::getpath("ros_waypoint_generator");
  //auto path_ = path + "/waypoints/counter_";
  //std::string waypoints_name = "naren" + ".csv";
  std::string path1,path2,path3,waypoints_name;

  /*path for storing files */
  path1 = argv[1];
  path2 = argv[2];
  path3 = argv[3];
 
  //std::string waypoints_name = path + ".csv";
  waypoints_name = path1  + "/waypoints/counter_" + path2 + path3 + ".csv";
  std::cout << waypoints_name;
  WaypointSaver saver(waypoints_name);
  while(!saver.saved_waypoints_ && ros::ok())
  {
    ros::spinOnce();
  }
  
  return 0;
}
