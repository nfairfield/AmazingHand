import time
import json
import sys
import tty
import termios
import os
import numpy as np

from rustypot import Scs0009PyController

CALIBRATION_FILE = 'calibration.json'

def load_calibration():
    if os.path.exists(CALIBRATION_FILE):
        with open(CALIBRATION_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_calibration(calib):
    with open(CALIBRATION_FILE, 'w') as f:
        json.dump(calib, f, indent=4)

def getch():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
        if ch == '\x1b':
            ch2 = sys.stdin.read(1)
            if ch2 == '[':
                ch3 = sys.stdin.read(1)
                ch = ch + ch2 + ch3
            else:
                ch = ch + ch2
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

def clear_line():
    sys.stdout.write('\r\033[K')
    sys.stdout.flush()

def main():
    print("Initializing controller...")
    try:
        c = Scs0009PyController(
            serial_port="/dev/ttyACM0",
            baudrate=1000000,
            timeout=0.5,
        )
    except Exception as e:
        print(f"Failed to connect to controller: {e}")
        return

    calib = load_calibration()
    
    if calib:
        print("Moving servos to saved zero positions...")
        for sid_str, zp in calib.items():
            s_id = int(sid_str)
            c.write_torque_enable(s_id, 1)
            c.write_goal_speed(s_id, 6)
            c.write_goal_position(s_id, np.deg2rad(zp))
        time.sleep(0.5)
    
    sid = None
    zero_point = 0.0

    def print_menu():
        print("\n" + "="*40)
        if sid is None:
            print("No servo selected. Press 1-9 to select a servo.")
        else:
            print(f"Active Servo ID: {sid} | Zero point: {zero_point}")
        print("Controls:")
        print("  1-9        : Select active servo ID")
        print("  UP arrow   : Increase zero point by 1 degree")
        print("  DOWN arrow : Decrease zero point by 1 degree")
        print("  'm'        : Move to middle (zero point)")
        print("  'o'        : Move to open position")
        print("  'k'        : Move to closed position")
        print("  'q'        : Quit and save")
        print("="*40)

    print_menu()

    while True:
        cmd = getch()
        
        if cmd == 'q' or cmd == '\x03': # q or Ctrl+C
            if sid is not None:
                calib[str(sid)] = zero_point
                c.write_torque_enable(sid, 2) # Off
            save_calibration(calib)
            print("\nSaved and exiting.")
            break
            
        elif len(cmd) == 1 and cmd.isdigit() and '1' <= cmd < '9':
            new_sid = int(cmd)
            # Save and disable old
            if sid is not None:
                calib[str(sid)] = zero_point
                c.write_torque_enable(sid, 2)
            
            # Setup new
            sid = new_sid
            sid_key = str(sid)
            if sid_key not in calib:
                calib[sid_key] = 0.0
            zero_point = calib[sid_key]
            
            c.write_torque_enable(sid, 1)
            print_menu()
            
        elif sid is not None:
            if cmd == '\x1b[A': # Up
                zero_point += 1
                pos = np.deg2rad(zero_point)
                c.write_goal_speed(sid, 6)
                c.write_goal_position(sid, pos)
                clear_line()
                sys.stdout.write(f"Servo {sid} Zero point: {zero_point}")
                sys.stdout.flush()
            elif cmd == '\x1b[B': # Down
                zero_point -= 1
                pos = np.deg2rad(zero_point)
                c.write_goal_speed(sid, 6)
                c.write_goal_position(sid, pos)
                clear_line()
                sys.stdout.write(f"Servo {sid} Zero point: {zero_point}")
                sys.stdout.flush()
            elif cmd == 'm':
                pos = np.deg2rad(zero_point)
                c.write_goal_speed(sid, 6)
                c.write_goal_position(sid, pos)
                clear_line()
                sys.stdout.write(f"Servo {sid} Moved to middle (zero={zero_point})")
                sys.stdout.flush()
            elif cmd == 'o':
                offset = -30 if sid % 2 == 0 else 30
                pos = np.deg2rad(zero_point + offset)
                c.write_goal_speed(sid, 6)
                c.write_goal_position(sid, pos)
                clear_line()
                sys.stdout.write(f"Servo {sid} Moved to open (pos={zero_point + offset})")
                sys.stdout.flush()
            elif cmd == 'k':
                offset = 90 if sid % 2 == 0 else -90
                pos = np.deg2rad(zero_point + offset)
                c.write_goal_speed(sid, 6)
                c.write_goal_position(sid, pos)
                clear_line()
                sys.stdout.write(f"Servo {sid} Moved to closed (pos={zero_point + offset})")
                sys.stdout.flush()

if __name__ == '__main__':
    main()
