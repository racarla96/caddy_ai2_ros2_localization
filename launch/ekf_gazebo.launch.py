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

    start_ekf_node_cmd = Node(
        package='robot_localization',
        executable='ekf_node',
        name='ekf_filter_node',
        output='screen',
        parameters=[
            ekf_config_file,
            {'use_sim_time': use_sim_time}
        ]
    )

    ld = LaunchDescription()
    ld.add_action(declare_ekf_config_file_cmd)
    ld.add_action(declare_use_sim_time_cmd)
    ld.add_action(start_ekf_node_cmd)

    return ld
