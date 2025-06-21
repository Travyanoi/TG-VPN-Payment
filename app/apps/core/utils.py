import random
import uuid


def generate_md5_token():
    return uuid.uuid4().hex


def default_extra_conf():
    random.seed()
    jc = random.randint(3, 127)
    jmin = random.randint(3, 700)
    jmax = random.randint(jmin + 1, 1270)
    return {
        "Jc": jc,
        "Jmin": jmin,
        "Jmax": jmax,
        "S1": random.randint(3, 127),
        "S2": random.randint(3, 127),
        "H1": random.randint(0x10000011, 0x7FFFFF00),
        "H2": random.randint(0x10000011, 0x7FFFFF00),
        "H3": random.randint(0x10000011, 0x7FFFFF00),
        "H4": random.randint(0x10000011, 0x7FFFFF00),
    }
