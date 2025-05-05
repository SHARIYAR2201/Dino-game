from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import sys
import math
import random
import time

# Dinosaur position and orientation
dino_x, dino_y, dino_z = 0.0, 0.0, 0.0
dino_angle = 0.0

# Animation variables
leg_angle = 0.0
leg_direction = 1.0
leg_speed = 5.0
mouth_angle = 0.0
mouth_direction = 1.0
eye_angle = 0.0
blink_timer = 0
is_blinking = False

# First person view toggle
first_person = False

# Window size
width, height = 800, 600

# Movement states
move_forward = move_backward = move_left = move_right = False
turn_left = turn_right = False

# Camera parameters
camera_angle = 0.0
camera_height = 2.0
camera_distance = 10.0
camera_smoothness = 0.1  # Lower value = smoother camera
target_camera_angle = 0.0
target_camera_height = 2.0
target_camera_distance = 10.0

# Environment rotation angle
environment_angle = 0.0

# Movement parameters
movement_speed = 0.3
rotation_speed = 3.0
strafe_speed = 0.2

# List of random dragon positions and states
dragons = []

# Fireball properties
fireballs = []
fireball_speed = 0.5
last_fireball_time = 0
fireball_cooldown = 0.5  # seconds between fireballs

# Score system
score = 0
hit_cooldown = {}  # Dictionary to track hit cooldowns for each dragon

# Add these variables at the top with other global variables
cheat_mode = False
target_dragon = None
last_auto_fire_time = 0
auto_fire_cooldown = 0.3  # Faster fire rate in cheat mode

def draw_cube():
    glutSolidCube(1.0)

def draw_sphere(radius=1.0):
    glutSolidSphere(radius, 16, 16)

def draw_ground():
    # Main ground
    glColor3f(0.4, 0.25, 0.1)
    glPushMatrix()
    glTranslatef(0, -0.5, 0)
    glScalef(200, 1, 200)
    draw_cube()
    glPopMatrix()

def draw_dragons():
    for dragon in dragons:
        x, y, z, angle = dragon
        draw_dragon(x, y, z, angle)

def draw_dragon(x, y, z, angle=0.0):
    glPushMatrix()
    glTranslatef(x, y, z)
    glRotatef(angle, 0, 1, 0)
    
    # Body (bigger size)
    glColor3f(0.8, 0.2, 0.2)
    glPushMatrix()
    glScalef(0.8, 0.6, 1.2)  # Doubled the size
    draw_cube()
    glPopMatrix()
    
    # Head
    glPushMatrix()
    glTranslatef(0.0, 0.4, 0.6)  # Adjusted position for bigger body
    glScalef(0.4, 0.4, 0.6)  # Doubled the size
    glColor3f(0.9, 0.2, 0.2)
    draw_cube()
    
    # Eyes
    glColor3f(0.0, 0.0, 0.0)
    glPushMatrix()
    glTranslatef(0.2, 0.2, 0.4)  # Adjusted position
    draw_sphere(0.06)  # Bigger eyes
    glPopMatrix()
    glPushMatrix()
    glTranslatef(-0.2, 0.2, 0.4)  # Adjusted position
    draw_sphere(0.06)  # Bigger eyes
    glPopMatrix()
    
    # Mouth
    glColor3f(0.0, 0.0, 0.0)
    glPushMatrix()
    glTranslatef(0.0, -0.2, 0.4)  # Adjusted position
    glScalef(0.2, 0.1, 0.2)  # Bigger mouth
    draw_cube()
    glPopMatrix()
    
    glPopMatrix()
    
    # Legs (bigger)
    leg_positions = [(-0.3, -0.3, 0.4), (0.3, -0.3, 0.4), 
                    (-0.3, -0.3, -0.4), (0.3, -0.3, -0.4)]
    for (lx, ly, lz) in leg_positions:
        glPushMatrix()
        glTranslatef(lx, ly, lz)
        glScalef(0.16, 0.4, 0.16)  # Bigger legs
        glColor3f(0.7, 0.1, 0.1)
        draw_cube()
        glPopMatrix()
    
    glPopMatrix()

