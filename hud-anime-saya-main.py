import ac
import acsys
import random
import math
import os
import sys
import platform

# --- PROTECTED ENVIRONMENT ARCHITECTURE PATH PATCH ---
current_dir = os.path.dirname(__file__)

# 1. Dynamically route to the correct bit-architecture standard library
sysdir = os.path.join(current_dir, "stdlib")
if platform.architecture()[0] == '64bit':
    sysdir = os.path.join(current_dir, "stdlib64")

# 2. Inject standard library paths safely into the front of Python's searching array
sys.path.insert(0, sysdir)
sys.path.insert(0, os.path.join(current_dir, "third_party"))

# 3. Force Windows system paths to check the current directory for missing DLL dependencies
os.environ['PATH'] = os.environ['PATH'] + ';.'

# 4. Safely initialize third-party telemetry bindings now that ctypes is mapped
from sim_info import info
# -----------------------------------------------------

# CRITICAL MATCH: Changed to exactly match your folder "ShiftLight"
app_name = "hud-anime-saya-main"
pngFolder = os.path.join(current_dir, "images") + "/"

# Windows & UI Element Handles
appWindow = 0
settingsWindow = 0

# Physics & Logic
current_state = -1 
timer = 0 
flash_toggle = True
MAX_RPM = 0
MAX_RPM_INITIALIZED = False
shake_enabled = 1  
offset_x = 10  
offset_y = 10  

# --- FIXED RIGHT-ANCHORED SPEEDOMETER LOGIC PROPERTIES ---
speed_list = []          
speed_x = 240            # Fixed horizontal anchor for the unit text (KM/H or MPH)
speed_y = 85             # Anchor Y position for centering vertically
speed_width = 22         # Width of individual numbers
speed_height = 34        # Height of individual numbers
speed_gap = 2            # Space between numbers

unit_width = 26          # Width of the unit texture
unit_height = 12         # Height of the unit texture
unit_y_offset = 18       # Drops the unit text lower down to align with digit bottoms

# Interchangeable metric toggle state (True = KM/H, False = MPH)
unit_kmh = True
speedo_enabled = 0       # Visibility toggle (1 = Show / 0 = Hide)
# ----------------------------------------------------------

# Settings Toggle (1 = On / 0 = Off)
cooked_enabled = 1 

# Splash & Fading Logic
tex_splash = -1
tex_collision = -1
tex_pog_splash = -1
splash_toggle = 0
was_colliding = False
splash_opacity = 0.0
show_splash = False
hide_timer = 0
collision_delay = 0
splash_enabled = 1 
FADE_IN_SPEED = 10.0  
FADE_OUT_SPEED = 1.5

# Texture Handles
tex_active = -1
tex_frame = -1     
last_loaded_path = ""
speed_digits = []       
tex_kmh = -1            
tex_mph = -1            

# Callback functions
def on_shake_toggle(name, value):
    global shake_enabled
    shake_enabled = value

def on_splash_toggle(name, value):
    global splash_enabled
    splash_enabled = value

def on_cooked_toggle(name, value):
    global cooked_enabled
    cooked_enabled = value

def on_unit_toggle(name, value):
    global unit_kmh
    unit_kmh = bool(value)

def on_speedo_toggle(name, value):
    global speedo_enabled
    speedo_enabled = value

