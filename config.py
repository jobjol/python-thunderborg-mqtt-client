client_name = 'raspberry_1'
broker = 'home.jobjol.com'
port = 1883

# Tell the system how to drive the stepper
maxPower = 1.00                         # Output to drive the stepper
holdingPower = 0.50                     # Output to drive the stepper when holding
sequence = [                            # Order for stepping
    [+maxPower, +maxPower],
    [+maxPower, -maxPower],
    [-maxPower, -maxPower],
    [-maxPower, +maxPower]]
sequenceHold = [                        # Order for stepping at holding power
    [+holdingPower, +holdingPower],
    [+holdingPower, -holdingPower],
    [-holdingPower, -holdingPower],
    [-holdingPower, +holdingPower]]
stepDelay = 0.002
