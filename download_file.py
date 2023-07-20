import os
import traceback

import drive_io
from drive_io import DriveIO
from google_drive_file import GoogleDriveFile


def get_file_by_id(g_drive: drive_io.DriveIO, id: str) -> GoogleDriveFile:
    query = "id = '{}' and trashed = false".format(id)
    file_list = g_drive.query_worker(query)
    if len(file_list) == 0:
        return None
    elif len(file_list) > 1:
        return None
    else:
        return file_list[0]


def download(token, filename, folder, output_filepath):
    if not os.path.exists(output_filepath):
        os.makedirs(output_filepath)

    print('Instantiating Drive object')
    g_drive = DriveIO(token)

    print('Making query to drive')
    query = "name = '{}' and trashed = false".format(filename)
    print(query)
    file_list = g_drive.query_worker(query)

    selected_file_list = list()

    for gfile in file_list:
        file_stack = list()
        file_stack.insert(0, gfile.name)

        fid = gfile.parents[0]
        while True:
            response = g_drive.service.files().get(fileId=fid, fields="name, parents, id").execute()
            if 'name' not in response:
                # print("Found file with matching name, with the incorrect parent folder at path: {}".format(file_stack))
                break
            file_stack.insert(0, response['name'])
            if response['name'] == folder:
                selected_file_list.append(gfile)
                file_stack.insert(0, "...")
                print("Found file with matching name, with the following path: {}".format(file_stack))
                break
            if 'parents' not in response:
                # print("Found file with matching name, with the incorrect parent folder at path: {}".format(file_stack))
                break
            fid = response['parents'][0]


    if len(selected_file_list) > 1:
        print('Found {} files matching the query parameters. Terminating since we cannot disambiguate.'.format(len(selected_file_list)))
    elif len(selected_file_list) == 0:
        print('Failed to find file {} in folder {}. Terminating'.format(filename, folder))
    else:
        selected_gfile = selected_file_list[0]
        print('Found file {} in folder {}. Downloading'.format(filename, folder))
        g_drive.download(selected_gfile, output_filepath)
        print('Download complete')


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



