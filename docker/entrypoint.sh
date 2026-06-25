#!/bin/bash
set -e

# Carga el entorno de ROS2 y del workspace antes de ejecutar cualquier comando
source /opt/ros/${ROS_DISTRO}/setup.bash
if [ -f /bocbot_ws/install/setup.bash ]; then
    source /bocbot_ws/install/setup.bash
fi

exec "$@"
