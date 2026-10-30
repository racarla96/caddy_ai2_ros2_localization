#!/usr/bin/env python3
"""
Launch the Extended Kalman Filter node for the Caddy AI2 in Gazebo simulation.

Fuses wheel odometry (/bicycle_steering_controller/odometry) and IMU (/imu)
to produce a filtered odom → base_footprint transform.
"""

import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    package_name = 'caddy_ai2_ros2_localization'
    ekf_config_file_path = 'config/ekf.yaml'

    pkg_share = FindPackageShare(package=package_name).find(package_name)
    default_ekf_config_path = os.path.join(pkg_share, ekf_config_file_path)

    ekf_config_file = LaunchConfiguration('ekf_config_file')
    use_sim_time = LaunchConfiguration('use_sim_time')
    namespace = LaunchConfiguration('namespace')

    declare_ekf_config_file_cmd = DeclareLaunchArgument(
        name='ekf_config_file',
        default_value=default_ekf_config_path,
        description='Full path to the EKF configuration YAML file'
    )

    declare_use_sim_time_cmd = DeclareLaunchArgument(
        name='use_sim_time',
        default_value='true',
        description='Use simulation (Gazebo) clock if true'
    )

    declare_namespace_cmd = DeclareLaunchArgument(
        name='namespace',
        default_value='',
        description='ROS 2 namespace for the EKF node'
    )

    start_ekf_node_cmd = Node(
        package='robot_localization',
        executable='ekf_node',
        name='ekf_filter_node',
        namespace=namespace,
        output='screen',
        parameters=[
            ekf_config_file,
            {
                'use_sim_time': use_sim_time,
                'publish_tf': True,
                'odom_frame': 'odom',
                'base_link_frame': 'base_footprint',
                'world_frame': 'odom',
            }
        ],
        remappings=[
            ('tf', '/tf'),
            ('tf_static', '/tf_static'),
        ],
    )

    # navsat_transform_node converts GPS NavSatFix (lat/lon) → local Odometry (x/y)
    # and feeds it into the EKF as odom1 to anchor absolute position.
    start_navsat_transform_cmd = Node(
        package='robot_localization',
        executable='navsat_transform_node',
        name='navsat_transform_node',
        namespace=namespace,
        output='screen',
        parameters=[{
            'use_sim_time': use_sim_time,
            'magnetic_declination_radians': 0.0,
            'yaw_offset': 0.0,
            'zero_altitude': True,
            'broadcast_utm_transform': False,
            'publish_filtered_gps': False,
            'use_odometry_yaw': False,
            'wait_for_datum': False,
        }],
        remappings=[
            ('imu/data',           'sbg_ig500n/imu'),
            ('gps/fix',            'sbg_ig500n/navsat'),
            ('odometry/filtered',  'odometry/filtered'),
            ('tf',                 '/tf'),
            ('tf_static',          '/tf_static'),
        ],
    )

    ld = LaunchDescription()
    ld.add_action(declare_ekf_config_file_cmd)
    ld.add_action(declare_use_sim_time_cmd)
    ld.add_action(declare_namespace_cmd)
    ld.add_action(start_ekf_node_cmd)
    ld.add_action(start_navsat_transform_cmd)

    return ld
