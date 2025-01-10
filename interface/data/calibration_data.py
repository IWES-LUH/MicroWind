# Calibration data for turbine and wind tunnel.
GENERATOR_TORQUE_CONSTANT = 0.008714  # [mNm/mA] / Edit only if you have the equipment to measure
TSR_AT_20_DEG = 2.5  # [] / Edit only if you have the equipment to measure
ANGLE_AT_FRONT_LIMIT = -5  # [°] / Edit only if you have the equipment to measure
ANGLE_AT_BACK_LIMIT = 85  # [°] / Edit only if you have the equipment to measure
SERVO_TIME_FACTOR = -5.055555555555555  # [us/deg] / Calculated by calibrate_pitch.py
SERVO_TIME_BIAS = 1494.7222222222222  # [us] / Calculated by calibrate_pitch.py
DRIVETRAIN_FRICTION_TORQUE = -0.36041103999999996  # [mNm] / Calculated by calibrate.py
DRIVETRAIN_FACTOR = [3.0124157206953196e-05, 0.00012201100670135896, 0.00022737386953530547, 0.0002851602509879177, 0.0003663118665567324, 0.0004266999873273349, 0.0005398013330411129, 0.0006205043514405217, 0.0007661145092176049, 0.0008657988635002594, 0.0010811495696738435, 0.0011895270982284851, 0.0014536392748368382]  # [mNm/rpm] / Calculated by calibrate.py
DRIVETRAIN_BIAS = [0.0, -0.03224180000000004, -0.014378100000000005, -0.006012660000000003, 0.011328199999999955, 0.02893047999999998, 0.06265365999999994, 0.08104019999999995, 0.12304167999999999, 0.15005507999999998, 0.20181623999999998, 0.23719507999999995, 0.30559998]  # [mNm/�] / Calculated by calibrate.py
FAN_PWM_FACTOR = 36.07816743861474  # [-/(m/s)] / Calculated by calibrate_wind.py
FAN_PWM_BIAS = 17.056928034371623  # [-] / Calculated by calibrate_wind.py
WIND_SPEED_FACTOR = 0.00452081092183158  # [(m/s)/(rpm)] / Calculated by calibrate_wind.py
WIND_SPEED_BIAS = -0.1711886876887747  # [m/s] / Calculated by calibrate_wind.py
ANEMOMETER_READ = [184.44912, 217.0184, 227.83344, 235.58, 241.72624, 246.38144]  # [-] / Calculated by calibrate.py
ANEMOMETER_WIND = [0, 1, 2, 3, 4, 5]  # [m/S] / Calculated by calibrate.py
THRUST_FACTOR = 1/655  # [mN/-] / Calculated by calibrate_thrust.py
POTENTIOMETER_FACTOR = -0.2174  # [-] / Calibrate yourself
POTENTIOMETER_BIAS = 192  # [-] / Calibrate yourself