def draw_dinosaur():
    global leg_angle, mouth_angle, eye_angle, is_blinking
    
    glPushMatrix()
    glTranslatef(dino_x, dino_y, dino_z)
    glRotatef(dino_angle, 0, 1, 0)
    
    # Body
    glColor3f(0.2, 0.8, 0.2)  # Green color
    glPushMatrix()
    glScalef(0.8, 0.6, 1.2)
    draw_cube()
    glPopMatrix()
    
    # Head
    glPushMatrix()
    glTranslatef(0.0, 0.4, 0.6)
    glScalef(0.4, 0.4, 0.6)
    glColor3f(0.2, 0.9, 0.2)  # Slightly lighter green
    draw_cube()
    
    # Eyes
    glColor3f(0.0, 0.0, 0.0)
    if not is_blinking:
        # Left eye
        glPushMatrix()
        glTranslatef(0.2, 0.2, 0.4)
        glRotatef(eye_angle, 0, 1, 0)
        draw_sphere(0.06)
        glPopMatrix()
        
        # Right eye
        glPushMatrix()
        glTranslatef(-0.2, 0.2, 0.4)
        glRotatef(-eye_angle, 0, 1, 0)
        draw_sphere(0.06)
        glPopMatrix()
    else:
        # Blinking eyes
        glPushMatrix()
        glTranslatef(0.2, 0.2, 0.4)
        glScalef(0.1, 0.02, 0.1)
        draw_cube()
        glPopMatrix()
        
        glPushMatrix()
        glTranslatef(-0.2, 0.2, 0.4)
        glScalef(0.1, 0.02, 0.1)
        draw_cube()
        glPopMatrix()
    
    # Mouth
    glColor3f(0.0, 0.0, 0.0)
    glPushMatrix()
    glTranslatef(0.0, -0.2, 0.4)
    glRotatef(mouth_angle, 1, 0, 0)
    glScalef(0.2, 0.1, 0.2)
    draw_cube()
    glPopMatrix()
    
    glPopMatrix()
    
    # Legs with animation
    leg_positions = [(-0.3, -0.3, 0.4), (0.3, -0.3, 0.4), 
                    (-0.3, -0.3, -0.4), (0.3, -0.3, -0.4)]
    for i, (lx, ly, lz) in enumerate(leg_positions):
        glPushMatrix()
        glTranslatef(lx, ly, lz)
        # Alternate leg movement
        if i % 2 == 0:
            glRotatef(leg_angle, 1, 0, 0)
        else:
            glRotatef(-leg_angle, 1, 0, 0)
        glScalef(0.16, 0.4, 0.16)
        glColor3f(0.2, 0.7, 0.2)  # Slightly darker green
        draw_cube()
        glPopMatrix()
    
    # Tail
    glColor3f(0.2, 0.8, 0.2)
    glPushMatrix()
    glTranslatef(0.0, 0.0, -0.8)
    glScalef(0.2, 0.2, 0.8)
    draw_cube()
    glPopMatrix()
    
    glPopMatrix()

def draw_fireball(x, y, z, direction):
    glPushMatrix()
    glTranslatef(x, y, z)
    
    # Fireball body
    glColor3f(1.0, 0.5, 0.0)
    draw_sphere(0.2)
    
    # Glowing effect
    glColor3f(1.0, 0.8, 0.0)
    draw_sphere(0.15)
    
    glPopMatrix()

def draw_score():
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    glOrtho(0, width, height, 0, -1, 1)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    # Draw score text
    glColor3f(1.0, 1.0, 1.0)
    glRasterPos2f(20, 30)
    score_text = f"Score: {score}"
    for char in score_text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(char))
    
    # Draw cheat mode status
    if cheat_mode:
        glColor3f(1.0, 0.0, 0.0)
        glRasterPos2f(20, 60)
        cheat_text = "CHEAT MODE: ON"
        for char in cheat_text:
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(char))
    
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    glPopMatrix()

