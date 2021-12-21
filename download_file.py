import os
import traceback

from drive_io import DriveIO


def download(token, filename, folder, output_filepath):
    if not os.path.exists(output_filepath):
        os.makedirs(output_filepath)

    print('Instantiating Drive object')
    g_drive = DriveIO(token)

    print('Making query to drive')
    query = "name = '{}' and trashed = false".format(filename, folder)
    print(query)
    file_list = g_drive.query_worker(query)

    selected_gfile = None
    for gfile in file_list:
        response = g_drive.service.files().get(fileId=gfile.parents[0],
                                             fields="name").execute()

        if response['name'] == folder:
            selected_gfile = gfile
            break

    if selected_gfile is not None:
        print('Found file {} in folder {}. Downloading'.format(filename, folder))
        g_drive.download(selected_gfile, output_filepath)
    else:
        print('Failed to find file {} in folder {}. Terminating'.format(filename, folder))


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Upload a folder to the trojai google drive.')

    parser.add_argument('--token-pickle-filepath', type=str,
                        help='Path token.pickle file holding the oauth keys.',
                        default='token.pickle')
    parser.add_argument('--filename', type=str,
                        help='The filename to download from drive',
                        required=True)
    parser.add_argument('--folder', type=str,
                        help='The folder to download from on drive',
                        default="My Drive")
    parser.add_argument('--output_dirpath', type=str,
                        help='The folder to download into on your local machine',
                        required=True)

    args = parser.parse_args()

    token = args.token_pickle_filepath
    filename = args.filename
    folder = args.folder
    output_dirpath = args.output_dirpath
    print('Args: ')
    print('token = {}'.format(token))
    print('filename = {}'.format(filename))
    print('folder = {}'.format(folder))
    print('output_dirpath = {}'.format(output_dirpath))

    try_nb = 0
    max_nb_tries = 1
    done = False
    while not done and try_nb < max_nb_tries:
        try:
            try_nb = try_nb + 1
            download(token, filename, folder, output_dirpath)
            done = True
        except Exception as e:
            traceback.print_exc()
            traceback.print_stack()
            print('failed, retrying')
            pass



