import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node

def generate_launch_description():
    robot_name = 'bocbot'
    world_file_name = 'bocbot_office.sdf'

    pkg_bocbot = get_package_share_directory(robot_name)
    pkg_ros_gz_sim = get_package_share_directory('ros_gz_sim')

    world_path = os.path.join(pkg_bocbot, 'worlds', world_file_name)
    urdf_path = os.path.join(pkg_bocbot, 'urdf', 'bocbot.urdf')

    with open(urdf_path, 'r') as infp:
        robot_desc = infp.read()

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_ros_gz_sim, 'launch', 'gz_sim.launch.py')
        ),
        launch_arguments={'gz_args': f'-r -v 4 {world_path}'}.items(),
    )

    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='both',
        parameters=[{'robot_description': robot_desc, 'use_sim_time':True}],
    )

    spawn_entity = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-name', 'bocbot',
            '-topic', 'robot_description',
            '-z', '0.1'
        ],
        output='screen',
    )
    
    static_tf = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='static_transform_publisher_laser',
        arguments=[
            '0', '0', '0', '0', '0', '0',  
            'hokuyo',                      
            'bocbot/robot_footprint/head_hokuyo_sensor'  
        ],
        output='screen'
    )
    
    static_tf_hokuyo = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='static_transform_publisher_hokuyo',

        arguments=['0.15', '0', '0.15', '0', '0', '0', 'chassis', 'hokuyo'],
        output='screen'
    )
    
    static_tf_base_link = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='static_transform_publisher_base_link',
        arguments=['0', '0', '0', '0', '0', '0', 'base_link', 'robot_footprint'],
        output='screen'
    )

    static_tf_base_foot = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='static_transform_publisher_base_foot',
        arguments=['0', '0', '0', '0', '0', '0', 'base_footprint', 'robot_footprint'],
        output='screen'
    )

    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            # Motores y Odometría
            '/cmd_vel@geometry_msgs/msg/Twist@gz.msgs.Twist',
            '/odom@nav_msgs/msg/Odometry@gz.msgs.Odometry',
            '/tf@tf2_msgs/msg/TFMessage@gz.msgs.Pose_V',
            '/joint_states@sensor_msgs/msg/JointState@gz.msgs.Model',
            # Sensores (Lidar y Cámara)
            '/scan@sensor_msgs/msg/LaserScan@gz.msgs.LaserScan',
            '/camera/image_raw@sensor_msgs/msg/Image@gz.msgs.Image',
            '/camera/camera_info@sensor_msgs/msg/CameraInfo@gz.msgs.CameraInfo',
            '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock]'
        ],
        output='screen'
    )

    return LaunchDescription([
        gazebo,
        robot_state_publisher,
        spawn_entity,
        bridge,
        static_tf,
        static_tf_hokuyo,
        static_tf_base_link,
        static_tf_base_foot
    ])
