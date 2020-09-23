import os
import shutil
from . import data


def write_tree(directory='.'):
    entries = []
    oid = None
    file_type = None

    with os.scandir(directory) as direct:
        for entry in direct:
            file_path = f'{directory}{os.sep}{entry.name}'

            if (is_ignored(file_path)):
                continue
            elif entry.is_file(follow_symlinks=False):
                file_type = 'blob'
                with open(file_path, 'rb') as f:
                    oid = data.hash_object(f.read())
            elif entry.is_dir(follow_symlinks=False):
                file_type = 'tree'
                oid = write_tree(file_path)

            entries.append((entry.name, oid, file_type))

    tree = ''.join(f'{file_type} {oid} {name}\n' for name,
                   oid, file_type in sorted(entries))
    return data.hash_object(tree.encode(), 'tree')


def _empty_current_directory():
    for path in os.listdir('.'):
        if (not is_ignored(path)):
            if (os.path.isfile(path)):
                os.remove(path)
            else:
                shutil.rmtree(path)


def _iter_tree_entries(oid):
    # Iterator for every child node of a tree node
    if not oid:
        return
    tree = data.get_object(oid, 'tree')
    for entry in tree.decode().splitlines():
        entry_type, oid, name = entry.split(' ', 2)
        yield entry_type, oid, name


def get_tree(oid, base_path=''):
    # Iterate through the whole tree and turn it into a dictionary
    result = {}
    for entry_type, oid, name in _iter_tree_entries(oid):
        # For each immediate child, add it to the result
        path = base_path + name
        if entry_type == 'blob':
            result[path] = oid
        elif entry_type == 'tree':
            # Recurse and add it to this dict
            result.update(get_tree(oid, path + os.sep))

    return result


def read_tree(tree_oid):
    _empty_current_directory()
    # For every path/oid in the tree, make it and write the object to it
    for path, oid in get_tree(tree_oid, base_path=f'.{os.sep}').items():
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'wb') as f:
            f.write(data.get_object(oid))


def is_ignored(path):
    return '.ugit' in path.split(os.sep)
