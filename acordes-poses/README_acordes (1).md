# 🎹 Acordes por Poses Corporales - MIDI Controller

Toca acordes musicales usando tu cuerpo completo como controlador MIDI. Este proyecto usa MediaPipe Pose para detectar poses corporales y enviar acordes a tu DAW favorito (Ableton Live, Logic Pro, etc.).

## ✨ Características

- **Control por Poses Corporales**: Todo tu cuerpo es el instrumento
- **3 Acordes Predefinidos**: Cmaj7, Fmaj7, G7
- **2 Modos de Reproducción**:
  - 🎹 **Acordes Completos**: Todas las notas suenan simultáneamente
  - 🎵 **Arpegiador**: Las notas suenan secuencialmente
- **Cambio de Modo Gestual**: Toca un botón virtual con tu dedo índice
- **Feedback Visual en Tiempo Real**: Ve tu esqueleto y landmarks

## 🎭 Poses para Acordes

| Acorde | Pose | Descripción |
|--------|------|-------------|
| **Cmaj7** | 🙋 | UN brazo extendido + piernas juntas |
| **Fmaj7** | 🙆 | AMBOS brazos extendidos + piernas juntas (forma de T) |
| **G7** | 🤸 | AMBOS brazos extendidos + piernas separadas (forma de estrella) |
| **NONE** | 🦩 | Parado en un pie (silencio) |

## 🔘 Botón de Cambio de Modo

- **Ubicación**: Esquina inferior izquierda de la pantalla
- **Control**: Toca con la punta de tu dedo índice
- **Estados**:
  - ⚫ **Gris**: Modo Acordes (todas las notas a la vez)
  - 🟢 **Verde**: Modo Arpegiador (notas secuenciales)

## 🛠️ Tecnologías

### Librerías Python:
- **MediaPipe Pose**: Detección de cuerpo completo (33 landmarks)
- **MediaPipe Hands**: Detección de manos para el botón
- **OpenCV**: Captura y procesamiento de video
- **mido**: Comunicación MIDI
- **python-rtmidi**: Backend MIDI para macOS

## 📦 Instalación

```bash
# Instalar dependencias
pip install opencv-python mediapipe mido python-rtmidi
```

O usar el archivo requirements.txt:

```bash
pip install -r requirements.txt
```

## 🚀 Configuración

### 1. Configurar IAC Driver (macOS)

1. Abre **Audio MIDI Setup** (Configuración de Audio MIDI)
2. **Ventana** → **Mostrar Estudio MIDI**
3. Doble clic en **IAC Driver**
4. Marca **"El dispositivo está en línea"**
5. Asegúrate de tener al menos un bus activo

### 2. Configurar tu DAW

#### Ableton Live:
1. **Preferencias** → **Link/Tempo/MIDI**
2. En **MIDI Ports**, activa **Track** y **Remote** para IAC Driver
3. Crea un instrumento MIDI en una pista
4. El instrumento recibirá las notas automáticamente

#### Logic Pro:
1. **Configuración** → **MIDI**
2. Habilita **IAC Driver Bus 1** como entrada
3. Crea una pista de instrumento de software
4. Selecciona IAC Driver como entrada MIDI

## 💻 Uso

```bash
python acordes_poses_mac.py
```

### Controles:

1. **Colócate frente a la cámara** (cuerpo completo visible)
2. **Haz una pose** para tocar un acorde:
   - Un brazo arriba = Cmaj7
   - Brazos en T = Fmaj7  
   - Estrella = G7
   - Un pie levantado = Silencio
3. **Toca el botón** con tu dedo índice para cambiar entre Acordes/Arpegiador
4. **Presiona 'q'** para salir

## 🎵 Acordes MIDI

Los acordes están en la octava 4:

```python
"Cmaj7": [60, 64, 67, 71]  # C4, E4, G4, B4
"Fmaj7": [65, 69, 72, 76]  # F4, A4, C5, E5
"G7":    [67, 71, 74, 77]  # G4, B4, D5, F5
```

## ⚙️ Personalización

### Cambiar los Acordes:

```python
CHORDS = {
    "NONE": [],
    "Cmaj7": [60, 64, 67, 71],  # Modifica las notas aquí
    "Fmaj7": [65, 69, 72, 76],
    "G7":    [67, 71, 74, 77]
}
```

### Agregar Más Acordes:

1. Define la pose en la función `get_pose_from_landmarks()`
2. Agrega el acorde al diccionario `CHORDS`

### Ajustar Velocidad del Arpegio:

```python
ARP_SPEED = 0.15  # Segundos entre notas (más bajo = más rápido)
```

### Cambiar Canal MIDI:

```python
NOTE_CHANNEL = 0  # Cambia a 1, 2, 3... según necesites
```

## 🔧 Requisitos del Sistema

- **Cámara web**: Resolución mínima 720p, recomendado 1080p
- **Python**: 3.7 o superior
- **Sistema Operativo**: macOS (IAC Driver nativo)
- **RAM**: 4GB mínimo, 8GB recomendado
- **CPU**: Procesador multi-núcleo para MediaPipe
- **Espacio**: Suficiente para capturar cuerpo completo

## 🎯 Casos de Uso

- **Composición expresiva**: Crea música con tu cuerpo
- **Live performances**: Actuaciones visuales únicas
- **Educación musical**: Enseña armonía de forma física
- **Terapia musical**: Combina movimiento y música
- **Instalaciones interactivas**: Arte sonoro corporal

## 🐛 Solución de Problemas

### La cámara no detecta mi cuerpo completo:
- Aléjate de la cámara
- Asegúrate de tener buena iluminación
- Verifica que todo tu cuerpo sea visible (cabeza a pies)

### Las poses no se detectan correctamente:
- Mejora la iluminación
- Usa ropa que contraste con el fondo
- Ajusta los umbrales en `get_pose_from_landmarks()`

### El botón no responde:
- Acerca más tu mano a la cámara
- Asegúrate de que la detección de manos esté activa
- Aumenta `TOUCH_THRESHOLD` en el código

### No hay sonido en el DAW:
- Verifica que IAC Driver esté habilitado
- Confirma que el DAW esté escuchando IAC Driver
- Revisa el volumen de tu pista MIDI

## 📝 Licencia

MIT License - Uso libre con atribución

## 🤝 Contribuciones

Ideas para mejorar:
- [ ] Más acordes y poses
- [ ] Detección de velocidad de movimiento
- [ ] Exportar poses personalizadas
- [ ] Control de octavas con gestos
- [ ] Modo de entrenamiento de poses
- [ ] Grabación de secuencias

## 🙏 Agradecimientos

- **MediaPipe** por su framework de detección de poses
- **OpenCV** por las herramientas de visión
- Comunidad de **música generativa** y **arte sonoro**

---

**¡Convierte tu cuerpo en un instrumento musical!** 🎵🕺
