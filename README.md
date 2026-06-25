# BocBot 🤖 — Simulación de Robot Móvil en Gazebo + ROS 2

BocBot es un **robot móvil autónomo de tracción diferencial (4 ruedas)** simulado en Gazebo Harmonic, diseñado para tareas de navegación, mapeo y evasión de obstáculos en entornos interiores estructurados.

Este repositorio contiene el workspace de ROS 2 (`bocbot_ws`) con el paquete `bocbot`, que integra el modelo del robot, los sensores y el entorno de simulación.

---

## 🧠 ¿Qué hace?

BocBot navega un entorno de oficina simulado (`bocbot_office.sdf`) con el objetivo de realizar **SLAM (Simultaneous Localization and Mapping)**: recorrer el espacio y construir un mapa 2D en tiempo real a partir de sus sensores.

### Componentes del robot

| Componente | Descripción |
|---|---|
| **Chasis y tracción** | Cuerpo central (`chassis`, 15 kg) con 4 ruedas (`front_left`, `front_right`, `back_left`, `back_right`) controladas por `gz::sim::systems::DiffDrive`. Separación entre ruedas: 0.4 m, radio de rueda: 0.1 m. Publica odometría (`odom`) y TFs de ruedas. |
| **Cámara** | Sensor RGB (`camera_sensor`) con FOV horizontal de ~80° (1.3962634 rad), resolución 800×800, 30 Hz. Publica en `camera/image_raw`. |
| **LiDAR** | Sensor `gpu_lidar` (`head_hokuyo_sensor`), barrido horizontal de -90° a 90° (720 muestras), rango de 0.10 a 30 m, ruido gaussiano (stddev 0.01), 40 Hz. Publica en `scan`. |
| **Joint States** | `gz::sim::systems::JointStatePublisher` publica el estado de las 4 ruedas en `joint_states`, para visualización correcta en RViz2. |
| **Entorno** | Mundo simulado `bocbot_office.sdf`: oficina cerrada con pasillos y habitaciones para probar navegación y evasión de obstáculos. |

---

## ⚙️ Stack tecnológico

- **ROS 2:** Jazzy Jalisco
- **Simulador:** Gazebo Harmonic (Ignition Gazebo)
- **Puente de comunicación:** [`ros_gz_bridge`](https://github.com/gazebosim/ros_gz) — traduce tópicos entre Gazebo y ROS 2
- **Mapeo:** `slam_toolbox`
- **Formato de mundo:** SDF 1.8

> **Nota:** este proyecto usa la arquitectura nativa de Gazebo Harmonic (`gz::sim::systems::DiffDrive`, `gz::sim::systems::Sensors`), no los plugins clásicos de Gazebo Classic.

### Tópicos ROS principales

| Tópico | Tipo | Descripción |
|---|---|---|
| `/cmd_vel` | `geometry_msgs/Twist` | Comando de velocidad (entrada) |
| `/odom` | `nav_msgs/Odometry` | Odometría calculada por `DiffDrive` |
| `/scan` | `sensor_msgs/LaserScan` | Datos del LiDAR |
| `/camera/image_raw` | `sensor_msgs/Image` | Imagen RGB de la cámara |
| `/joint_states` | `sensor_msgs/JointState` | Estado de las ruedas |
| `/tf` | `tf2_msgs/TFMessage` | Transformaciones (odom → base_footprint, ruedas) |

---

## 📦 Estructura del workspace

```
bocbot_ws/
├── README.md
└── src/
    └── bocbot/
        ├── CMakeLists.txt
        ├── include/bocbot/      # Headers (C++)
        ├── src/                 # Código fuente
        ├── launch/
        │   └── launch.py        # Lanza Gazebo + robot_state_publisher + ros_gz_bridge + TFs estáticas
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

## 🚀 Instalación

### Requisitos previos

- Ubuntu 24.04
- [ROS 2 Jazzy Jalisco](https://docs.ros.org/en/jazzy/Installation.html)
- [Gazebo Harmonic](https://gazebosim.org/docs/harmonic/install)
- `ros_gz_bridge`
- `slam_toolbox`
- `teleop_twist_keyboard`
- `nav2_map_server`

### Clonar y compilar

```bash
git clone https://github.com/sutingoo/bocbot-in-gazebo-sim.git
cd bocbot-in-gazebo-sim
rosdep install --from-paths src --ignore-src -r -y
colcon build --symlink-install
source install/setup.bash
```

---

## ▶️ Cómo ejecutar

La ejecución completa requiere varias terminales abiertas en simultáneo (todas con `source install/setup.bash` ya ejecutado).

### Terminal 1 — Simulador y nodos base

Levanta Gazebo Harmonic con la oficina, publica el modelo del robot, establece el puente ROS 2 ↔ Gazebo y las transformaciones estáticas.

```bash
ros2 launch bocbot launch.py
```

### Terminal 2 — Teleoperación

Controla al robot con el teclado (`U, I, O, J, K, L, M, ,, .`):

```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

### Terminal 3 — Visualización en RViz2

```bash
ros2 run rviz2 rviz2 -d src/bocbot/rviz/bocbot_view.rviz --ros-args -p use_sim_time:=true
```

Esto carga automáticamente la configuración guardada con **Fixed Frame:** `map` y los displays de `RobotModel`, `LaserScan` y `Map`.

### Terminal 4 — SLAM (mapeo)

```bash
ros2 launch slam_toolbox online_async_launch.py use_sim_time:=true params_file:=/opt/ros/jazzy/share/slam_toolbox/config/mapper_params_online_async.yaml
```

### Terminal 5 — Guardar el mapa

Una vez completado el recorrido en RViz2, crea la carpeta de mapas (si no existe) y exporta:

```bash
mkdir -p ~/bocbot_ws/src/bocbot/maps
ros2 run nav2_map_server map_saver_cli -f ~/bocbot_ws/src/bocbot/maps/mi_oficina
```

Esto exporta el mapa como `.pgm`/`.png` junto con su `.yaml` de metadatos.

---

## 🗺️ Roadmap

- [ ] Navegación autónoma con Nav2
- [ ] Dockerfile para entorno reproducible
- [ ] Pruebas automatizadas (`colcon test`)

---

## 📄 Licencia

Pendiente de definir.
