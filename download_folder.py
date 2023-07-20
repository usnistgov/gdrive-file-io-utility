import os
import traceback

import drive_io
from drive_io import DriveIO
from google_drive_file import GoogleDriveFile


def download_all_children_of_folder(g_drive: drive_io.DriveIO, folder_name: str, output_filepath: str):
    """
    Return a dictionary of all the folder IDs in a drive mapped to their parent folder IDs (or to the
    drive itself if a top-level folder). That is, flatten the entire folder structure.
    """
    just_folders = "'trojai@nist.gov' in owners and trashed = false and mimeType = 'application/vnd.google-apps.folder'"
    results = g_drive.query_worker(just_folders)

    # find the id of the relevant folder
    folder_list = list()
    for folder in results:
        if folder.name == folder_name:
            folder_list.append({'gdrivefile': folder, 'parent_ofp': output_filepath})
    if len(folder_list) > 1:
        raise RuntimeError('More than one folder with the same name found')

    while len(folder_list) > 0:
        new_folder_list = list()
        for folder_dict in folder_list:
            folder = folder_dict['gdrivefile']
            parent_ofp = folder_dict['parent_ofp']
            cur_ofp = os.path.join(parent_ofp, folder.name)
            query = "'trojai@nist.gov' in owners and trashed = false and '{}' in parents".format(folder.id)
            files = g_drive.query_worker(query)
            for file in files:
                if file.mime_type == 'application/vnd.google-apps.folder':
                    new_folder_list.append({'gdrivefile': file, 'parent_ofp': cur_ofp})
                else:
                    print(os.path.join(cur_ofp, file.name))
                    if not os.path.exists(cur_ofp):
                        os.makedirs(cur_ofp)
                    g_drive.download(file, cur_ofp)
                    print("  Downloaded: {}".format(file.name))
        folder_list = new_folder_list





def download(token, folder, output_filepath):
    if not os.path.exists(output_filepath):
        os.makedirs(output_filepath)

    print('Instantiating Drive object')
    g_drive = DriveIO(token)

    download_all_children_of_folder(g_drive, folder, output_filepath)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Downloads a folders contents from the trojai google drive.')

    parser.add_argument('--token-pickle-filepath', type=str,
                        help='Path token.pickle file holding the oauth keys.',
                        default='token.pickle')
    parser.add_argument('--folder', type=str,
                        help='The folder to download from on drive',
                        default="My Drive")
    parser.add_argument('--output_dirpath', type=str,
                        help='The folder to download into on your local machine',
                        required=True)

    args = parser.parse_args()

    token = args.token_pickle_filepath
    folder = args.folder
    output_dirpath = args.output_dirpath
    print('Args: ')
    print('token = {}'.format(token))
    print('folder = {}'.format(folder))
    print('output_dirpath = {}'.format(output_dirpath))

    try_nb = 0
    max_nb_tries = 1
    done = False
    while not done and try_nb < max_nb_tries:
        try:
            try_nb = try_nb + 1
            download(token, folder, output_dirpath)
            done = True
        except Exception as e:
            traceback.print_exc()
            traceback.print_stack()
            print('failed, retrying')
            pass



