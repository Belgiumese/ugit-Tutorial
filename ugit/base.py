import os
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


def is_ignored(path):
    return '.ugit' in path.split(os.sep)
