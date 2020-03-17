import fcntl
import json
import jsonpickle
import logging


def write(filepath, obj):
    assert filepath.endswith('.json')
    lock_file = '/var/lock/trojai-json_io-lockfile'
    with open(lock_file, 'w') as lfh:
        try:
            fcntl.lockf(lfh, fcntl.LOCK_EX)
            with open(filepath, mode='w', encoding='utf-8') as f:
                f.write(jsonpickle.encode(obj, warn=True))
        except:
            msg = 'json_io failed writing file "{}" releasing file lock regardless.'.format(filepath)
            logging.error(msg)
            raise
        finally:
            fcntl.lockf(lfh, fcntl.LOCK_UN)


def read(filepath):
    assert filepath.endswith('.json')
    lock_file = '/var/lock/trojai-json_io-lockfile'
    with open(lock_file, 'w') as lfh:
        try:
            fcntl.lockf(lfh, fcntl.LOCK_EX)
            with open(filepath, mode='r', encoding='utf-8') as f:
                obj = jsonpickle.decode(f.read())
        except json.decoder.JSONDecodeError:
            logging.error("JSON decode error for file: {}, is it a proper json?".format(filepath))
            raise
        except:
            msg = 'json_io failed reading file "{}" releasing file lock regardless.'.format(filepath)
            logging.error(msg)
            raise
        finally:
            fcntl.lockf(lfh, fcntl.LOCK_UN)
    return obj
