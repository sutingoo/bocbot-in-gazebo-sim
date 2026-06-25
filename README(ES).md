# BocBot 🤖 — Simulación de Robot Móvil en Gazebo + ROS 2

<p align="center">
  <img src="docs/images/Screenshot from 2026-06-24 01-35-03.png" alt="BocBot navegando en Gazebo" width="700"/>
</p>

BocBot es un **robot móvil autónomo de tracción diferencial (4 ruedas)** simulado en Gazebo, diseñado para tareas de navegación, mapeo y evasión de obstáculos en entornos interiores estructurados.

Este proyecto está basado en la guía [**"Build Robot using ROS 2 and Gazebo"**](https://bunchofcoders.github.io/basic_bocbot/) de [bunchofcoders](https://github.com/bunchofcoders), originalmente escrita para **ROS 2 Eloquent** y **Gazebo Classic** (2020). Como ese stack ya quedó desactualizado, **migré el proyecto completo a ROS 2 Jazzy Jalisco y Gazebo Harmonic**, lo que implicó reescribir los plugins de simulación, adaptar el formato de mundo SDF y ajustar el flujo de tópicos a la nueva arquitectura de Gazebo. Ver la sección [Origen y migración](#-origen-y-migración) para el detalle completo de los cambios.

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

<p align="center">
  <img src="docs/images/Screenshot from 2026-06-22 18-07-39.png" alt="Modelo de BocBot" width="500"/>
</p>


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
├── LICENSE
├── Dockerfile
├── docker-compose.yml
├── .dockerignore
├── docker/
│   └── entrypoint.sh
├── docs/
│   └── images/          # Imágenes y GIFs usados en el README
└── src/
    └── bocbot/
        ├── CMakeLists.txt
        ├── include/bocbot/
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

## 🐳 Uso con Docker (alternativa recomendada)

Si no quieres instalar ROS2 Jazzy y Gazebo Harmonic manualmente, puedes usar el `Dockerfile` incluido. Esto evita problemas de versiones y dependencias.

### Requisitos

- [Docker](https://docs.docker.com/get-docker/) y [Docker Compose](https://docs.docker.com/compose/install/)
- Linux con servidor X11 (para que Gazebo/RViz puedan mostrar ventanas gráficas)

### Construir y levantar el contenedor

```bash
# Permite que el contenedor acceda a tu display (solo una vez por sesión)
xhost +local:docker

# Construye la imagen y levanta el contenedor
docker compose up --build -d

# Entra al contenedor
docker compose exec bocbot bash
```

Dentro del contenedor, el workspace ya está compilado y con el entorno cargado — puedes correr directamente los comandos de la sección [Cómo ejecutar](#️-cómo-ejecutar) (necesitarás varias terminales: usa `docker compose exec bocbot bash` en cada una).

> **Nota:** `docker-compose.yml` monta `./src` como volumen, así que los cambios que hagas en el código se reflejan sin reconstruir la imagen. Si agregas nuevas dependencias en `package.xml`, vuelve a correr `docker compose up --build`.

> **Windows/Mac:** la configuración de `DISPLAY` y X11 es distinta (necesitas [VcXsrv](https://sourceforge.net/projects/vcxsrv/) en Windows o [XQuartz](https://www.xquartz.org/) en Mac). Si usas estos sistemas, avísame y te ayudo a adaptar el `docker-compose.yml`.

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

<p align="center">
  <img src="docs/images/Peek 2026-06-25 01-55.gif" alt="SLAM en RViz2" width="600"/>
</p>

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

## 🔄 Origen y migración

Este proyecto parte de la guía [*Build Robot using ROS 2 and Gazebo*](https://bunchofcoders.github.io/basic_bocbot/), que enseña los fundamentos de URDF, plugins de Gazebo y el flujo básico de ROS 2 usando un robot de 4 ruedas con cámara y LiDAR (de ahí el nombre BocBot — **B**unch **o**f **C**oders **Bot**).

La guía original usa un stack que ya no se distribuye activamente (Eloquent llegó a su fin de vida en 2020, y Gazebo Classic está siendo reemplazado por Gazebo moderno). Adapté el proyecto completo al stack actual:

| Aspecto | Guía original | Este proyecto |
|---|---|---|
| ROS 2 | Eloquent (2019) | Jazzy Jalisco |
| Simulador | Gazebo Classic | Gazebo Harmonic |
| Plugin de tracción | `libgazebo_ros_diff_drive.so` | `gz::sim::systems::DiffDrive` |
| Plugin de cámara | `libgazebo_ros_camera.so` | Sistema de sensores nativo de Harmonic |
| Plugin de LiDAR | `libgazebo_ros_ray_sensor.so` | `gz::sim::systems::Sensors` (`gpu_lidar`) |
| Estado de las ruedas | No incluido | `gz::sim::systems::JointStatePublisher` (agregado) |
| Formato de mundo | `boc_office.world` (SDF 1.6) | `bocbot_office.sdf` (SDF 1.8) |
| Spawn del robot | Llamada manual al servicio `/spawn_entity` con XML escapado | `ros_gz_bridge` / herramientas nativas de Harmonic |
| Namespacing de tópicos | Todo bajo `/bocbot/*` | Sin namespace (`/cmd_vel`, `/scan`, `/odom`) |

Este cambio de arquitectura (plugins clásicos → sistemas nativos `gz::sim::systems`) no es solo un cambio de nombres: Gazebo Harmonic reorganizó por completo cómo los plugins se registran y comunican con ROS 2, así que fue necesario reescribir la configuración de sensores y el puente de comunicación desde cero.

---

## 🗺️ Roadmap

- [ ] Navegación autónoma con Nav2
- [ ] Pruebas automatizadas (`colcon test`)
- [ ] Soporte Docker para Windows/Mac (X11 forwarding)

---

## 📄 Licencia

Este proyecto está bajo la licencia MIT. Consulta el archivo [LICENSE](LICENSE) para más detalles.

El diseño base del robot y del mundo de simulación proviene de la guía de [bunchofcoders](https://github.com/bunchofcoders/basic_bocbot) — todo el crédito por el concepto original es de ellos. El código de este repositorio refleja la migración y adaptación al stack moderno (ROS 2 Jazzy + Gazebo Harmonic).
