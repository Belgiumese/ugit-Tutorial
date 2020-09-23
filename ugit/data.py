import os
import hashlib

GIT_DIR = '.ugit'


def init():
    os.makedirs(GIT_DIR, exist_ok=True)
    os.makedirs(f'{GIT_DIR}/objects', exist_ok=True)
    print(
        f'Initialised empty ugit repository in {os.getcwd()}{os.sep}{GIT_DIR}')


def hash_object(obj, ob_type='blob'):
    # Add type header
    obj = ob_type.encode() + b'x\00' + obj

    oid = hashlib.sha1(obj).hexdigest()
    with open(f'{GIT_DIR}/objects/{oid}', 'wb') as f:
        f.write(obj)

    return oid


def get_object(oid, expected='blob'):
    with open(f'{GIT_DIR}/objects/{oid}', 'rb') as f:
        obj = f.read()

    first_null = obj.index(b'\x00')
    obj_type = obj[:first_null].decode()
    content = obj[first_null + 1:]

    if (expected is not None and obj_type != expected):
        raise IOError(f'Expected object of type {expected}, got {obj_type}')

    return content