def onFormRender(deltaT):
    global tex_active, tex_frame, tex_splash, shake_enabled, MAX_RPM, offset_x, offset_y, splash_opacity
    global speed_list, speed_digits, speed_x, speed_y, speed_width, speed_height, speed_gap
    global tex_kmh, tex_mph, unit_kmh, unit_width, unit_height, unit_y_offset, speedo_enabled
    
    ac.glColor4f(1, 1, 1, 1)
    rpm = ac.getCarState(0, acsys.CS.RPM)
    
    cx, cy = 0, 0
    if shake_enabled == 1:
        if rpm > 4000 and MAX_RPM > 4000:
            rel_rpm = max(0, min(1, (rpm - 4000) / (MAX_RPM - 4000)))
            amplitude = (rel_rpm ** 3) * 6.0
            cx = random.uniform(-amplitude, amplitude)
            cy = random.uniform(-amplitude, amplitude)

    # --- 1. LIGHTS (BOTTOM) ---
    if tex_active != -1:
        ac.ext_glSetTexture(tex_active)
        ac.glBegin(acsys.GL.Quads)
        ac.ext_glVertexTex((offset_x + cx), (offset_y + cy), 0, 0)
        ac.ext_glVertexTex((offset_x + cx), ((offset_y + 120) + cy), 0, 1)
        ac.ext_glVertexTex(((offset_x + 320) + cx), ((offset_y + 120) + cy), 1, 1)
        ac.ext_glVertexTex(((offset_x + 320) + cx), (offset_y + cy), 1, 0)
        ac.glEnd()

    # --- 2. SPLASH (MIDDLE) ---
    if tex_splash != -1 and splash_opacity > 0:
        ac.glColor4f(1, 1, 1, splash_opacity)
        ac.ext_glSetTexture(tex_splash)
        ac.glBegin(acsys.GL.Quads)
        ac.ext_glVertexTex((offset_x + cx), (offset_y + cy), 0, 0)
        ac.ext_glVertexTex((offset_x + cx), ((offset_y + 120) + cy), 0, 1)
        ac.ext_glVertexTex(((offset_x + 320) + cx), ((offset_y + 120) + cy), 1, 1)
        ac.ext_glVertexTex(((offset_x + 320) + cx), (offset_y + cy), 1, 0)
        ac.glEnd()
        ac.glColor4f(1, 1, 1, 1)

    # --- 3. FRAME (TOP) ---
    if tex_frame != -1:
        ac.ext_glSetTexture(tex_frame)
        ac.glBegin(acsys.GL.Quads)
        ac.ext_glVertexTex(0, 0, 0, 0)
        ac.ext_glVertexTex(0, 140, 0, 1)
        ac.ext_glVertexTex(340, 140, 1, 1)
        ac.ext_glVertexTex(340, 0, 1, 0)
        ac.glEnd()

    # --- 4. DIGITAL SPEEDOMETER RENDERING ENGINE ---
    if speedo_enabled == 1:
        ac.glColor4f(1, 1, 1, 1)
        
        # Render Unit Text first at fixed anchor position
        active_unit_tex = tex_kmh if unit_kmh else tex_mph
        if active_unit_tex != -1:
            u_x1 = speed_x
            u_y1 = (speed_y + unit_y_offset)
            u_x2 = (speed_x + unit_width)
            u_y2 = (speed_y + unit_y_offset + unit_height)
            
            ac.ext_glSetTexture(active_unit_tex)
            ac.glBegin(acsys.GL.Quads)
            ac.ext_glVertexTex(u_x1, u_y1, 0, 0)
            ac.ext_glVertexTex(u_x1, u_y2, 0, 1)
            ac.ext_glVertexTex(u_x2, u_y2, 1, 1)
            ac.ext_glVertexTex(u_x2, u_y1, 1, 0)
            ac.glEnd()

        # Render digital segments moving backwards to the left
        for i in range(len(speed_list)):
            digit_value = int((speed_list[::-1])[i])
            
            x2 = speed_x - speed_gap - (i * (speed_width + speed_gap))
            x1 = x2 - speed_width
            y1 = speed_y
            y2 = y1 + speed_height
            
            ac.ext_glSetTexture(speed_digits[digit_value])
            ac.glBegin(acsys.GL.Quads)
            ac.ext_glVertexTex(x1, y1, 0, 0)
            ac.ext_glVertexTex(x1, y2, 0, 1)
            ac.ext_glVertexTex(x2, y2, 1, 1)
            ac.ext_glVertexTex(x2, y1, 1, 0)
            ac.glEnd()

def acUpdate(deltaT):
    global current_state, timer, flash_toggle, tex_active, last_loaded_path
    global MAX_RPM, MAX_RPM_INITIALIZED
    global show_splash, hide_timer, collision_delay, splash_opacity, splash_enabled, tex_splash
    global cooked_enabled, speed_list, unit_kmh
    global was_colliding, splash_toggle, tex_collision, tex_pog_splash

    if not MAX_RPM_INITIALIZED:
        if info.static.maxRpm > 0:
            MAX_RPM = info.static.maxRpm
            MAX_RPM_INITIALIZED = True
        else: return

    raw_lat, vert_g, raw_lon = ac.getCarState(0, acsys.CS.AccG)
    g_mag = math.sqrt(raw_lat**2 + raw_lon**2)
    
    if g_mag > 2.0 and splash_enabled == 1:
        if not was_colliding:
            was_colliding = True
            # Swap splash image on each NEW hit
            if splash_toggle == 0:
                tex_splash = tex_collision
                splash_toggle = 1
            else:
                tex_splash = tex_pog_splash
                splash_toggle = 0
                
        collision_delay = 0.1 
        hide_timer = 0.4 
    elif g_mag <= 1.5:
        was_colliding = False # Reset hit trigger when G-force drops
    
    if collision_delay > 0:
        collision_delay -= deltaT
        show_splash = False 
    elif hide_timer > 0:
        hide_timer -= deltaT
        show_splash = True  
    else:
        show_splash = False

    if show_splash:
        splash_opacity = min(1.0, splash_opacity + (FADE_IN_SPEED * deltaT))
    else:
        splash_opacity = max(0.0, splash_opacity - (FADE_OUT_SPEED * deltaT))

    if unit_kmh:
        speed = ac.getCarState(0, acsys.CS.SpeedKMH)
    else:
        speed = ac.getCarState(0, acsys.CS.SpeedMPH)
        
    speed_list = list("{0:.0f}".format(speed))

    # Calculate status mappings
    rpm = ac.getCarState(0, acsys.CS.RPM)
    rpmPercent = rpm / MAX_RPM if MAX_RPM > 0 else 0

    if rpmPercent > 1.01:
        new_state = 6 if cooked_enabled == 1 else 5 
    elif rpmPercent > 0.96: new_state = 5           
    elif rpmPercent > 0.90: new_state = 4           
    elif rpmPercent > 0.80: new_state = 3           
    elif rpmPercent > 0.65: new_state = 2           
    elif rpmPercent > 0.50: new_state = 1           
    else: new_state = 0                             

    mapping = {0: "green.png", 1: "green2.png", 2: "yellow.png", 
               3: "yellow2.png", 4: "red.png", 6: "cooked.png"}
    
    img_file = ""
    if new_state == 5:
        timer += deltaT
        if timer > 0.05:
            flash_toggle = not flash_toggle
            timer = 0
        img_file = "red.png" if flash_toggle else "blank.png"
    else:
        img_file = mapping.get(new_state, "green.png")

    new_path = pngFolder + img_file
    if new_path != last_loaded_path:
        tex_active = ac.newTexture(new_path)
        last_loaded_path = new_path

