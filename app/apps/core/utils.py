import uuid


def generate_md5_token():
    return uuid.uuid4().hex