def check_collisions():
    global score, fireballs, dragons, hit_cooldown
    current_time = time.time()
    
    # Check each fireball against each dragon
    for fireball in fireballs[:]:
        fx, fy, fz, _ = fireball
        for i, dragon in enumerate(dragons[:]):
            dx, dy, dz, _ = dragon
            # Calculate distance between fireball and dragon
            distance = math.sqrt((fx - dx)**2 + (fy - dy)**2 + (fz - dz)**2)
            
            # If collision detected and not in cooldown
            if distance < 1.0 and i not in hit_cooldown:
                score += 1
                dragons.pop(i)
                fireballs.remove(fireball)
                hit_cooldown[i] = current_time
                break

def draw_cloud(x, y, z, size):
    glPushMatrix()
    glTranslatef(x, y, z)
    
    # Cloud is made of multiple spheres
    glColor3f(1.0, 1.0, 1.0)
    
    # Main cloud parts
    positions = [
        (0, 0, 0),
        (size*0.3, size*0.1, 0),
        (-size*0.3, size*0.1, 0),
        (0, size*0.2, size*0.3),
        (0, size*0.2, -size*0.3)
    ]
    
    for px, py, pz in positions:
        glPushMatrix()
        glTranslatef(px, py, pz)
        draw_sphere(size * 0.3)
        glPopMatrix()
    
    glPopMatrix()

def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()

    if first_person:
        # First person camera
        cam_x = dino_x + math.sin(math.radians(dino_angle)) * 1.5
        cam_y = dino_y + 1.0
        cam_z = dino_z + math.cos(math.radians(dino_angle)) * 1.5
        look_x = dino_x + math.sin(math.radians(dino_angle)) * 2.0
        look_y = dino_y + 1.0
        look_z = dino_z + math.cos(math.radians(dino_angle)) * 2.0
        gluLookAt(cam_x, cam_y, cam_z, look_x, look_y, look_z, 0, 1, 0)
    else:
        # Third person camera with smooth following
        cam_x = dino_x - math.sin(math.radians(camera_angle)) * camera_distance
        cam_y = dino_y + camera_height
        cam_z = dino_z - math.cos(math.radians(camera_angle)) * camera_distance
        gluLookAt(cam_x, cam_y, cam_z, dino_x, dino_y, dino_z, 0, 1, 0)

    # Apply environment rotation
    glPushMatrix()
    glRotatef(environment_angle, 0, 1, 0)

    draw_ground()
    draw_dragons()
    draw_dinosaur()
    
    # Draw fireballs
    for fireball in fireballs:
        x, y, z, direction = fireball
        draw_fireball(x, y, z, direction)

    glPopMatrix()

    # Draw score
    draw_score()

    glutSwapBuffers()

def reshape(w, h):
    global width, height
    width, height = w, h
    glViewport(0, 0, w, h)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(60, float(w)/float(h), 1.0, 100.0)
    glMatrixMode(GL_MODELVIEW)