def acMain(ac_version):
    global appWindow, settingsWindow, tex_frame, tex_splash, speed_digits, tex_kmh, tex_mph
    global speedo_enabled, tex_collision, tex_pog_splash
    
    appWindow = ac.newApp(app_name)
    ac.setSize(appWindow, 340, 140)
    
    # FORCED VISIBILITY LAYER: Giving it a name and standard gray borders temporarily
    ac.setTitle(appWindow, "")
    ac.drawBorder(appWindow, 0)
    ac.setBackgroundOpacity(appWindow, 0)
    
    # Load textures for digits 0 through 9
    speed_digits = []
    for i in range(10):
        digit_path = pngFolder + "speed_digits/speed_digits_" + str(i) + ".png"
        speed_digits.append(ac.newTexture(digit_path))
        
    # --- LOAD INTERCHANGEABLE UNIT IMAGES ---
    tex_kmh = ac.newTexture(pngFolder + "speed_unit/kmh.png")
    tex_mph = ac.newTexture(pngFolder + "speed_unit/mph.png")
    # ----------------------------------------
    
    # Settings Window 
    settingsWindow = ac.newApp("ShiftLight Settings")
    ac.setSize(settingsWindow, 200, 200)
    ac.setPosition(settingsWindow, 760, 300)
    
    shake_check = ac.addCheckBox(settingsWindow, "Enable Shake")
    ac.setPosition(shake_check, 10, 35)
    ac.setSize(shake_check, 15, 15)
    ac.setValue(shake_check, 1)
    ac.addOnCheckBoxChanged(shake_check, on_shake_toggle)

    splash_check = ac.addCheckBox(settingsWindow, "Collision Enabled")
    ac.setPosition(splash_check, 10, 65)
    ac.setSize(splash_check, 15, 15)
    ac.setValue(splash_check, 1)
    ac.addOnCheckBoxChanged(splash_check, on_splash_toggle)
    
    cooked_check = ac.addCheckBox(settingsWindow, "Enable Cooked Light")
    ac.setPosition(cooked_check, 10, 95)
    ac.setSize(cooked_check, 15, 15)
    ac.setValue(cooked_check, 1)  
    ac.addOnCheckBoxChanged(cooked_check, on_cooked_toggle)

    unit_check = ac.addCheckBox(settingsWindow, "Speed in KM/H")
    ac.setPosition(unit_check, 10, 125)
    ac.setSize(unit_check, 15, 15)
    ac.setValue(unit_check, 1 if unit_kmh else 0)  
    ac.addOnCheckBoxChanged(unit_check, on_unit_toggle)

    speedo_check = ac.addCheckBox(settingsWindow, "Enable Speedometer")
    ac.setPosition(speedo_check, 10, 155)
    ac.setSize(speedo_check, 15, 15)
    ac.setValue(speedo_check, 1 if speedo_enabled == 1 else 0)
    ac.addOnCheckBoxChanged(speedo_check, on_speedo_toggle)
    
    tex_frame = ac.newTexture(pngFolder + "frame.png")
    
    # Load both collision textures
    tex_collision = ac.newTexture(pngFolder + "collision.png")
    tex_pog_splash = ac.newTexture(pngFolder + "pog.png")
    tex_splash = tex_collision
    
    ac.addRenderCallback(appWindow, onFormRender)
    return app_name