# NIST-developed software is provided by NIST as a public service. You may use, copy and distribute copies of the software in any medium, provided that you keep intact this entire notice. You may improve, modify and create derivative works of the software or any portion of the software, and you may copy and distribute such modifications or works. Modified works should carry a notice stating that you changed the software and should note the date and nature of any such change. Please explicitly acknowledge the National Institute of Standards and Technology as the source of the software.

# NIST-developed software is expressly provided "AS IS." NIST MAKES NO WARRANTY OF ANY KIND, EXPRESS, IMPLIED, IN FACT OR ARISING BY OPERATION OF LAW, INCLUDING, WITHOUT LIMITATION, THE IMPLIED WARRANTY OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, NON-INFRINGEMENT AND DATA ACCURACY. NIST NEITHER REPRESENTS NOR WARRANTS THAT THE OPERATION OF THE SOFTWARE WILL BE UNINTERRUPTED OR ERROR-FREE, OR THAT ANY DEFECTS WILL BE CORRECTED. NIST DOES NOT WARRANT OR MAKE ANY REPRESENTATIONS REGARDING THE USE OF THE SOFTWARE OR THE RESULTS THEREOF, INCLUDING BUT NOT LIMITED TO THE CORRECTNESS, ACCURACY, RELIABILITY, OR USEFULNESS OF THE SOFTWARE.

# You are solely responsible for determining the appropriateness of using and distributing the software and you assume all risks associated with its use, including but not limited to the risks and costs of program errors, compliance with applicable laws, damage to or loss of data, programs or equipment, and the unavailability or interruption of operation. This software is not intended to be used in any situation where a failure could cause risk of injury or damage to property. The software developed by NIST employees is not subject to copyright protection within the United States.

import os
import fcntl
import json
import logging


def _open_lock_file(filepath):
    # per-file lock next to the target, created owner-only, never truncated, and never followed if it is a symlink
    fd = os.open(filepath + '.lock', os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o600)
    return os.fdopen(fd, 'r+')


def write(filepath, obj):
    assert filepath.endswith('.json')
    with _open_lock_file(filepath) as lfh:
        try:
            fcntl.lockf(lfh, fcntl.LOCK_EX)
            with open(filepath, mode='w', encoding='utf-8') as f:
                json.dump(obj, f, indent=2)
        except:
            msg = 'json_io failed writing file "{}" releasing file lock regardless.'.format(filepath)
            logging.error(msg)
            raise
        finally:
            fcntl.lockf(lfh, fcntl.LOCK_UN)


def read(filepath):
    assert filepath.endswith('.json')
    with _open_lock_file(filepath) as lfh:
        try:
            fcntl.lockf(lfh, fcntl.LOCK_EX)
            with open(filepath, mode='r', encoding='utf-8') as f:
                obj = json.load(f)
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

