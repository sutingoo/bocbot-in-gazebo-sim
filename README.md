# BocBot 🤖 — Simulación de Robot Móvil en Gazebo + ROS 2

BocBot es un **robot móvil autónomo de tracción diferencial (4 ruedas)** simulado en Gazebo Harmonic, diseñado para tareas de navegación, mapeo y evasión de obstáculos en entornos interiores estructurados.

Este repositorio contiene el workspace de ROS 2 (`bocbot_ws`) con el paquete `bocbot`, que integra el modelo del robot, los sensores y el entorno de simulación.

---

## 🧠 ¿Qué hace?

BocBot navega un entorno de oficina simulado (`boc_office.sdf`) con el objetivo de realizar **SLAM (Simultaneous Localization and Mapping)**: recorrer el espacio y construir un mapa 2D en tiempo real a partir de sus sensores.

### Componentes del robot

| Componente | Descripción |
|---|---|
| **Chasis y tracción** | Cuerpo central (`chassis`) con 4 ruedas (`front_left`, `front_right`, `back_left`, `back_right`) controladas por un sistema de tracción diferencial con odometría basada en giro de ruedas. |
| **Cámara** | Sensor RGB frontal (`camera_sensor`) con campo de visión amplio, listo para tareas de visión computacional. |
| **LiDAR** | Sensor láser tipo Hokuyo (`gpu_lidar`), barrido horizontal de -90° a 90°, alcance de hasta 30 metros. |
| **Entorno** | Mundo simulado `boc_office.sdf`: oficina cerrada con pasillos y habitaciones para probar navegación y evasión de obstáculos. |

---

## ⚙️ Stack tecnológico

- **ROS 2:** Jazzy Jalisco
- **Simulador:** Gazebo Harmonic (Ignition Gazebo)
- **Puente de comunicación:** [`ros_gz_bridge`](https://github.com/gazebosim/ros_gz) — traduce tópicos entre Gazebo y ROS 2
- **Mapeo:** `slam_toolbox`
- **Formato de mundo:** SDF 1.8

> **Nota:** este proyecto usa la arquitectura nativa de Gazebo Harmonic (`gz::sim::systems::DiffDrive`, `gz::sim::systems::Sensors`), no los plugins clásicos de Gazebo Classic.

---

## 📦 Estructura del workspace

```
bocbot_ws/
└── src/
    └── bocbot/
        ├── bocbot/          # Código fuente Python
        ├── launch/          # Archivos de lanzamiento (launch.py)
        ├── worlds/          # Mundo de simulación (boc_office.sdf)
        ├── urdf/            # Descripción del robot
        ├── config/          # Configuraciones (RViz, etc.)
        ├── maps/            # Mapas generados por SLAM
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
ros2 run rviz2 rviz2 --ros-args -p use_sim_time:=true
```

Configura manualmente (o carga `bocbot_view.rviz` si está disponible):
- **Fixed Frame:** `map`
- **Displays:** `RobotModel`, `LaserScan`, `Map`

### Terminal 4 — SLAM (mapeo)

```bash
ros2 launch slam_toolbox online_async_launch.py use_sim_time:=true params_file:=/opt/ros/jazzy/share/slam_toolbox/config/mapper_params_online_async.yaml
```

### Terminal 5 — Guardar el mapa

Una vez completado el recorrido en RViz2:

```bash
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
