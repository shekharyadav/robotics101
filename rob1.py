{
    "mode": "Text",
    "hardwareTarget": "brain",
    "textContent": '#region VEXcode Generated Robot Configuration
from vex import *
import urandom

# Brain should be defined by default
brain=Brain()

# Robot configuration code
brain_inertial = Inertial()
left_drive_smart = Motor(Ports.PORT6, 3.0, False)
right_drive_smart = Motor(Ports.PORT12, 3.0, True)

drivetrain = SmartDrive(left_drive_smart, right_drive_smart, brain_inertial, 200)
controller = Controller()
BallShooter_right = Motor(Ports.PORT3, False)
BallShooter_left = Motor(Ports.PORT10, True)
LowerCollector = Motor(Ports.PORT11, True)
UpperCollector = Motor(Ports.PORT5, False)
pneumatic_one = Pneumatic(Ports.PORT1)
light_up_first = Touchled(Ports.PORT2)
light_up_second = Touchled(Ports.PORT9)
ball_ready = Distance(Ports.PORT7)
ball_loaded = Distance(Ports.PORT8)
pneumatic_two = Pneumatic(Ports.PORT4)



# generating and setting random seed
def initializeRandomSeed():
    wait(100, MSEC)
    xaxis = brain_inertial.acceleration(XAXIS) * 1000
    yaxis = brain_inertial.acceleration(YAXIS) * 1000
    zaxis = brain_inertial.acceleration(ZAXIS) * 1000
    systemTime = brain.timer.system() * 100
    urandom.seed(int(xaxis + yaxis + zaxis + systemTime)) 
    
# Initialize random seed 
initializeRandomSeed()

vexcode_initial_drivetrain_calibration_completed = False
def calibrate_drivetrain():
    # Calibrate the Drivetrain Inertial
    global vexcode_initial_drivetrain_calibration_completed
    if not vexcode_initial_drivetrain_calibration_completed:
        pneumatic_one.pump_off()
        pneumatic_two.pump_off()
    sleep(200, MSEC)
    brain.screen.print("Calibrating")
    brain.screen.next_row()
    brain.screen.print("Inertial")
    brain_inertial.calibrate()
    while brain_inertial.is_calibrating():
        sleep(25, MSEC)
    if not vexcode_initial_drivetrain_calibration_completed:
        pneumatic_one.pump_on()
        pneumatic_two.pump_on()
    vexcode_initial_drivetrain_calibration_completed = True
    brain.screen.clear_screen()
    brain.screen.set_cursor(1, 1)


# Calibrate the Drivetrain
calibrate_drivetrain()



# define variables used for controlling motors based on controller inputs
drivetrain_l_needs_to_be_stopped_controller = False
drivetrain_r_needs_to_be_stopped_controller = False

# define a task that will handle monitoring inputs from controller
def rc_auto_loop_function_controller():
    global drivetrain_l_needs_to_be_stopped_controller, drivetrain_r_needs_to_be_stopped_controller, remote_control_code_enabled
    # process the controller input every 20 milliseconds
    # update the motors based on the input values
    while True:
        if remote_control_code_enabled:
            
            # calculate the drivetrain motor velocities from the controller joystick axies
            # left = axisA + axisC
            # right = axisA - axisC
            drivetrain_left_side_speed = controller.axisA.position() + controller.axisC.position()
            drivetrain_right_side_speed = controller.axisA.position() - controller.axisC.position()
            
            # check if the value is inside of the deadband range
            if drivetrain_left_side_speed < 5 and drivetrain_left_side_speed > -5:
                # check if the left motor has already been stopped
                if drivetrain_l_needs_to_be_stopped_controller:
                    # stop the left drive motor
                    left_drive_smart.stop()
                    # tell the code that the left motor has been stopped
                    drivetrain_l_needs_to_be_stopped_controller = False
            else:
                # reset the toggle so that the deadband code knows to stop the left motor next
                # time the input is in the deadband range
                drivetrain_l_needs_to_be_stopped_controller = True
            # check if the value is inside of the deadband range
            if drivetrain_right_side_speed < 5 and drivetrain_right_side_speed > -5:
                # check if the right motor has already been stopped
                if drivetrain_r_needs_to_be_stopped_controller:
                    # stop the right drive motor
                    right_drive_smart.stop()
                    # tell the code that the right motor has been stopped
                    drivetrain_r_needs_to_be_stopped_controller = False
            else:
                # reset the toggle so that the deadband code knows to stop the right motor next
                # time the input is in the deadband range
                drivetrain_r_needs_to_be_stopped_controller = True
            
            # only tell the left drive motor to spin if the values are not in the deadband range
            if drivetrain_l_needs_to_be_stopped_controller:
                left_drive_smart.set_velocity(drivetrain_left_side_speed, PERCENT)
                left_drive_smart.spin(FORWARD)
            # only tell the right drive motor to spin if the values are not in the deadband range
            if drivetrain_r_needs_to_be_stopped_controller:
                right_drive_smart.set_velocity(drivetrain_right_side_speed, PERCENT)
                right_drive_smart.spin(FORWARD)
        # wait before repeating the process
        wait(20, MSEC)

# define variable for remote controller enable/disable
remote_control_code_enabled = True

rc_auto_loop_thread_controller = Thread(rc_auto_loop_function_controller)

#endregion VEXcode Generated Robot Configuration

# Variable controls if collector should be stopped
collector_stopped = False

# Variable informs if the collector is running or stopped
is_collector_stopped = False

# variable controls if autonomous second function should be running or notv
is_autonomous_second_running = False

# Drive train velocity
DRIVE_VELOCITY = 60

# shooter speed (flywheel velocity)
# High velocity will make the ball shoot higher and further
# low velocity will make the ball shoot low
SHOOTER_SPEED = 75

# Restarts the ball shooter
def restart_ball_shooter():
    BallShooter_right.stop()
    BallShooter_left.stop()
    BallShooter_right.spin_for(REVERSE, 900000, DEGREES, wait=False) 
    BallShooter_left.spin_for(REVERSE, 900000, DEGREES, wait=False)

# Set the ball shooters speed to high speed and restart the flywheels (ball shooter) so new velocity takes effect
# This is unnecessary code now because we are not using speed to control the low/high goals
def set_shoot_higher():
    brain.play_sound(SoundType.SIREN)
    BallShooter_right.set_velocity(SHOOTER_SPEED, PERCENT)
    BallShooter_left.set_velocity(SHOOTER_SPEED, PERCENT)
    restart_ball_shooter()

# Set the shooting mechanism to high position
def set_shoot_high():
    brain.play_sound(SoundType.SIREN)
    pneumatic_two.extend(CYLINDER1)
    pneumatic_two.extend(CYLINDER2)
    
# Drops the shooting mechanism to low position
# in this position the ball automatically (gravity) moves to the flywheel
# so all we have to do is set the shooting mechanism to low position and ball will shoot
# We then reset the shooting mechanism to point at high position
def set_shoot_low():
    brain.play_sound(SoundType.ALARM2)
    global collector_stopped
    collector_stopped = True
    pneumatic_two.retract(CYLINDER1)
    pneumatic_two.retract(CYLINDER2)
    wait(0.5,SECONDS)
    pneumatic_two.extend(CYLINDER1)
    pneumatic_two.extend(CYLINDER2)
    wait(1,SECONDS)
    collector_stopped = False
    
# extends the penuamtics to loading position so a new ball can be loaded
def load():
    pneumatic_one.extend(CYLINDER1)
    pneumatic_one.extend(CYLINDER2)

# Retracts the penumatics to move the ball towards the flywheels
def shoot():
    pneumatic_one.retract(CYLINDER1)
    pneumatic_one.retract(CYLINDER2)

# Stops the collectors (so as to transfer most power to the shooter)
# Shoots by retracting the penumatics and then extending them again
# starts the collector again
def shoot_and_load():
    global collector_stopped
    collector_stopped = True
    wait(.5, SECONDS)
    shoot()
    wait(.5,SECONDS)
    load()
    collector_stopped = False

# Starts collecting
def collector_collect():
    LowerCollector.spin_for(FORWARD, 90000, DEGREES, wait=False)
    UpperCollector.spin_for(FORWARD, 90000, DEGREES, wait=False)

# Reverses the collector direction to spit the balls out
def collector_spit_out():
    LowerCollector.spin_for(REVERSE, 90000, DEGREES, wait=False)
    UpperCollector.spin_for(REVERSE, 90000, DEGREES, wait=False)

# stops both the collectors
def collector_stop():
    LowerCollector.stop()
    UpperCollector.stop()

# this is the controller event loop
# it runs behind the scenes periodically every 100 ms
# it checks if the balls are loaded if so then stops the collector
# if either of the ball is not loaded it will start the collector
# if the variable collector_stopped=True it will also stop the collector
def run_collector_controller():
    global is_collector_stopped
    if collector_stopped:
        collector_stop()
        is_collector_stopped = True
        brain.screen.clear_screen()
        brain.screen.set_cursor(1, 1)
        brain.screen.print("csV")
    else:
        # check if both ball_loaded and ball_ready is true then we stop 
        # otherwise we start collecting again
        if ball_loaded.object_distance(MM) < 20 and ball_ready.object_distance(MM) < 50:
            collector_stop()
            is_collector_stopped = True
            brain.screen.clear_screen()
            brain.screen.set_cursor(1, 1)
            brain.screen.print("csB")
        else:
            collector_collect()
            is_collector_stopped = False
            brain.screen.clear_screen()
            brain.screen.set_cursor(1, 1)
            brain.screen.print("cRun")
    
    # trigger the next run
    brain.timer.event(run_collector_controller, 100)

# first autonomous function, its goal is to take two balls
# and score the high and low goals only then it stops
# the user must then transfer the robot to the other side
# and start the second program
def start_autonomous_first():
    start_robot()

    drivetrain.set_drive_velocity(DRIVE_VELOCITY, PERCENT)
    drivetrain.set_stopping(COAST)
    brain.play_sound(SoundType.SIREN)

    set_shoot_higher()
    
    # wait for both balls to load, the collector will stop then
    while not is_collector_stopped:
        wait(0.1, SECONDS)

    drivetrain.drive_for(FORWARD, 50, INCHES ,wait=False)
    wait(3, SECONDS)
    # drivetrain.stop()
    set_shoot_low()
    wait(2.5, SECONDS)
    shoot_and_load()
    stop_robot()

# Wait for the collector to stop or the a timeout of 3 second happens
def wait_for_collector_with_timeout():
    count = 0
    while not is_collector_stopped and count <= 30 and is_autonomous_second_running:
        wait(0.1, SECONDS)
        if count==10 or count==20 or count==30:
            brain.play_sound(SoundType.TADA)    
        count=count+1    

# when the light up sensor is pressed it starts the second autonomous function
# if the sensor is pressed again it will stop the function by setting is_autonomous_second_running = False
def toggle_autonomous_second():
    global is_autonomous_second_running
    if is_autonomous_second_running:
        light_up_second.set_color(Color.YELLOW)
        brain.play_sound(SoundType.POWER_DOWN)
        stop_robot()
        is_autonomous_second_running = False
    else:
        brain.play_sound(SoundType.ALARM)
        light_up_second.set_color(Color.RED)
        is_autonomous_second_running = True
        global collector_stopped
        global is_collector_stopped
        start_robot()
        collector_stopped = False
        is_collector_stopped = False        
        # do not call the start_autonomous_second in this function, it will block the sensor callback function
        brain.timer.event(start_autonomous_second, 10)

# Second autonomus code, its goal is to score low and high goals
# then run in a forever loop of collecting two balls and shooting them high
# the robot has a timeout of 3 seconds, if balls are not loaded within 3 seconds
# the robot will proceed to shoot them
# note this function will quit if is_autonomous_second_running is set to False
def start_autonomous_second():
    # set drivetrain velocity for autonomous (different then manual)
    drivetrain.set_drive_velocity(DRIVE_VELOCITY, PERCENT)
    drivetrain.set_stopping(COAST)
    brain.play_sound(SoundType.SIREN)
    set_shoot_higher()


    # wait for both balls to load, the collector will stop then
    wait_for_collector_with_timeout()
    if not is_autonomous_second_running:
        return
    # drive forward again
    drivetrain.drive_for(FORWARD, 50, INCHES ,wait=False)
    if not is_autonomous_second_running:
        return
    wait(2.5, SECONDS)
    #drivetrain.stop()
    brain.play_sound(SoundType.ALARM2)
    if not is_autonomous_second_running:
        return
    set_shoot_low()
    if not is_autonomous_second_running:
        return
    wait(1.75, SECONDS)
    if not is_autonomous_second_running:
        return
    shoot_and_load()
    if not is_autonomous_second_running:
        return

    drivetrain.drive_for(REVERSE, 28, INCHES, True)

    while is_autonomous_second_running:
        # wait for both balls to load, the collector will stop then
        # add a counter so we don\'t wait for ever
        wait_for_collector_with_timeout()
        if not is_autonomous_second_running:
            return
        
        # drive forward again
        drivetrain.drive_for(FORWARD, 50, INCHES ,wait=False)
        wait(2, SECONDS)
        if not is_autonomous_second_running:
            return
        drivetrain.stop()
        brain.play_sound(SoundType.ALARM2)        
        shoot_and_load()
        if not is_autonomous_second_running:
            return        
        wait(1.75, SECONDS)
        if not is_autonomous_second_running:
            return        
        shoot_and_load()
        if not is_autonomous_second_running:
            return        
        drivetrain.drive_for(REVERSE, 28, INCHES, True)


# Starts the moving parts of the robot including pneumatic pump
def start_robot():
    global collector_stopped
    global is_collector_stopped
    collector_stopped = False
    is_collector_stopped = False
    restart_ball_shooter()
    pneumatic_one.pump_on()

# This stops all moving parts of the robot including the pneumatic
# this does not stop the collector event loop which will continue running
# It uses the collector_stopped variable to inform the collector event loop that it should 
# stop the collector
def stop_robot():
     global collector_stopped
     global is_collector_stopped
     collector_stopped=True
     is_collector_stopped = True
     drivetrain.stop()
     BallShooter_right.stop()
     BallShooter_left.stop()
     pneumatic_one.pump_off()

# This method is called when program is started
def when_started():
    light_up_first.set_color(Color.GREEN)
    light_up_second.set_color(Color.YELLOW)

    drivetrain.set_stopping(COAST)
    drivetrain.set_drive_velocity(100, PERCENT)
    drivetrain.set_turn_velocity(27, PERCENT)
    BallShooter_right.set_stopping(COAST)
    BallShooter_left.set_stopping(COAST)
    BallShooter_right.set_max_torque(100, PERCENT)
    BallShooter_left.set_max_torque(100, PERCENT)
    BallShooter_right.set_velocity(SHOOTER_SPEED, PERCENT)
    BallShooter_left.set_velocity(SHOOTER_SPEED, PERCENT)

    LowerCollector.set_max_torque(100, PERCENT)
    LowerCollector.set_velocity(100, PERCENT)
    LowerCollector.set_stopping(HOLD)
    UpperCollector.set_max_torque(100, PERCENT)
    UpperCollector.set_velocity(100, PERCENT)
    UpperCollector.set_stopping(HOLD)

    #controller stuff
    controller.buttonRUp.pressed(collector_collect)
    controller.buttonRDown.pressed(collector_spit_out)

    controller.buttonFUp.pressed(shoot_and_load)
    controller.buttonFDown.pressed(set_shoot_low)
    controller.buttonEDown.pressed(collector_stop)

    # controller.buttonEUp.pressed(shoot_and_load)
    controller.buttonLUp.pressed(start_robot)
    controller.buttonLDown.pressed(stop_robot)

    # Autonmous callback
    light_up_first.pressed(start_autonomous_first)
    light_up_second.pressed(toggle_autonomous_second)

    # Start the collector controller loop/
    # This loop runs periodically every 100 ms
    # it checks if the balls are loaded if so then stops the collector
    # if either of the balls is not loaded it starts the collector
    # if the variable collector_stopped is True then it also stops the collector
    # use this variable collector_stopped if you want to stop the collector
    # regardless of if ball is loaded or not
    global collector_stopped
    collector_stopped=True
    brain.timer.event(run_collector_controller, 100)

when_started()
# pandas rule!!!!!!!!!!!!!
# hamsters rule!!!!!!!!
# 
',
    "textLanguage": "python",
    "robotConfig": [
        {
            "port": [6, 12, 0],
            "name": "drivetrain",
            "customName": false,
            "deviceType": "Drivetrain",
            "deviceClass": "smartdrive",
            "setting": {
                "type": "2-motor",
                "wheelSize": "200mm",
                "gearRatio": "3:1",
                "direction": "fwd",
                "gyroType": "integrated",
                "width": "173",
                "unit": "mm",
                "wheelbase": "76",
                "wheelbaseUnit": "mm",
                "xOffset": "0",
                "yOffset": "0",
                "thetaOffset": "0",
            },
            "triportSourcePort": 22,
        },
        {
            "port": [],
            "name": "controller",
            "customName": false,
            "deviceType": "Controller",
            "deviceClass": "controller",
            "setting": {
                "left": "",
                "leftDir": "false",
                "right": "",
                "rightDir": "false",
                "e": "",
                "eDir": "false",
                "f": "",
                "fDir": "false",
                "l3r3": "",
                "l3r3Dir": "false",
                "drive": "split",
            },
            "triportSourcePort": 22,
        },
        {
            "port": [3],
            "name": "BallShooter_right",
            "customName": true,
            "deviceType": "Motor",
            "deviceClass": "motor",
            "setting": {"reversed": "false", "fwd": "forward", "rev": "reverse"},
            "triportSourcePort": 22,
        },
        {
            "port": [10],
            "name": "BallShooter_left",
            "customName": true,
            "deviceType": "Motor",
            "deviceClass": "motor",
            "setting": {"reversed": "true", "fwd": "forward", "rev": "reverse"},
            "triportSourcePort": 22,
        },
        {
            "port": [11],
            "name": "LowerCollector",
            "customName": true,
            "deviceType": "Motor",
            "deviceClass": "motor",
            "setting": {"reversed": "true", "fwd": "forward", "rev": "reverse"},
            "triportSourcePort": 22,
        },
        {
            "port": [5],
            "name": "UpperCollector",
            "customName": true,
            "deviceType": "Motor",
            "deviceClass": "motor",
            "setting": {"reversed": "false", "fwd": "forward", "rev": "reverse"},
            "triportSourcePort": 22,
        },
        {
            "port": [1],
            "name": "pneumatic_one",
            "customName": true,
            "deviceType": "Pneumatic",
            "deviceClass": "pneumatic",
            "setting": {
                "cylinder1": "cylinder1",
                "cylinder2": "cylinder2",
                "cylinder1_reversed": "false",
                "cylinder2_reversed": "false",
                "cylinder3": "",
                "cylinder4": "",
            },
            "triportSourcePort": 22,
        },
        {
            "port": [2],
            "name": "light_up_first",
            "customName": true,
            "deviceType": "TouchLED",
            "deviceClass": "touchled",
            "setting": {},
            "triportSourcePort": 22,
        },
        {
            "port": [9],
            "name": "light_up_second",
            "customName": true,
            "deviceType": "TouchLED",
            "deviceClass": "touchled",
            "setting": {},
            "triportSourcePort": 22,
        },
        {
            "port": [7],
            "name": "ball_ready",
            "customName": true,
            "deviceType": "Distance",
            "deviceClass": "distance",
            "setting": {},
            "triportSourcePort": 22,
        },
        {
            "port": [8],
            "name": "ball_loaded",
            "customName": true,
            "deviceType": "Distance",
            "deviceClass": "distance",
            "setting": {},
            "triportSourcePort": 22,
        },
        {
            "port": [4],
            "name": "pneumatic_two",
            "customName": true,
            "deviceType": "Pneumatic",
            "deviceClass": "pneumatic",
            "setting": {
                "cylinder1": "cylinder1",
                "cylinder2": "cylinder2",
                "cylinder1_reversed": "false",
                "cylinder2_reversed": "false",
                "cylinder3": "",
                "cylinder4": "",
            },
            "triportSourcePort": 22,
        },
    ],
    "slot": 0,
    "platform": "IQ",
    "sdkVersion": "20230818.11.00.00",
    "appVersion": "4.0.7",
    "minVersion": "3.0.0",
    "fileFormat": "2.0.0",
    "targetBrainGen": "Second",
    "v5SoundsEnabled": false,
    "target": "Physical",
}

