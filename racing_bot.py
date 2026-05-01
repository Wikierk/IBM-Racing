import math

TARGET_SPEED = 320.0
MAX_BRAKING_FORCE = 1.0

SHIFT_UP_RPM = 18150.0
SHIFT_DOWN_RPM = 12100.0 

def detect_corkscrew(speed_z, front_vision, speed_kmh):
    if speed_z < -0.8 and front_vision > 70.0 and speed_kmh > 80.0:
        return 35.0 
    return front_vision

def calculate_acceleration(current_speed, brake_applied, wheel_spin, steer_angle, track_pos):
    if brake_applied > 0.05:
        return 0.0 
        
    rear_spin = wheel_spin[2] + wheel_spin[3]
    front_spin = wheel_spin[0] + wheel_spin[1]
    slip = rear_spin - front_spin
    
    accel = 1.0
    
    if abs(steer_angle) > 0.6 and current_speed > 80.0:
        accel -= abs(steer_angle) * 0.15
        
    allowed_slip = 1.2 if current_speed > 80.0 else 1.0
    if slip > allowed_slip:
        accel -= (slip - allowed_slip) * 0.4 
        
    if abs(track_pos) > 0.85 and current_speed > 60.0:
        accel *= 0.80
        
    if current_speed < 50.0 and accel > 0.0:
        accel = min(accel, 0.7 + (current_speed / 100.0))

    return max(0.0, min(1.0, accel))

def calculate_steering(current_angle, track_pos, track_sensors, speed_kmh):
    right_vision = max(track_sensors[3:7])   
    left_vision = max(track_sensors[12:16])  
    front_vision = track_sensors[9]  

    max_dist = max(track_sensors)
    max_idx = track_sensors.index(max_dist)
    
    curve_direction = max_idx - 9
    turn_indicator = (left_vision - right_vision) / (left_vision + right_vision + 1.0)
    
    target_track_pos = 0.0 

    if front_vision < 150.0:
        if curve_direction < -1:
            target_track_pos = 0.6 * (1.0 - (front_vision/150.0))
        elif curve_direction > 1:
            target_track_pos = -0.6 * (1.0 - (front_vision/150.0))
    else:
        target_track_pos = 0.0

    lookahead_min = 35.0 + (speed_kmh * 0.3)
    distance_factor = max(0.0, min(1.0, (front_vision - lookahead_min) / 80.0)) 
    
    speed_factor = max(1.0, speed_kmh / 100.0)
    angle_weight = 4.0 / math.sqrt(speed_factor)
    pos_weight = 0.7 / speed_factor

    steer_angle_corr = current_angle * angle_weight
    steer_pos_corr = (track_pos - target_track_pos) * pos_weight 
    
    steer = steer_angle_corr - steer_pos_corr + (turn_indicator * 0.1 * (1.0 - distance_factor))
    
    if track_pos > 0.85:
        steer -= (track_pos - 0.85) * 1.5
    elif track_pos < -0.85:
        steer -= (track_pos + 0.85) * 1.5
    
    return max(-1.0, min(1.0, steer))

def calculate_braking(speed_kmh, track_sensors, speed_z, steer_intent):
    if speed_kmh < 20.0:
        return 0.0

    speed_ms = speed_kmh / 3.6
    raw_front_distance = max(track_sensors[8:11]) 
    critical_distance = detect_corkscrew(speed_z, raw_front_distance, speed_kmh)

    max_dist = max(track_sensors)
    max_idx = track_sensors.index(max_dist)
    
    angle_severity = abs(max_idx - 9)
    
    if angle_severity <= 1:
        target_speed_kmh = max(185.0, max_dist * 1.5)
    elif angle_severity <= 4:
        target_speed_kmh = max(85.0, max_dist * 0.95)
    else:
        target_speed_kmh = max(50.0, max_dist * 0.6)
    
    if speed_kmh <= target_speed_kmh:
        return 0.0 

    target_speed_ms = target_speed_kmh / 3.6

    deceleration = 19.5 + (speed_ms * 0.05) 
    
    stopping_distance = (speed_ms ** 2 - target_speed_ms ** 2) / (2.0 * deceleration)
    
    safety_margin = 2.5 + (speed_ms * 0.08) 

    if critical_distance > (stopping_distance + safety_margin):
        return 0.0 

    braking_intensity = ((stopping_distance + safety_margin) - critical_distance) / safety_margin
    
    max_brake = MAX_BRAKING_FORCE - (abs(steer_intent) * 0.25)

    return max(0.0, min(max_brake, braking_intensity * 2.0))

def drive_smart(c):
    S, R = c.S.d, c.R.d
    
    current_speed = S['speedX']
    speed_z = S['speedZ']                
    wheel_spin = S['wheelSpinVel']      
    rpm = S['rpm']
    current_gear = S['gear']
    
    front_wall = S['track'][9]
    if current_speed < 5.0 and front_wall < 6.0:
        R['gear'] = -1                 
        R['accel'] = 1.0          
        R['brake'] = 0.0
        R['steer'] = -S['angle']       
        return 

    R['steer'] = calculate_steering(S['angle'], S['trackPos'], S['track'], current_speed)
    R['brake'] = calculate_braking(current_speed, S['track'], speed_z, R['steer'])
    R['accel'] = calculate_acceleration(current_speed, R['brake'], wheel_spin, R['steer'], S['trackPos'])
            
    if current_gear <= 0: 
        R['gear'] = 1
    else:
        R['gear'] = current_gear
        if rpm > SHIFT_UP_RPM and current_gear < 6:
            R['gear'] = current_gear + 1
        elif current_gear == 2 and rpm < 3500.0:
            R['gear'] = 1
        elif rpm < SHIFT_DOWN_RPM and current_gear > 2:
            R['gear'] = current_gear - 1

    return