import os
import sys
import logging

logger = logging.getLogger(__name__)

from drive_io import DriveIO


def upload(token, filepath):

    if os.path.exists(filepath) and os.path.exists(token):
        logger.info("Starting upload")
        g_drive = DriveIO(token)
        g_drive.upload(filepath, only_root_flag=True)
    else:
        logger.info(filepath + " or " + token + " do not exist")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Upload a folder to the trojai google drive.')

    parser.add_argument('--token-pickle-filepath', type=str,
                        help='Path token.pickle file holding the oauth keys.',
                        default='token.pickle')
    parser.add_argument('--filepath', type=str,
                        help='The file or directory to upload',
                        required=True)

    args = parser.parse_args()

    # setup logger
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s [%(levelname)s] [%(filename)s:%(lineno)d] %(message)s",
                        stream=sys.stdout)


    token = args.token_pickle_filepath
    filepath = args.filepath

    try_nb = 0
    max_nb_tries = 2
    done = False
    while not done and try_nb < max_nb_tries:
        try:
            try_nb = try_nb + 1
            upload(token, filepath)
            done = True
        except:
            logger.info('failed, retrying')
            pass



