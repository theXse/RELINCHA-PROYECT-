import cv2
import mediapipe as mp
import mido
import numpy as np
from collections import deque

# ============================================
# CONFIGURACIÓN
# ============================================

# MIDI
MIDI_CHANNEL = 0
SLIDER_LEFT_CC = 20   # CC para slider izquierdo (mano izquierda)
SLIDER_RIGHT_CC = 21  # CC para slider derecho (mano derecha)

# Configuración de Pads (Notas MIDI para Drum Rack)
PAD_1_NOTE = 36  # C1 - Kick
PAD_2_NOTE = 38  # D1 - Snare
PAD_3_NOTE = 42  # F#1 - Hi-hat cerrado
PAD_4_NOTE = 46  # A#1 - Hi-hat abierto
PAD_VELOCITY = 100

# Configuración de cámara
CAMERA_WIDTH = 1280
CAMERA_HEIGHT = 720

# Configuración de sliders (pinza)
PINCH_MIN_DISTANCE = 20   # Distancia mínima de pinza (cerrada) = 0
PINCH_MAX_DISTANCE = 200  # Distancia máxima de pinza (abierta) = 127
SLIDER_BAR_HEIGHT = 60    # Altura de la barra visual
SLIDER_BAR_WIDTH = 500    # Ancho de la barra visual
SLIDER_Y_TOP = 150        # Posición Y del slider superior (mano izq)
SLIDER_Y_BOTTOM = 250     # Posición Y del slider inferior (mano der)

# Zona de activación de sliders - MEJORADA
SLIDER_ACTIVATION_MARGIN = 100  # Reducido de 150 a 100
SLIDER_MIN_Y = 80         # NUEVO: Límite superior de zona de sliders
SLIDER_MAX_Y = 380        # NUEVO: Límite inferior de zona de sliders

# Configuración de Pads - MEJORADA
PAD_SIZE = 140            # Tamaño visual del pad
PAD_TOUCH_AREA = 170      # Área de detección (reducido de 200 a 170)
PAD_MARGIN = 50           # Margen desde las esquinas
PAD_MIN_Y = 420           # NUEVO: Los pads solo funcionan DEBAJO de esta línea

# Configuración de suavizado
SMOOTHING_WINDOW = 7      # Ventana de promediado móvil (más suavizado)

# Colores vibrantes y fuertes
SLIDER_BG_COLOR = (20, 20, 20)
SLIDER_BORDER_LEFT = (255, 0, 255)    # Magenta fuerte
SLIDER_BORDER_RIGHT = (0, 255, 255)   # Cyan fuerte
SLIDER_FILL_LEFT = (255, 50, 255)     # Magenta brillante
SLIDER_FILL_RIGHT = (50, 255, 255)    # Cyan brillante

# Colores de Pads - Mucho más vibrantes
PAD_COLORS = [
    (0, 0, 255),      # Rojo puro - Pad 1 (Kick)
    (255, 0, 0),      # Azul puro - Pad 2 (Snare)
    (0, 255, 255),    # Amarillo puro - Pad 3 (Hi-hat cerrado)
    (0, 255, 0)       # Verde puro - Pad 4 (Hi-hat abierto)
]
PAD_ACTIVE_COLOR = (255, 255, 255)

# Colores de manos
HAND_LEFT_COLOR = (255, 0, 200)       # Rosa/Magenta
HAND_RIGHT_COLOR = (0, 200, 255)      # Cyan
PINCH_LINE_COLOR = (255, 255, 0)      # Amarillo

# ============================================
# INICIALIZACIÓN MIDI
# ============================================

print("🎛️  CONTROLADOR MIDI MEJORADO - 2 PINZAS + 4 PADS")
print("=" * 65)

# Buscar puerto MIDI (IAC Driver en Mac)
ports = mido.get_output_names()
print("\n📡 Puertos MIDI disponibles:")
for i, p in enumerate(ports):
    print(f"  {i+1}. {p}")