def update(value):
    global dino_x, dino_z, dino_angle, leg_angle, leg_direction
    global mouth_angle, mouth_direction, eye_angle, is_blinking, blink_timer
    global dragons, fireballs, hit_cooldown
    global camera_angle, camera_height, camera_distance
    global target_camera_angle, target_camera_height, target_camera_distance
    global cheat_mode, target_dragon, last_auto_fire_time
    current_time = time.time()

    if cheat_mode:
        auto_target_dragon()
        auto_move_to_dragon()
        auto_fire()

    # Update dinosaur rotation
    if turn_left:
        dino_angle += rotation_speed
    if turn_right:
        dino_angle -= rotation_speed

    # Calculate movement direction
    angle_rad = math.radians(dino_angle)
    
    # Update position based on movement state
    if move_forward:
        dino_x += math.sin(angle_rad) * movement_speed
        dino_z += math.cos(angle_rad) * movement_speed
    if move_backward:
        dino_x -= math.sin(angle_rad) * movement_speed
        dino_z -= math.cos(angle_rad) * movement_speed
    if move_left:
        # Strafe left
        dino_x -= math.cos(angle_rad) * strafe_speed
        dino_z += math.sin(angle_rad) * strafe_speed
    if move_right:
        # Strafe right
        dino_x += math.cos(angle_rad) * strafe_speed
        dino_z -= math.sin(angle_rad) * strafe_speed

    # Update leg animation
    if move_forward or move_backward or move_left or move_right:
        leg_angle += leg_speed * leg_direction
        if abs(leg_angle) > 30:
            leg_direction *= -1
    else:
        leg_angle = 0

    # Update mouth animation
    if move_forward or move_backward or move_left or move_right:
        mouth_angle += 2.0 * mouth_direction
        if abs(mouth_angle) > 15:
            mouth_direction *= -1
    else:
        mouth_angle = 0

    # Update eye movement
    eye_angle = math.sin(time.time() * 2) * 10

    # Update blinking
    if not is_blinking:
        blink_timer += 1
        if blink_timer > 100:
            is_blinking = True
            blink_timer = 0
    else:
        blink_timer += 1
        if blink_timer > 10:
            is_blinking = False
            blink_timer = 0

    # Smooth camera movement
    camera_angle += (target_camera_angle - camera_angle) * camera_smoothness
    camera_height += (target_camera_height - camera_height) * camera_smoothness
    camera_distance += (target_camera_distance - camera_distance) * camera_smoothness

    # Update dragons
    for i in range(len(dragons)):
        x, y, z, angle = dragons[i]
        angle += random.uniform(-1, 1)
        x += math.sin(math.radians(angle)) * 0.05
        z += math.cos(math.radians(angle)) * 0.05
        dragons[i] = (x, y, z, angle)

    # Update fireballs
    new_fireballs = []
    for fireball in fireballs:
        x, y, z, direction = fireball
        x += math.sin(math.radians(direction)) * fireball_speed
        z += math.cos(math.radians(direction)) * fireball_speed
        if abs(x) < 100 and abs(z) < 100:
            new_fireballs.append((x, y, z, direction))
    fireballs = new_fireballs

    # Check for collisions
    check_collisions()

    # Clean up hit cooldowns
    hit_cooldown = {k: v for k, v in hit_cooldown.items() if current_time - v < 1.0}

    glutPostRedisplay()
    glutTimerFunc(16, update, 0)

def keyboard(key, x, y):
    global move_forward, move_backward, turn_left, turn_right
    global cheat_mode
    
    if key == b'c' or key == b'C':
        cheat_mode = not cheat_mode
        if not cheat_mode:
            move_forward = False
            move_backward = False
            turn_left = False
            turn_right = False
    elif key == b'w':
        move_forward = True
    elif key == b's':
        move_backward = True
    elif key == b'a':
        turn_left = True
    elif key == b'd':
        turn_right = True
    elif key == b'm':
        global environment_angle
        environment_angle += 2.0
    elif key == b'r':
        global dino_x, dino_y, dino_z, dino_angle
        dino_x, dino_y, dino_z = 0.0, 0.0, 0.0
        dino_angle = 0.0
    elif key == b't':
        global dragons
        dragons = []
        for _ in range(15):
            x = random.uniform(-80, 80)
            z = random.uniform(-80, 80)
            y = 0.0
            angle = random.uniform(0, 360)
            dragons.append((x, y, z, angle))

def keyboard_up(key, x, y):
    global move_forward, move_backward, turn_left, turn_right
    if key == b'w':
        move_forward = False
    elif key == b's':
        move_backward = False
    elif key == b'a':
        turn_left = False
    elif key == b'd':
        turn_right = False

def special_input(key, x, y):
    global move_left, move_right, target_camera_angle, target_camera_distance
    if key == GLUT_KEY_LEFT:
        move_left = True
    elif key == GLUT_KEY_RIGHT:
        move_right = True
    elif key == GLUT_KEY_UP:
        target_camera_distance = max(5.0, target_camera_distance - 1.0)
    elif key == GLUT_KEY_DOWN:
        target_camera_distance = min(20.0, target_camera_distance + 1.0)

