import os
import shutil
from collections import namedtuple
from . import data

Commit = namedtuple('Commit', ['tree', 'parent', 'message'])


def write_tree(directory='.'):
    entries = []
    oid = None
    file_type = None

    # For every file/directory in the current directory
    with os.scandir(directory) as direct:
        for entry in direct:
            file_path = f'{directory}{os.sep}{entry.name}'

            if (is_ignored(file_path)):
                # Ignore things like '.ugit'
                continue
            elif entry.is_file(follow_symlinks=False):
                # If it's a file, hash it as a blob.
                file_type = 'blob'
                with open(file_path, 'rb') as f:
                    oid = data.hash_object(f.read())
            elif entry.is_dir(follow_symlinks=False):
                # If it's a directory, hash it as another tree recursively.
                file_type = 'tree'
                oid = write_tree(file_path)

            entries.append((entry.name, oid, file_type))

    # Our tree is a list of all the entries in this directory
    # with their file type, oid, and file name.
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


def commit(message):
    # Link to the new tree of contents
    commit_msg = f'tree {write_tree()}\n'

    # Add link to previous HEAD (parent) if it exists
    head = data.get_HEAD()
    if (head):
        commit_msg += f'parent {head}\n'

    # Add commit message
    commit_msg += '\n'
    commit_msg += f'{message}\n'

    # Hash the commit itself and set the head to it
    oid = data.hash_object(commit_msg.encode(), 'commit')
    data.set_HEAD(oid)

    return oid


def get_commit(oid):
    commit = data.get_object(oid, 'commit').decode()
    parent = None
    tree = None

    lines = iter(commit.splitlines())
    for line in lines:
        if (len(line) == 0):
            # This is the message separator
            break

        key, val = line.split(' ', 1)
        if key == 'tree':
            tree = val
        elif key == 'parent':
            parent = val
        else:
            raise IOError(f'Unknown commit field {key}')

    message = ''.join(lines)
    return Commit(tree=tree, parent=parent, message=message)


def checkout(oid):
    commit = get_commit(oid)
    read_tree(commit.tree)
    data.set_HEAD(oid)
