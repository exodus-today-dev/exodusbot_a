GREEN_BALL = '\U0001F7E2'
ORANGE_BALL = '\U0001F7E0'
RED_BALL = '\U0001F534'

HEART_RED = '\U00002764'
HANDSHAKE = '\U0001F91D'
HELP = '\U0001F64F'

RIGHT_ARROW = '\U000027A1'

def get_status(text):
    if text == "green":
        status = GREEN_BALL
    elif text == "orange":
        status = ORANGE_BALL
    elif 'red' in text:
        status = RED_BALL
    return status
