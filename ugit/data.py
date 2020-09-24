import os
import hashlib
import shutil
import string

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


def update_ref(ref, oid):
    # Keep track of refs just by storing the OID in a file with name
    path = f'{GIT_DIR}/{ref}'
    # If it doesn't already exist, create this path
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        f.write(oid)


def get_ref(ref):
    # Open the ref file with name ref and get the OID from it
    ref_path = f'{GIT_DIR}/{ref}'
    if (os.path.isfile(ref_path)):
        with open(ref_path) as f:
            return f.read().strip()
    else:
        return None


def is_oid(name):
    if len(name) != 40:
        return False

    is_hex = all(c in string.hexdigits for c in name)
    return is_hex
