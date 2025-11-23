# 🎛️ Controlador MIDI con Visión por Computadora

Controlador MIDI de manos libres que utiliza gestos de manos detectados por cámara web para controlar instrumentos virtuales en Ableton Live (o cualquier DAW compatible con MIDI).

## 📸 Demo

Controla efectos con gestos de pinza y toca pads de batería con la palma de tu mano - todo sin tocar nada físico.

## ✨ Características

- **2 Sliders MIDI (CC)**: Controlados con gestos de pinza (pulgar + índice)
  - Mano izquierda → CC#20
  - Mano derecha → CC#21
  - Ideal para controlar filtros, reverb, delay, etc.

- **4 Pads de Batería**: Activados con la palma de la mano
  - Pad 1 (Rojo) → Nota 36 (Kick)
  - Pad 2 (Azul) → Nota 38 (Snare)
  - Pad 3 (Amarillo) → Nota 42 (Hi-hat cerrado)
  - Pad 4 (Verde) → Nota 46 (Hi-hat abierto)

- **Zonas Separadas**: Los sliders funcionan en la zona superior, los pads en la inferior - sin confusiones
- **Debouncing**: Evita triggers múltiples accidentales
- **Suavizado**: Valores MIDI suavizados para transiciones fluidas
- **Feedback Visual**: Interfaz colorida con indicadores en tiempo real

## 🛠️ Tecnologías y Librerías

### Python 3.7+

### Librerías Principales:
- **OpenCV (cv2)** - Captura y procesamiento de video de la cámara web
- **MediaPipe** - Detección y tracking de manos en tiempo real (Google)
- **mido** - Comunicación MIDI (envío de mensajes CC y notas)
- **NumPy** - Operaciones matemáticas y procesamiento de arrays

### Instalación de Dependencias:
```bash
