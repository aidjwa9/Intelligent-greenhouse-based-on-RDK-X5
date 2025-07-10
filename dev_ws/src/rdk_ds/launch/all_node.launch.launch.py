from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='rdk_ds',
            executable='audio_node',
            name='audio_node',
            output='screen',
        ),
        Node(
            package='rdk_ds',
            executable='control_node',
            name='control_node',
            output='screen',
        ),
        Node(
            package='rdk_ds',
            executable='deepseek_node',
            name='deepseek_node',
            output='screen',
        ),
        Node(
            package='rdk_ds',
            executable='sensor_node',
            name='sensor_node',
            output='screen',
        ),
        Node(
            package='rdk_ds',
            executable='mqtt_node',
            name='sensor_node',
            output='screen',
        ),
    ])