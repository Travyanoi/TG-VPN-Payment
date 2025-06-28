import base64
import random
import uuid

from nacl.public import PrivateKey


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


def generate_wireguard_keypair() -> tuple[str, str]:
    private_key_obj = PrivateKey.generate()
    private_key = base64.b64encode(bytes(private_key_obj)).decode()
    public_key = base64.b64encode(bytes(private_key_obj.public_key)).decode()
    return private_key, public_key
