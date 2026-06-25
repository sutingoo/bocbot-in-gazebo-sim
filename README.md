# BocBot 🤖 — Mobile Robot Simulation in Gazebo + ROS 2

<p align="center">
  <img src="docs/images/Screenshot from 2026-06-24 01-35-03.png" alt="BocBot navegando en Gazebo" width="700"/>
</p>


BocBot is an **autonomous differential drive mobile robot (4 wheels)** simulated in Gazebo, designed for navigation, mapping, and obstacle avoidance tasks in structured indoor environments.

This project is based on the [**"Build Robot using ROS 2 and Gazebo"**](https://bunchofcoders.github.io/basic_bocbot/) guide by [bunchofcoders](https://github.com/bunchofcoders), originally written for **ROS 2 Eloquent** and **Gazebo Classic** (2020). Since that stack is now outdated, **I migrated the entire project to ROS 2 Jazzy Jalisco and Gazebo Harmonic**. This involved rewriting the simulation plugins, adapting the SDF world format, and adjusting the topic flow to the new Gazebo architecture. See the [Origin and migration](#-origen-y-migración) section for full details on the changes.

---

## 🧠 What does it do?

BocBot navigates a simulated office environment (`bocbot_office.sdf`) with the goal of performing **SLAM (Simultaneous Localization and Mapping)**: traversing the space and building a 2D map in real-time using its sensors.

### Robot Components

| Component | Description |
| --- | --- |
| **Chassis and drive** | Central body (`chassis`, 15 kg) with 4 wheels (`front_left`, `front_right`, `back_left`, `back_right`) controlled by `gz::sim::systems::DiffDrive`. Wheel separation: 0.4 m, wheel radius: 0.1 m. Publishes odometry (`odom`) and wheel TFs. |
| **Camera** | RGB sensor (`camera_sensor`) with horizontal FOV of ~80° (1.3962634 rad), 800×800 resolution, 30 Hz. Publishes to `camera/image_raw`. |
| **LiDAR** | `gpu_lidar` sensor (`head_hokuyo_sensor`), horizontal scan from -90° to 90° (720 samples), range from 0.10 to 30 m, Gaussian noise (stddev 0.01), 40 Hz. Publishes to `scan`. |
| **Joint States** | `gz::sim::systems::JointStatePublisher` publishes the state of the 4 wheels to `joint_states`, for proper visualization in RViz2. |
| **Environment** | Simulated world `bocbot_office.sdf`: closed office with hallways and rooms to test navigation and obstacle avoidance. |

<p align="center">
  <img src="docs/images/Screenshot from 2026-06-22 18-07-39.png" alt="Modelo de BocBot" width="500"/>
</p>


---

## ⚙️ Tech Stack

* **ROS 2:** Jazzy Jalisco
* **Simulator:** Gazebo Harmonic (Ignition Gazebo)
* **Communication Bridge:** [`ros_gz_bridge`](https://github.com/gazebosim/ros_gz) — translates topics between Gazebo and ROS 2
* **Mapping:** `slam_toolbox`
* **World format:** SDF 1.8

> **Note:** this project uses the native Gazebo Harmonic architecture (`gz::sim::systems::DiffDrive`, `gz::sim::systems::Sensors`), not the classic Gazebo Classic plugins.

### Main ROS Topics

| Topic | Type | Description |
| --- | --- | --- |
| `/cmd_vel` | `geometry_msgs/Twist` | Velocity command (input) |
| `/odom` | `nav_msgs/Odometry` | Odometry calculated by `DiffDrive` |
| `/scan` | `sensor_msgs/LaserScan` | LiDAR data |
| `/camera/image_raw` | `sensor_msgs/Image` | Camera RGB image |
| `/joint_states` | `sensor_msgs/JointState` | Wheel states |
| `/tf` | `tf2_msgs/TFMessage` | Transformations (odom → base_footprint, wheels) |

---

## 📦 Workspace Structure

```
bocbot_ws/
├── README.md
├── LICENSE
├── Dockerfile
├── docker-compose.yml
├── .dockerignore
├── docker/
│   └── entrypoint.sh
├── docs/
│   └── images/          # Images and GIFs used in the README
└── src/
    └── bocbot/
        ├── CMakeLists.txt
        ├── include/bocbot/
        ├── src/                 # Source code
        ├── launch/
        │   └── launch.py        # Launches Gazebo + robot_state_publisher + ros_gz_bridge + static TFs
        ├── urdf/
        │   ├── bocbot.urdf
        │   ├── bocbot.urdf.xacro
        │   └── bocbot.gazebo
        ├── worlds/
        │   └── bocbot_office.sdf
        ├── rviz/
        │   └── bocbot_view.rviz
        └── package.xml

```

---

## 🚀 Installation

### Prerequisites

* Ubuntu 24.04
* [ROS 2 Jazzy Jalisco](https://docs.ros.org/en/jazzy/Installation.html)
* [Gazebo Harmonic](https://gazebosim.org/docs/harmonic/install)
* `ros_gz_bridge`
* `slam_toolbox`
* `teleop_twist_keyboard`
* `nav2_map_server`

### Clone and Build

```bash
git clone https://github.com/sutingoo/bocbot-in-gazebo-sim.git
cd bocbot-in-gazebo-sim
rosdep install --from-paths src --ignore-src -r -y
colcon build --symlink-install
source install/setup.bash

```

---

## 🐳 Usage with Docker (Recommended Alternative)

If you prefer not to install ROS2 Jazzy and Gazebo Harmonic manually, you can use the included `Dockerfile`. This avoids version and dependency issues.

### Requirements

* [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/install/)
* Linux with an X11 server (so Gazebo/RViz can display graphical windows)

### Build and Run the Container

```bash
# Allows the container to access your display (only needed once per session)
xhost +local:docker

# Builds the image and starts the container
docker compose up --build -d

# Enter the container
docker compose exec bocbot bash

```

Inside the container, the workspace is already built and the environment is sourced — you can directly run the commands from the [How to run](#️-how-to-run) section (you will need multiple terminals: use `docker compose exec bocbot bash` in each one).

> **Note:** `docker-compose.yml` mounts `./src` as a volume, so any changes you make to the code are reflected without rebuilding the image. If you add new dependencies in `package.xml`, run `docker compose up --build` again.

> **Windows/Mac:** The `DISPLAY` and X11 configuration is different (you need [VcXsrv](https://sourceforge.net/projects/vcxsrv/) on Windows or [XQuartz](https://www.xquartz.org/) on Mac). If you use these systems, let me know and I can help you adapt the `docker-compose.yml`.

---

## ▶️ How to Run

Full execution requires several terminals open simultaneously (all with `source install/setup.bash` already executed).

### Terminal 1 — Simulator and Base Nodes

Starts Gazebo Harmonic with the office environment, publishes the robot model, and establishes the ROS 2 ↔ Gazebo bridge along with static transformations.

```bash
ros2 launch bocbot launch.py

```

### Terminal 2 — Teleoperation

Control the robot with your keyboard (`U, I, O, J, K, L, M, ,, .`):

```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard

```

### Terminal 3 — RViz2 Visualization

```bash
ros2 run rviz2 rviz2 -d src/bocbot/rviz/bocbot_view.rviz --ros-args -p use_sim_time:=true

```

This automatically loads the saved configuration with **Fixed Frame:** `map` and the `RobotModel`, `LaserScan`, and `Map` displays.

### Terminal 4 — SLAM (Mapping)

<p align="center">
  <img src="docs/images/Peek 2026-06-25 01-55.gif" alt="SLAM en RViz2" width="600"/>
</p>

```bash
ros2 launch slam_toolbox online_async_launch.py use_sim_time:=true params_file:=/opt/ros/jazzy/share/slam_toolbox/config/mapper_params_online_async.yaml

```

### Terminal 5 — Saving the Map

Once you have finished navigating the area in RViz2, create the maps folder (if it doesn't exist) and export:

```bash
mkdir -p ~/bocbot_ws/src/bocbot/maps
ros2 run nav2_map_server map_saver_cli -f ~/bocbot_ws/src/bocbot/maps/my_office

```

This exports the map as a `.pgm`/`.png` file along with its metadata `.yaml` file.

---

## 🔄 Origin and Migration

This project stems from the guide [*Build Robot using ROS 2 and Gazebo*](https://bunchofcoders.github.io/basic_bocbot/), which teaches the fundamentals of URDF, Gazebo plugins, and the basic ROS 2 workflow using a 4-wheel robot equipped with a camera and LiDAR (hence the name BocBot — **B**unch **o**f **C**oders **Bot**).

The original guide uses a stack that is no longer actively distributed (Eloquent reached its End-of-Life in 2020, and Gazebo Classic is being replaced by modern Gazebo). I adapted the entire project to the current stack:

| Aspect | Original Guide | This Project |
| --- | --- | --- |
| ROS 2 | Eloquent (2019) | Jazzy Jalisco |
| Simulator | Gazebo Classic | Gazebo Harmonic |
| Drive Plugin | `libgazebo_ros_diff_drive.so` | `gz::sim::systems::DiffDrive` |
| Camera Plugin | `libgazebo_ros_camera.so` | Harmonic's native sensor system |
| LiDAR Plugin | `libgazebo_ros_ray_sensor.so` | `gz::sim::systems::Sensors` (`gpu_lidar`) |
| Wheel States | Not included | `gz::sim::systems::JointStatePublisher` (added) |
| World Format | `boc_office.world` (SDF 1.6) | `bocbot_office.sdf` (SDF 1.8) |
| Robot Spawning | Manual call to `/spawn_entity` service with escaped XML | `ros_gz_bridge` / native Harmonic tools |
| Topic Namespacing | Everything under `/bocbot/*` | No namespace (`/cmd_vel`, `/scan`, `/odom`) |

This architecture shift (classic plugins → native `gz::sim::systems`) is not merely a name change: Gazebo Harmonic completely reorganized how plugins are registered and how they communicate with ROS 2, making it necessary to rewrite the sensor configuration and communication bridge from scratch.

---

## 🗺️ Roadmap

* [ ] Autonomous navigation with Nav2
* [ ] Automated testing (`colcon test`)
* [ ] Docker support for Windows/Mac (X11 forwarding)

---

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

The base design of the robot and the simulation world originates from the [bunchofcoders](https://github.com/bunchofcoders/basic_bocbot) guide — all credit for the original concept goes to them. The code in this repository reflects the migration and adaptation to the modern stack (ROS 2 Jazzy + Gazebo Harmonic).
