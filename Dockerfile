# syntax=docker/dockerfile:1
FROM osrf/ros:jazzy-desktop-full

# Evita prompts interactivos durante la instalación de paquetes
ENV DEBIAN_FRONTEND=noninteractive
ENV ROS_DISTRO=jazzy

# ---------------------------------------------------------------------------
# Dependencias del sistema y paquetes ROS2 necesarios para BocBot
# ---------------------------------------------------------------------------
RUN apt-get update && apt-get install -y --no-install-recommends \
    ros-${ROS_DISTRO}-ros-gz \
    ros-${ROS_DISTRO}-slam-toolbox \
    ros-${ROS_DISTRO}-nav2-map-server \
    ros-${ROS_DISTRO}-teleop-twist-keyboard \
    ros-${ROS_DISTRO}-xacro \
    python3-colcon-common-extensions \
    python3-rosdep \
    && rm -rf /var/lib/apt/lists/*

# ---------------------------------------------------------------------------
# Workspace
# ---------------------------------------------------------------------------
WORKDIR /bocbot_ws

# Copiamos solo el código fuente (build/install/log quedan fuera vía .dockerignore)
COPY src/ ./src/

# Instala dependencias declaradas en package.xml y compila
RUN . /opt/ros/${ROS_DISTRO}/setup.sh && \
    rosdep update --rosdistro=${ROS_DISTRO} && \
    rosdep install --from-paths src --ignore-src -r -y && \
    colcon build --symlink-install

# ---------------------------------------------------------------------------
# Entrypoint: hace source del workspace automáticamente en cada shell
# ---------------------------------------------------------------------------
RUN echo "source /opt/ros/${ROS_DISTRO}/setup.bash" >> /root/.bashrc && \
    echo "source /bocbot_ws/install/setup.bash" >> /root/.bashrc

COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
CMD ["bash"]