def special_up(key, x, y):
    global move_left, move_right
    if key == GLUT_KEY_LEFT:
        move_left = False
    elif key == GLUT_KEY_RIGHT:
        move_right = False

def mouse(button, state, x, y):
    global first_person, fireballs, last_fireball_time
    if button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
        first_person = not first_person
    elif button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        current_time = time.time()
        # Check cooldown before spawning new fireball
        if current_time - last_fireball_time >= fireball_cooldown:
            # Spawn fireball from dinosaur's mouth
            fireball_x = dino_x + math.sin(math.radians(dino_angle)) * 1.5
            fireball_y = dino_y + 0.5
            fireball_z = dino_z + math.cos(math.radians(dino_angle)) * 1.5
            fireballs.append((fireball_x, fireball_y, fireball_z, dino_angle))
            last_fireball_time = current_time

def init():
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_COLOR_MATERIAL)
    glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
    
    # Set up light
    glLightfv(GL_LIGHT0, GL_POSITION, (0, 100, 0, 1))
    glLightfv(GL_LIGHT0, GL_AMBIENT, (0.2, 0.2, 0.2, 1))
    glLightfv(GL_LIGHT0, GL_DIFFUSE, (0.8, 0.8, 0.8, 1))
    
    # Set background color to sky blue
    glClearColor(0.5, 0.8, 1.0, 1.0)

def find_nearest_dragon():
    if not dragons:
        return None
    
    nearest_dragon = None
    min_distance = float('inf')
    
    for dragon in dragons:
        dx = dragon[0] - dino_x
        dz = dragon[2] - dino_z
        distance = math.sqrt(dx * dx + dz * dz)
        
        if distance < min_distance:
            min_distance = distance
            nearest_dragon = dragon
    
    return nearest_dragon

def auto_target_dragon():
    global dino_angle, target_dragon
    
    if not dragons:
        target_dragon = None
        return
    
    if not target_dragon or target_dragon not in dragons:
        target_dragon = find_nearest_dragon()
    
    if target_dragon:
        # Calculate angle to dragon
        dx = target_dragon[0] - dino_x
        dz = target_dragon[2] - dino_z
        target_angle = math.degrees(math.atan2(dx, dz))
        
        # Smoothly rotate towards target
        angle_diff = (target_angle - dino_angle) % 360
        if angle_diff > 180:
            angle_diff -= 360
        
        if abs(angle_diff) > 5:
            dino_angle += angle_diff * 0.1

def auto_move_to_dragon():
    global dino_x, dino_z, move_forward
    
    if not target_dragon:
        return
    
    # Calculate distance to target
    dx = target_dragon[0] - dino_x
    dz = target_dragon[2] - dino_z
    distance = math.sqrt(dx * dx + dz * dz)
    
    # Move forward if not too close
    if distance > 5:
        move_forward = True
    else:
        move_forward = False

def auto_fire():
    global last_auto_fire_time, fireballs
    
    current_time = time.time()
    if current_time - last_auto_fire_time >= auto_fire_cooldown:
        # Spawn fireball from dinosaur's mouth
        fireball_x = dino_x + math.sin(math.radians(dino_angle)) * 1.5
        fireball_y = dino_y + 0.5
        fireball_z = dino_z + math.cos(math.radians(dino_angle)) * 1.5
        fireballs.append((fireball_x, fireball_y, fireball_z, dino_angle))
        last_auto_fire_time = current_time

def main():
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGBA | GLUT_DEPTH)
    glutInitWindowSize(width, height)
    glutCreateWindow(b"3D Dinosaur Game")
    init()
    glutDisplayFunc(display)
    glutReshapeFunc(reshape)
    glutKeyboardFunc(keyboard)
    glutKeyboardUpFunc(keyboard_up)
    glutSpecialFunc(special_input)
    glutSpecialUpFunc(special_up)
    glutMouseFunc(mouse)
    glutTimerFunc(16, update, 0)
    glutMainLoop()

if __name__ == "__main__":
    main()
