# ros_waypoint_generator
This package generate waypoints for 2D navigation by using waypoints. It also contains the code to generate and save waypoints.   

### required

Launch any robot with the following options,
1. map server
2. navigation
3. rviz

### To generate Waypoints

To Start the waypoint generator  

```
rosrun ros_waypoint_generator ros_waypoint_generator_custom
```

Add waypoints by using the (2d nav goal) command in rviz .   

### To save Waypoints

Generated waypoints can be saved by launching the saver using the following command   
```
roslaunch ros_waypoint_generator waypoint_saver.launch direction:=fwd counter:=1
```
By default waypoints are stored under package ros_waypoint_generator/waypoints.  
arguments passed to the launch file are,
1. direction ,values = fwd or rev
2. counter, values = counter no 
3. path, values = /path/to/store/csvfile.   

for eg,   
roslaunch jackal_gazebo jackal_world.launch config:=front_laser
roslaunch jackal_navigation amcl_demo.launch map_file:=/path/to/my/map.yaml
roslaunch jackal_viz view_robot.launch config:=localization

### To follow waypoints

To start the follow waypoints node 
```
rosrun ros_waypoint_generator follow_waypoints_custom.py
```
To start following waypoints,path of the file(.csv) should be published under the topic /load_paths. for eg,  

```
rostopic pub /load_paths std_msgs/String "data: '/home/nare/way3.csv'" 
```
### Navigation based on conter number
To start the node that guides follow_waypoints node based on the counter number,  

```
rosrun ros_waypoint_generator ui_nav_waypoints.py /home/naren/office/ui_ws/src/ros_waypoint_generator/waypoints/
```
Path to the waypoints file should be passed as a argument as given above.  

To navigate based on the counter number,counter number can be published in the topic **/counter_no** as a string data. for eg,  

```
rostopic pub /counter_no std_msgs/String "data: '1'"
```
This command loads the corresponding csv file based on the counter no.   

### check waypoints
If you want to check the waypoints,   
```
rosrun ros_waypoint_generator ros_waypoint_server --load path/to/waypoints.csv
```
This can be viewed in rviz by adding the display **MarkerArray**