port_name = None
for p in ports:
    if "IAC" in p or "Bus" in p:
        port_name = p
        break

if not port_name and ports:
    port_name = ports[0]

if not port_name:
    print("\n❌ No se encontró ningún puerto MIDI")
    print("💡 Habilita IAC Driver en 'Configuración MIDI de Audio'")
    exit()

try:
    midi_out = mido.open_output(port_name)
    print(f"\n✅ MIDI conectado: {port_name}")
    print(f"\n🤏 SLIDERS (Control con Pinza - ZONA SUPERIOR):")
    print(f"   Mano IZQUIERDA (Magenta) → CC#{SLIDER_LEFT_CC}")
    print(f"   Mano DERECHA (Cyan) → CC#{SLIDER_RIGHT_CC}")
    print(f"   ⚠️  Solo funcionan en la ZONA SUPERIOR (barras iluminadas)")
    print(f"\n🥁 PADS (Notas MIDI - ZONA INFERIOR):")
    print(f"   Pad 1 (Rojo) → Nota {PAD_1_NOTE} (C1)")
    print(f"   Pad 2 (Azul) → Nota {PAD_2_NOTE} (D1)")
    print(f"   Pad 3 (Amarillo) → Nota {PAD_3_NOTE} (F#1)")
    print(f"   Pad 4 (Verde) → Nota {PAD_4_NOTE} (A#1)")
    print(f"   ⚠️  Solo funcionan en la ZONA INFERIOR (círculos abajo)")
except Exception as e:
    print(f"\n❌ Error al abrir puerto MIDI: {e}")
    exit()

# ============================================
# INICIALIZACIÓN MEDIAPIPE
# ============================================

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=2,  # Dos manos para controlar dos sliders
    min_detection_confidence=0.7,
    min_tracking_confidence=0.8,
    model_complexity=1
)

# ============================================
# INICIALIZACIÓN CÁMARA
# ============================================

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_WIDTH)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)
cap.set(cv2.CAP_PROP_FPS, 60)
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

if not cap.isOpened():
    print("\n❌ No se pudo abrir la cámara")
    exit()

print("✅ Cámara iniciada")
print("\n📝 Instrucciones:")
print("   • SLIDERS: Haz gesto de PINZA en la ZONA SUPERIOR")
print("     - La zona está claramente marcada con rectángulos")
print("     - Cerrada = 0 | Abierta = 127")
print("   • PADS: Coloca la PALMA en la ZONA INFERIOR")
print("     - Solo funcionan DEBAJO de la línea amarilla")
print("     - Zonas totalmente SEPARADAS para evitar confusión")
print("   • Presiona 'q' o 'ESC' para salir")
print("=" * 65)

# ============================================
# CLASE SLIDER (PINZA)
# ============================================

