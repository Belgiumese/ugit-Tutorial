import os
import hashlib
import shutil

GIT_DIR = '.ugit'


def init():
    if os.path.exists(GIT_DIR):
        shutil.rmtree(GIT_DIR)
    os.makedirs(GIT_DIR, exist_ok=True)
    os.makedirs(f'{GIT_DIR}/objects', exist_ok=True)
    print(
        f'Initialised empty ugit repository in {os.getcwd()}{os.sep}{GIT_DIR}')


def hash_object(data, obj_type='blob'):
    # Add type header
    obj = obj_type.encode() + b'\x00' + data

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


def set_HEAD(oid):
    with open(f'{GIT_DIR}/HEAD', 'w') as f:
        f.write(oid)


def get_HEAD():
    head_path = f'{GIT_DIR}/HEAD'
    if (os.path.isfile(head_path)):
        with open(head_path) as f:
            return f.read().strip()
    else:
        return None