class PinchSlider:
    def __init__(self, y_position, cc_number, label, color_border, color_fill, hand_type):
        self.y = y_position
        self.cc_number = cc_number
        self.label = label
        self.color_border = color_border
        self.color_fill = color_fill
        self.hand_type = hand_type  # "Left" o "Right"
        
        # Calcular X centrado
        self.x = (CAMERA_WIDTH - SLIDER_BAR_WIDTH) // 2
        self.width = SLIDER_BAR_WIDTH
        self.height = SLIDER_BAR_HEIGHT
        
        # Definir zona de activación (área donde la pinza activa el slider)
        self.activation_x_min = self.x - SLIDER_ACTIVATION_MARGIN
        self.activation_x_max = self.x + self.width + SLIDER_ACTIVATION_MARGIN
        self.activation_y_min = max(SLIDER_MIN_Y, self.y - SLIDER_ACTIVATION_MARGIN)
        self.activation_y_max = min(SLIDER_MAX_Y, self.y + self.height + SLIDER_ACTIVATION_MARGIN)
        
        # Valor actual (0-127)
        self.value = 0
        self.pinch_distance = 0
        
        # Estado
        self.is_active = False
        self.is_in_zone = False  # Si la mano está en la zona de activación
        
        # Buffer para suavizado
        self.value_history = deque(maxlen=SMOOTHING_WINDOW)
        for _ in range(SMOOTHING_WINDOW):
            self.value_history.append(0)
        
        # Último valor enviado por MIDI
        self.last_sent_value = -1
    
    def is_in_activation_zone(self, x, y):
        """Verifica si una posición está dentro de la zona de activación del slider"""
        in_x = self.activation_x_min <= x <= self.activation_x_max
        in_y = self.activation_y_min <= y <= self.activation_y_max
        # CRÍTICO: No activar si está en zona de pads
        not_in_pad_zone = y < PAD_MIN_Y
        return in_x and in_y and not_in_pad_zone
    
    def update_from_pinch(self, distance, pinch_center_x, pinch_center_y):
        """Actualiza el valor basado en la distancia de pinza (solo si está en zona)"""
        # Verificar si está en zona de activación
        self.is_in_zone = self.is_in_activation_zone(pinch_center_x, pinch_center_y)
        
        if not self.is_in_zone:
            self.is_active = False
            return
        
        self.pinch_distance = distance
        self.is_active = True
        
        # Clampear la distancia dentro del rango
        distance = max(PINCH_MIN_DISTANCE, min(distance, PINCH_MAX_DISTANCE))
        
        # Mapear a rango 0-127
        normalized = (distance - PINCH_MIN_DISTANCE) / (PINCH_MAX_DISTANCE - PINCH_MIN_DISTANCE)
        midi_value = int(normalized * 127)
        
        # Agregar al buffer de suavizado
        self.value_history.append(midi_value)
        
        # Calcular promedio suavizado
        self.value = int(sum(self.value_history) / len(self.value_history))
    
    def send_midi_if_changed(self, midi_out):
        """Envía mensaje MIDI solo si el valor cambió (con deadzone de 2)"""
        if abs(self.value - self.last_sent_value) >= 2:  # DEADZONE
            msg = mido.Message('control_change',
                              channel=MIDI_CHANNEL,
                              control=self.cc_number,
                              value=self.value)
            midi_out.send(msg)
            self.last_sent_value = self.value
    
    def draw(self, frame):
        """Dibuja el slider horizontal en el frame"""
        # Dibujar zona de activación (más visible cuando está activa)
        if self.is_in_zone:
            zone_alpha = 0.25
        else:
            zone_alpha = 0.08
        
        zone_overlay = frame.copy()
        cv2.rectangle(zone_overlay,
                     (self.activation_x_min, self.activation_y_min),
                     (self.activation_x_max, self.activation_y_max),
                     self.color_border, -1)
        cv2.addWeighted(zone_overlay, zone_alpha, frame, 1-zone_alpha, 0, frame)
        
        # Borde de zona de activación
        border_thickness = 3 if self.is_in_zone else 2
        cv2.rectangle(frame,
                     (self.activation_x_min, self.activation_y_min),
                     (self.activation_x_max, self.activation_y_max),
                     self.color_border, border_thickness)
        
        # Texto indicador de zona
        if self.y == SLIDER_Y_TOP:
            zone_text = "ZONA DE SLIDERS (EFECTOS)"
            text_size = cv2.getTextSize(zone_text, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)[0]
            text_x = (CAMERA_WIDTH - text_size[0]) // 2
            
            # Fondo negro para el texto
            cv2.rectangle(frame,
                         (text_x - 10, SLIDER_MIN_Y - 35),
                         (text_x + text_size[0] + 10, SLIDER_MIN_Y - 5),
                         (0, 0, 0), -1)
            
            cv2.putText(frame, zone_text,
                       (text_x, SLIDER_MIN_Y - 12),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # Fondo oscuro del slider
        cv2.rectangle(frame,
                     (self.x - 5, self.y - 5),
                     (self.x + self.width + 5, self.y + self.height + 5),
                     (10, 10, 10), -1)
        
        # Borde del slider
        thickness = 4 if self.is_active else 3
        cv2.rectangle(frame,
                     (self.x, self.y),
                     (self.x + self.width, self.y + self.height),
                     self.color_border, thickness)
        
        # Calcular ancho del fill
        fill_width = int((self.value / 127) * self.width)
        
        # Relleno del slider (de izquierda a derecha)
        if fill_width > 0:
            cv2.rectangle(frame,
                         (self.x + 3, self.y + 3),
                         (self.x + fill_width - 3, self.y + self.height - 3),
                         self.color_fill, -1)
        
        # Línea indicadora del valor actual
        indicator_x = self.x + fill_width
        if fill_width > 0:
            cv2.line(frame,
                    (indicator_x, self.y - 10),
                    (indicator_x, self.y + self.height + 10),
                    (255, 255, 255), 3)
        
        # Valor numérico (a la izquierda)
        value_text = f"{self.value}"
        cv2.putText(frame, value_text,
                   (self.x - 60, self.y + 45),
                   cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 3)
        
        # Etiqueta (arriba del slider)
        label_text = f"{self.label} - CC{self.cc_number}"
        cv2.putText(frame, label_text,
                   (self.x, self.y - 15),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, self.color_border, 2)
        
        # Etiqueta de mano
        hand_label = "MANO IZQ" if self.hand_type == "Left" else "MANO DER"
        cv2.putText(frame, hand_label,
                   (self.x + self.width - 150, self.y - 15),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, self.color_border, 2)
        
        # Marcas de nivel
        marks = [0, self.width // 2, self.width]
        mark_values = ["0", "64", "127"]
        for mark_x_rel, mark_text in zip(marks, mark_values):
            mark_x = self.x + mark_x_rel
            cv2.line(frame,
                    (mark_x, self.y + self.height),
                    (mark_x, self.y + self.height + 8),
                    (100, 100, 100), 2)
            text_size = cv2.getTextSize(mark_text, cv2.FONT_HERSHEY_SIMPLEX, 0.4, 1)[0]
            cv2.putText(frame, mark_text,
                       (mark_x - text_size[0] // 2, self.y + self.height + 25),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (150, 150, 150), 1)
        
        # Si está activo, mostrar distancia de pinza
        if self.is_active:
            distance_text = f"Pinza: {int(self.pinch_distance)}px"
            cv2.putText(frame, distance_text,
                       (self.x + self.width // 2 - 80, self.y + self.height // 2 + 8),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)

# ============================================
# CLASE PAD (CON DEBOUNCING)
# ============================================

class Pad:
    def __init__(self, x, y, size, touch_area, note, label, color):
        self.x = x
        self.y = y
        self.size = size
        self.touch_area = touch_area
        self.note = note
        self.label = label
        self.color = color
        
        # Calcular centro del pad
        self.center_x = x + size // 2
        self.center_y = y + size // 2
        
        # Estado
        self.is_active = False
        self.was_touching = False
        self.activation_time = 0
        self.activation_duration = 0.15
        
        # NUEVO: Debouncing
        self.last_trigger_time = 0
        self.debounce_time = 0.12  # 120ms entre triggers
    
    def check_touch_with_palm(self, palm_x, palm_y):
        """Verifica si la palma de la mano está tocando el pad"""
        # CRÍTICO: Solo funcionar en zona de pads (debajo de la línea)
        if palm_y < PAD_MIN_Y:
            self.was_touching = False
            return False
        
        # Calcular distancia al centro del pad
        dx = palm_x - self.center_x
        dy = palm_y - self.center_y
        distance = (dx**2 + dy**2)**0.5
        
        # Área circular de detección
        is_touching = distance < (self.touch_area / 2)
        
        # Detectar momento del toque (flanco de subida)
        if is_touching and not self.was_touching:
            self.trigger()
        
        self.was_touching = is_touching
        return is_touching
    
    def trigger(self):
        """Activa el pad y envía nota MIDI (con debouncing)"""
        import time
        current_time = time.time()
        
        # DEBOUNCING: Evitar triggers múltiples
        if current_time - self.last_trigger_time < self.debounce_time:
            return
        
        self.last_trigger_time = current_time
        self.is_active = True
        self.activation_time = current_time
        
        # Enviar Note ON
        msg_on = mido.Message('note_on',
                             channel=MIDI_CHANNEL,
                             note=self.note,
                             velocity=PAD_VELOCITY)
        midi_out.send(msg_on)
        
        print(f"🥁 {self.label} → Nota {self.note}")
    
    def update(self):
        """Actualiza el estado del pad (para animación y note off)"""
        import time
        if self.is_active:
            elapsed = time.time() - self.activation_time
            
            if elapsed > self.activation_duration:
                msg_off = mido.Message('note_off',
                                      channel=MIDI_CHANNEL,
                                      note=self.note,
                                      velocity=0)
                midi_out.send(msg_off)
                self.is_active = False
    
    def draw(self, frame):
        """Dibuja el pad en el frame con área de detección visible"""
        # Dibujar área de detección (círculo translúcido)
        overlay = frame.copy()
        cv2.circle(overlay, (self.center_x, self.center_y),
                  self.touch_area // 2, self.color, -1)
        cv2.addWeighted(overlay, 0.15, frame, 0.85, 0, frame)
        
        # Borde del área de detección
        cv2.circle(frame, (self.center_x, self.center_y),
                  self.touch_area // 2, self.color, 2)
        
        # Color del pad según estado
        if self.is_active:
            pad_color = PAD_ACTIVE_COLOR
            border_thickness = 8
            glow_size = 35
        else:
            pad_color = self.color
            border_thickness = 5
            glow_size = 0
        
        # Efecto de brillo cuando está activo
        if glow_size > 0:
            for i in range(3):
                alpha = 0.3 - (i * 0.1)
                glow_overlay = frame.copy()
                cv2.rectangle(glow_overlay,
                            (self.x - glow_size + i*10, self.y - glow_size + i*10),
                            (self.x + self.size + glow_size - i*10, self.y + self.size + glow_size - i*10),
                            pad_color, -1)
                cv2.addWeighted(glow_overlay, alpha, frame, 1-alpha, 0, frame)
        
        # Fondo del pad
        cv2.rectangle(frame,
                     (self.x, self.y),
                     (self.x + self.size, self.y + self.size),
                     pad_color, -1)
        
        # Borde del pad
        cv2.rectangle(frame,
                     (self.x, self.y),
                     (self.x + self.size, self.y + self.size),
                     (255, 255, 255), border_thickness)
        
        # Etiqueta centrada (más grande)
        label_size = cv2.getTextSize(self.label, cv2.FONT_HERSHEY_SIMPLEX, 1.0, 3)[0]
        label_x = self.x + (self.size - label_size[0]) // 2
        label_y = self.y + (self.size + label_size[1]) // 2
        
        # Sombra del texto
        cv2.putText(frame, self.label,
                   (label_x + 3, label_y + 3),
                   cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 0), 5)
        
        # Texto principal
        cv2.putText(frame, self.label,
                   (label_x, label_y),
                   cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 0), 3)
        
        # Número de nota (abajo)
        note_text = f"N:{self.note}"
        note_size = cv2.getTextSize(note_text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)[0]
        note_x = self.x + (self.size - note_size[0]) // 2
        note_y = self.y + self.size - 15
        
        cv2.putText(frame, note_text,
                   (note_x, note_y),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)

# ============================================
# CREAR SLIDERS Y PADS
# ============================================

sliders = [
    PinchSlider(SLIDER_Y_TOP, SLIDER_LEFT_CC, "SLIDER 1", 
                SLIDER_BORDER_LEFT, SLIDER_FILL_LEFT, "Left"),
    PinchSlider(SLIDER_Y_BOTTOM, SLIDER_RIGHT_CC, "SLIDER 2", 
                SLIDER_BORDER_RIGHT, SLIDER_FILL_RIGHT, "Right")
]

# Reposicionar pads más abajo para mayor separación
pad_y_top = CAMERA_HEIGHT - 2*PAD_MARGIN - 2*PAD_SIZE - 20
pad_y_bottom = CAMERA_HEIGHT - PAD_MARGIN - PAD_SIZE

pads = [
    # Pad 1 - Inferior Izquierda (Kick - Rojo)
    Pad(PAD_MARGIN, pad_y_top, PAD_SIZE, PAD_TOUCH_AREA, 
        PAD_1_NOTE, "PAD 1", PAD_COLORS[0]),
    
    # Pad 2 - Inferior Derecha (Snare - Azul)
    Pad(CAMERA_WIDTH - PAD_MARGIN - PAD_SIZE, pad_y_top, PAD_SIZE, PAD_TOUCH_AREA,
        PAD_2_NOTE, "PAD 2", PAD_COLORS[1]),
    
    # Pad 3 - Más Inferior Izquierda (Hi-hat cerrado - Amarillo)
    Pad(PAD_MARGIN, pad_y_bottom, PAD_SIZE, PAD_TOUCH_AREA,
        PAD_3_NOTE, "PAD 3", PAD_COLORS[2]),
    
    # Pad 4 - Más Inferior Derecha (Hi-hat abierto - Verde)
    Pad(CAMERA_WIDTH - PAD_MARGIN - PAD_SIZE, pad_y_bottom, PAD_SIZE, PAD_TOUCH_AREA,
        PAD_4_NOTE, "PAD 4", PAD_COLORS[3])
]

# ============================================
# FUNCIONES DE DETECCIÓN
# ============================================

def get_pinch_distance(hand_landmarks, w, h):
    """Calcula la distancia entre el pulgar y el índice (pinza)"""
    thumb_tip = hand_landmarks.landmark[4]
    index_tip = hand_landmarks.landmark[8]
    
    thumb_x = int(thumb_tip.x * w)
    thumb_y = int(thumb_tip.y * h)
    index_x = int(index_tip.x * w)
    index_y = int(index_tip.y * h)
    
    distance = ((thumb_x - index_x)**2 + (thumb_y - index_y)**2)**0.5
    
    # Calcular centro de la pinza (punto medio entre pulgar e índice)
    center_x = (thumb_x + index_x) // 2
    center_y = (thumb_y + index_y) // 2
    
    return distance, (thumb_x, thumb_y), (index_x, index_y), (center_x, center_y)

def get_palm_center(hand_landmarks, w, h):
    """Obtiene la posición del centro de la palma de la mano"""
    # Landmark 0 = Centro de la muñeca (base de la palma)
    # Landmark 9 = Base del dedo medio
    # Usamos el promedio para un centro más preciso de la palma
    wrist = hand_landmarks.landmark[0]
    middle_base = hand_landmarks.landmark[9]
    
    palm_x = int((wrist.x + middle_base.x) / 2 * w)
    palm_y = int((wrist.y + middle_base.y) / 2 * h)
    
    return palm_x, palm_y

def draw_pinch_visualization(frame, thumb_pos, index_pos, hand_color):
    """Dibuja la visualización de la pinza"""
    thumb_x, thumb_y = thumb_pos
    index_x, index_y = index_pos
    
    # Línea entre pulgar e índice
    cv2.line(frame, (thumb_x, thumb_y), (index_x, index_y),
             PINCH_LINE_COLOR, 4)
    
    # Círculos en las puntas
    cv2.circle(frame, (thumb_x, thumb_y), 15, hand_color, -1)
    cv2.circle(frame, (thumb_x, thumb_y), 15, (255, 255, 255), 3)
    
    cv2.circle(frame, (index_x, index_y), 15, hand_color, -1)
    cv2.circle(frame, (index_x, index_y), 15, (255, 255, 255), 3)

def draw_palm_marker(frame, x, y, color, in_pad_zone=False):
    """Dibuja un marcador grande en el centro de la palma"""
    # Destacar más cuando está en zona de pads
    if in_pad_zone:
        # Círculo grande y visible
        cv2.circle(frame, (x, y), 50, color, 4)
        cv2.circle(frame, (x, y), 42, color, -1)
    else:
        # Normal
        cv2.circle(frame, (x, y), 40, color, 3)
        cv2.circle(frame, (x, y), 35, color, -1)
    
    # Círculo medio
    cv2.circle(frame, (x, y), 25, (255, 255, 255), 3)
    
    # Centro
    cv2.circle(frame, (x, y), 10, (255, 255, 255), -1)
    
    # Cruz para indicar centro exacto
    line_len = 20
    cv2.line(frame, (x - line_len, y), (x + line_len, y), (0, 0, 0), 3)
    cv2.line(frame, (x, y - line_len), (x, y + line_len), (0, 0, 0), 3)

def draw_separator_line(frame):
    """Dibuja una línea clara separando las zonas"""
    # Línea amarilla gruesa
    cv2.line(frame, (0, PAD_MIN_Y), (CAMERA_WIDTH, PAD_MIN_Y),
             (0, 255, 255), 4)
    
    # Texto "ZONA DE PADS"
    zone_text = "ZONA DE PADS (BATERIA) - Solo aqui abajo"
    text_size = cv2.getTextSize(zone_text, cv2.FONT_HERSHEY_SIMPLEX, 0.8, 2)[0]
    text_x = (CAMERA_WIDTH - text_size[0]) // 2
    
    # Fondo negro para el texto
    cv2.rectangle(frame,
                 (text_x - 10, PAD_MIN_Y + 5),
                 (text_x + text_size[0] + 10, PAD_MIN_Y + 40),
                 (0, 0, 0), -1)
    
    cv2.putText(frame, zone_text,
               (text_x, PAD_MIN_Y + 30),
               cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)

# ============================================
# LOOP PRINCIPAL
# ============================================

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            continue
        
        # Voltear horizontalmente para efecto espejo
        frame = cv2.flip(frame, 1)
        h, w = frame.shape[:2]
        
        # Fondo más oscuro para colores vibrantes
        frame = cv2.convertScaleAbs(frame, alpha=0.5, beta=0)
        
        # Procesar con MediaPipe
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        rgb.flags.writeable = False
        results = hands.process(rgb)
        
        # Resetear estado de sliders
        for slider in sliders:
            slider.is_active = False
        
        hand_data = {}  # Almacenar datos de cada mano
        
        # Detectar manos
        if results.multi_hand_landmarks and results.multi_handedness:
            for hand_landmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
                hand_label = handedness.classification[0].label  # "Left" o "Right"
                
                # Obtener datos de pinza
                distance, thumb_pos, index_pos, pinch_center = get_pinch_distance(hand_landmarks, w, h)
                pinch_center_x, pinch_center_y = pinch_center
                
                # Obtener centro de la palma (para pads)
                palm_x, palm_y = get_palm_center(hand_landmarks, w, h)
                
                hand_data[hand_label] = {
                    'distance': distance,
                    'thumb_pos': thumb_pos,
                    'index_pos': index_pos,
                    'pinch_center_x': pinch_center_x,
                    'pinch_center_y': pinch_center_y,
                    'palm_x': palm_x,
                    'palm_y': palm_y
                }
        
        # Actualizar sliders según mano correspondiente (solo en zona de activación)
        for slider in sliders:
            if slider.hand_type in hand_data:
                data = hand_data[slider.hand_type]
                slider.update_from_pinch(data['distance'], 
                                        data['pinch_center_x'], 
                                        data['pinch_center_y'])
                if slider.is_active:
                    slider.send_midi_if_changed(midi_out)
        
        # Verificar pads con PALMA de la mano (cualquier mano puede tocarlos)
        for hand_label, data in hand_data.items():
            for pad in pads:
                pad.check_touch_with_palm(data['palm_x'], data['palm_y'])
        
        # Actualizar pads (para note off)
        for pad in pads:
            pad.update()
        
        # DIBUJAR TODO
        # ============
        
        # 1. Línea separadora entre zonas
        draw_separator_line(frame)
        
        # 2. Pads (fondo)
        for pad in pads:
            pad.draw(frame)
        
        # 3. Sliders
        for slider in sliders:
            slider.draw(frame)
        
        # 4. Visualización de pinzas y palmas
        for hand_label, data in hand_data.items():
            if hand_label == "Left":
                hand_color = HAND_LEFT_COLOR
            else:
                hand_color = HAND_RIGHT_COLOR
            
            # Dibujar pinza (solo si está en zona de sliders)
            in_slider_zone = False
            for slider in sliders:
                if slider.hand_type == hand_label and slider.is_in_zone:
                    in_slider_zone = True
                    break
            
            if in_slider_zone:
                # Dibujar pinza cuando está en zona activa
                draw_pinch_visualization(frame, data['thumb_pos'], data['index_pos'], hand_color)
            
            # Dibujar marcador de palma (destacar si está en zona de pads)
            in_pad_zone = data['palm_y'] >= PAD_MIN_Y
            draw_palm_marker(frame, data['palm_x'], data['palm_y'], hand_color, in_pad_zone)
        
        # INFORMACIÓN EN PANTALLA
        # =======================
        
        info_y = 30
        cv2.putText(frame, "CONTROLADOR MIDI MEJORADO",
                   (10, info_y), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 3)
        
        info_y += 45
        left_active = sliders[0].is_active
        right_active = sliders[1].is_active
        
        status_parts = []
        if left_active:
            status_parts.append("SLIDER IZQ")
        if right_active:
            status_parts.append("SLIDER DER")
        
        # Mostrar pads activos
        active_pads = [p.label for p in pads if p.is_active]
        if active_pads:
            status_parts.extend(active_pads)
        
        if status_parts:
            status_text = "Activo: " + " + ".join(status_parts)
            status_color = (0, 255, 255)
        else:
            status_text = "Esperando manos..."
            status_color = (150, 150, 150)
        
        cv2.putText(frame, status_text,
                   (10, info_y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, status_color, 2)
        
        # Instrucciones (abajo)
        instruction_y = h - 80
        cv2.putText(frame, "ARRIBA: Pinza para sliders (efectos) | ABAJO: Palma para pads (bateria)",
                   (10, instruction_y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (220, 220, 220), 2)
        
        instruction_y += 30
        cv2.putText(frame, "Las zonas estan SEPARADAS - No se cruzan!",
                   (10, instruction_y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
        
        instruction_y += 30
        cv2.putText(frame, "Presiona 'q' o ESC para salir",
                   (10, instruction_y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (150, 150, 150), 1)
        
        # Mostrar frame
        cv2.imshow('MIDI Controller - Mejorado', frame)
        
        # Control de teclado
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q') or key == 27:
            break

except KeyboardInterrupt:
    print("\n⚠️  Interrupción detectada (Ctrl+C)")

# ============================================
# LIMPIEZA
# ============================================

print("\n🧹 Limpiando...")

# Resetear todos los CC a 0
for slider in sliders:
    msg = mido.Message('control_change',
                      channel=MIDI_CHANNEL,
                      control=slider.cc_number,
                      value=0)
    midi_out.send(msg)

# Apagar todas las notas de los pads
for pad in pads:
    msg = mido.Message('note_off',
                      channel=MIDI_CHANNEL,
                      note=pad.note,
                      velocity=0)
    midi_out.send(msg)

# Liberar recursos
cap.release()
cv2.destroyAllWindows()
hands.close()
midi_out.close()

print("✅ Finalizado correctamente")
print("¡Hasta pronto! 🎛️")
