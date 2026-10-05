# NIST-developed software is provided by NIST as a public service. You may use, copy and distribute copies of the software in any medium, provided that you keep intact this entire notice. You may improve, modify and create derivative works of the software or any portion of the software, and you may copy and distribute such modifications or works. Modified works should carry a notice stating that you changed the software and should note the date and nature of any such change. Please explicitly acknowledge the National Institute of Standards and Technology as the source of the software.

# NIST-developed software is expressly provided "AS IS." NIST MAKES NO WARRANTY OF ANY KIND, EXPRESS, IMPLIED, IN FACT OR ARISING BY OPERATION OF LAW, INCLUDING, WITHOUT LIMITATION, THE IMPLIED WARRANTY OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, NON-INFRINGEMENT AND DATA ACCURACY. NIST NEITHER REPRESENTS NOR WARRANTS THAT THE OPERATION OF THE SOFTWARE WILL BE UNINTERRUPTED OR ERROR-FREE, OR THAT ANY DEFECTS WILL BE CORRECTED. NIST DOES NOT WARRANT OR MAKE ANY REPRESENTATIONS REGARDING THE USE OF THE SOFTWARE OR THE RESULTS THEREOF, INCLUDING BUT NOT LIMITED TO THE CORRECTNESS, ACCURACY, RELIABILITY, OR USEFULNESS OF THE SOFTWARE.

# You are solely responsible for determining the appropriateness of using and distributing the software and you assume all risks associated with its use, including but not limited to the risks and costs of program errors, compliance with applicable laws, damage to or loss of data, programs or equipment, and the unavailability or interruption of operation. This software is not intended to be used in any situation where a failure could cause risk of injury or damage to property. The software developed by NIST employees is not subject to copyright protection within the United States.

import os
import io
import hashlib
import random
import mimetypes
import time
import logging
from typing import List

import socket
socket.setdefaulttimeout(120)  # set timeout to 5 minutes (300s)

from google_drive_file import GoogleDriveFile

from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.http import MediaIoBaseDownload
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError

# Limit logging from Drive API
logging.getLogger('googleapiclient.discovery').setLevel(logging.WARNING)
logging.getLogger('google_auth_oauthlib.flow').setLevel(logging.WARNING)
logging.getLogger('google.auth.transport.requests').setLevel(logging.WARNING)
logging.getLogger('googleapiclient.http').setLevel(logging.WARNING)
logging.getLogger('googleapiclient.errors').setLevel(logging.WARNING)

FILE_FIELDS = "name, id, modifiedTime, owners, parents, mimeType, md5Checksum"


def escape_query_value(value: str) -> str:
    """
    Escape a value for use inside a single quoted string literal in a Drive search query.
    https://developers.google.com/drive/api/guides/search-files#query_string_examples
    """
    return str(value).replace('\\', '\\\\').replace("'", "\\'")


def safe_local_path(output_dirpath: str, name: str) -> str:
    """
    Join a Drive file/folder name onto a local directory, rejecting any name which could resolve outside that directory.
    """
    if name is None or name in ('', '.', '..') or '/' in name or '\\' in name or '\0' in name or os.path.basename(name) != name:
        raise ValueError('Refusing to use unsafe Drive file name "{}" as a local path.'.format(name))
    base = os.path.realpath(output_dirpath)
    dest = os.path.join(base, name)
    if os.path.commonpath([base, os.path.realpath(dest)]) != base:
        raise ValueError('Drive file name "{}" resolves outside of "{}".'.format(name, output_dirpath))
    return dest


def write_private_file(filepath: str, contents: str) -> None:
    """
    Write contents to filepath with owner only (0600) permissions, refusing to follow a symlink.
    """
    fd = os.open(filepath, os.O_WRONLY | os.O_CREAT | os.O_TRUNC | os.O_NOFOLLOW, 0o600)
    os.fchmod(fd, 0o600)
    with os.fdopen(fd, 'w') as fh:
        fh.write(contents)


def md5_of_file(filepath: str) -> str:
    md5 = hashlib.md5()
    with open(filepath, 'rb') as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b''):
            md5.update(chunk)
    return md5.hexdigest()


class DriveIO(object):
    # If modifying these scopes, delete the file token.json.
    SCOPES = ['https://www.googleapis.com/auth/drive']

    def __init__(self, token_filepath):
        self.token_filepath = token_filepath
        self.page_size = 100
        self.max_retry_count = 4
        self.__get_service(self.token_filepath)

    def __get_service(self, token_filepath):
        logging.debug('Starting connection to Google Drive.')
        creds = None
        try:
            # The token file stores the user's access and refresh tokens as json, and is
            # created by create_auth_token.py when the authorization flow completes.
            if os.path.exists(token_filepath):
                logging.debug('Found token file: {}'.format(token_filepath))
                creds = Credentials.from_authorized_user_file(token_filepath, DriveIO.SCOPES)
            logging.debug('Token credentials loaded')
            # If there are no (valid) credentials available, let the user log in.
            if not creds:
                logging.error('Credentials could not be loaded. Rebuild token using create_auth_token.py')
                raise RuntimeError('Credentials could not be loaded. Rebuild token using create_auth_token.py')

            # check if the credentials are not valid
            if not creds.valid:
                if creds.expired and creds.refresh_token:
                    logging.debug('Credentials exists, but are no longer valid, attempting to refresh.')
                    creds.refresh(Request())
                    logging.debug('Credentials refreshed successfully.')
                    # Save the credentials for the next run
                    write_private_file(token_filepath, creds.to_json())
                    logging.debug('Credentials refreshed and saved to "{}".'.format(token_filepath))
                else:
                    logging.error('Could not refresh credentials. Rebuild token using create_auth_token.py.')
                    raise RuntimeError('Could not refresh credentials. Rebuild token using create_auth_token.py.')

            logging.debug('Building Drive service from credentials.')
            self.service = build('drive', 'v3', credentials=creds, cache_discovery=False)
            # Turn off cache discover to prevent logging warnings
            # https://github.com/googleapis/google-api-python-client/issues/299

            logging.debug('Querying Drive to determine account owner details.')
            response = self.service.about().get(fields="user").execute(num_retries=self.max_retry_count)
            self.user_details = response.get('user')
            self.email_address = self.user_details.get('emailAddress')
            logging.info('Connected to Drive for user: "{}" with email "{}".'.format(self.user_details.get('displayName'), self.email_address))
        except:
            logging.error('Failed to connect to Drive.')
            raise

    def query_worker(self, query: str) -> List[GoogleDriveFile]:
        # make query_worker available outside the class
        return self.__query_worker(query)

    def __query_worker(self, query: str) -> List[GoogleDriveFile]:
        # https://developers.google.com/drive/api/v3/search-files
        # https://developers.google.com/drive/api/v3/reference/query-ref
        try:
            logging.debug('Querying Drive API with "{}".'.format(query))
            retry_count = 0
            while True:
                try:
                    # Call the Drive v3 API, blocking through pageSize records for each call
                    page_token = None
                    items = list()
                    while True:
                        # name, id, modifiedTime, sharingUser
                        response = self.service.files().list(q=query,
                                                             pageSize=self.page_size,
                                                             fields="nextPageToken, files({})".format(FILE_FIELDS),
                                                             pageToken=page_token,
                                                             spaces='drive').execute(num_retries=self.max_retry_count)
                        items.extend(response.get('files'))
                        page_token = response.get('nextPageToken', None)
                        if page_token is None:
                            break
                    break  # successfully download file list, break exponential backoff scheme loop
                except HttpError as e:
                    retry_count = retry_count + 1
                    if e.resp.status in [104, 404, 408, 410] and retry_count <= self.max_retry_count:
                        # Start the upload from the beginning.
                        logging.info('Drive Query Error, restarting query from beginning (attempt {}/{}) with exponential backoff.'.format(retry_count, self.max_retry_count))
                        sleep_time = random.random() * 2 ** retry_count
                        time.sleep(sleep_time)
                    else:
                        raise

            logging.debug('Downloaded list of {} files from Drive account.'.format(len(items)))
            file_list = list()
            for item in items:
                file_list.append(DriveIO.__to_drive_file(item))
        except:
            logging.error('Failed to connect to and list files from Drive.')
            raise

        return file_list

    @staticmethod
    def __to_drive_file(item: dict) -> GoogleDriveFile:
        owner = item['owners'][0]  # user first owner by default
        return GoogleDriveFile(owner['emailAddress'], item['name'], item['id'], item['modifiedTime'], item.get('parents', []), item['mimeType'], item.get('md5Checksum'))

    def get_by_id(self, file_id: str) -> GoogleDriveFile:
        item = self.service.files().get(fileId=file_id, fields=FILE_FIELDS).execute(num_retries=self.max_retry_count)
        return DriveIO.__to_drive_file(item)

    def query_by_filename(self, file_name: str, only_root_flag: bool = False) -> List[GoogleDriveFile]:
        file_name = escape_query_value(file_name)
        if only_root_flag:
            query = "name = '{}' and trashed = false and 'root' in parents".format(file_name)
        else:
            query = "name = '{}' and trashed = false".format(file_name)
        file_list = self.__query_worker(query)
        return file_list

    def query_by_email_and_filename(self, email: str, file_name: str, only_root_flag: bool = False) -> List[GoogleDriveFile]:
        email = escape_query_value(email)
        file_name = escape_query_value(file_name)
        if only_root_flag:
            query = "name = '{}' and '{}' in owners and trashed = false and 'root' in parents".format(file_name, email)
        else:
            query = "name = '{}' and '{}' in owners and trashed = false".format(file_name, email)
        file_list = self.__query_worker(query)
        return file_list

    def query_by_email(self, email: str, only_root_flag: bool = False) -> List[GoogleDriveFile]:
        email = escape_query_value(email)
        if only_root_flag:
            query = "'{}' in owners and trashed = false and 'root' in parents".format(email)
        else:
            query = "'{}' in owners and trashed = false".format(email)
        file_list = self.__query_worker(query)
        return file_list

    def download(self, g_file: GoogleDriveFile, output_dirpath: str) -> str:
        retry_count = 0
        logging.info('Downloading file: "{}" from Drive'.format(g_file))
        local_filepath = safe_local_path(output_dirpath, g_file.name)
        while True:
            try:
                request = self.service.files().get_media(fileId=g_file.id)
                with io.FileIO(local_filepath, 'wb') as file_data:
                    downloader = MediaIoBaseDownload(file_data, request)
                    done = False
                    while not done:
                        status, done = downloader.next_chunk(num_retries=self.max_retry_count)
                        logging.debug("  downloaded {:d}%".format(int(status.progress() * 100)))
                return local_filepath  # download completed successfully
            except HttpError as e:
                retry_count = retry_count + 1
                if e.resp.status in [104, 404, 408, 410] and retry_count <= self.max_retry_count:
                    # Start the upload from the beginning.
                    logging.info('Download Error, restarting download from beginning (attempt {}/{}) with exponential backoff.'.format(retry_count, self.max_retry_count))
                    sleep_time = random.random() * 2 ** retry_count
                    time.sleep(sleep_time)
                else:
                    raise
            except:
                logging.error('Failed to download file "{}" from Drive.'.format(g_file.name))
                raise

    def upload(self, file_path: str, only_root_flag=True) -> str:
        _, file_name = os.path.split(file_path)
        logging.info('Uploading file: "{}" to Drive'.format(file_name))
        m_type = mimetypes.guess_type(file_name)[0]

        # TODO ensure file_path is a file, and not a folder

        for retry_count in range(self.max_retry_count):
            try:
                existing_files_list = self.query_by_email_and_filename(self.email_address, file_name, only_root_flag=only_root_flag)

                existing_file_id = None
                if len(existing_files_list) > 0:
                    existing_file_id = existing_files_list[0].id

                file_metadata = {'name': file_name}
                media = MediaFileUpload(file_path, mimetype=m_type, resumable=True)

                if existing_file_id is not None:
                    logging.info("Updating existing file '{}' on Drive.".format(file_name))
                    request = self.service.files().update(fileId=existing_file_id, body=file_metadata, media_body=media)
                else:
                    logging.info("Uploading new file '{}' to Drive.".format(file_name))
                    request = self.service.files().create(body=file_metadata, media_body=media, fields='id')

                response = None
                # loop while there are additional chunks
                while response is None:
                    status, response = request.next_chunk(num_retries=self.max_retry_count)
                    if status:
                        logging.debug("  uploaded {:d}%".format(int(status.progress() * 100)))

                file = request.execute()
                return file.get('id')  # upload completed successfully

            except HttpError as e:
                if e.resp.status in [104, 404, 408, 410] and retry_count < self.max_retry_count - 1:
                    # Start the upload from the beginning.
                    logging.info('Upload Error, restarting upload from beginning (attempt {}/{}) with exponential backoff.'.format(retry_count, self.max_retry_count))
                    sleep_time = random.random() * 2 ** retry_count
                    time.sleep(sleep_time)
                else:
                    raise
            except:
                logging.error("Failed to upload file '{}' to Drive.".format(file_name))
                raise

    def share(self, file_id: str, share_email: str) -> None:
        if share_email is not None:
            # update the permissions to share the log file with the team, using short exponential backoff scheme
            user_permissions = {'type': 'user', 'role': 'reader', 'emailAddress': share_email}
            for retry_count in range(self.max_retry_count):
                try:
                    self.service.permissions().create(fileId=file_id, body=user_permissions, fields='id', sendNotificationEmail=False).execute()
                    logging.info('Successfully shared file {} with {}.'.format(file_id, share_email))
                    return  # permissions were successfully modified if no exception
                except Exception:
                    if retry_count < self.max_retry_count - 1:
                        logging.info('Failed to modify permissions on try, performing random exponential backoff.')
                        time.sleep(random.random() * 2 ** retry_count)
                    else:
                        logging.error("Failed to share uploaded file '{}' with '{}'.".format(file_id, share_email))
                        raise

    def remove_all_sharing_permissions(self, file_id: str) -> None:
        permissions = self.service.permissions().list(fileId=file_id).execute()
        permissions = permissions['permissions']

        for permission in permissions:
            if permission['role'] != 'owner':
                for retry_count in range(self.max_retry_count):
                    try:
                        self.service.permissions().delete(fileId=file_id, permissionId=permission['id']).execute()
                        logging.info("Successfully removed share permission '{}' from file {}.".format(permission, file_id))
                        break  # break retry loop
                    except Exception:
                        if retry_count < self.max_retry_count - 1:
                            logging.info('Failed to modify permissions on try, performing random exponential backoff.')
                            time.sleep(random.random() * 2 ** retry_count)
                        else:
                            logging.error("Failed to remove share permission '{}' from file '{}'.".format(permission, file_id))
                            raise

        # confirm that only the owner retains access before the file is re-shared
        remaining = self.service.permissions().list(fileId=file_id).execute()['permissions']
        remaining = [p for p in remaining if p['role'] != 'owner']
        if len(remaining) > 0:
            msg = "Failed to remove share permissions {} from file '{}'.".format(remaining, file_id)
            logging.error(msg)
            raise RuntimeError(msg)

    def upload_and_share(self, file_path: str, share_email: str) -> None:
        file_id = self.upload(file_path)
        if file_id is None:
            raise RuntimeError("Upload of '{}' did not return a file id.".format(file_path))
        # unshare to remove all permissions except for owner, to ensure that if the file is deleted on the receivers end, that they get a new copy of it.
        self.remove_all_sharing_permissions(file_id)
        self.share(file_id, share_email)

    def submission_download(self, email: str, output_dirpath: str, metadata_filepath: str, sts: bool) -> GoogleDriveFile:
        actor_file_list = self.query_by_email(email)

        # filter list based on file prefix
        gdrive_file_list = list()
        for g_file in actor_file_list:
            if sts and g_file.name.startswith('test'):
                gdrive_file_list.append(g_file)
            if not sts and not g_file.name.startswith('test'):
                gdrive_file_list.append(g_file)

        # ensure submission is unique (one and only one possible submission file from a team email)
        if len(gdrive_file_list) < 1:
            msg = "Actor does not have submission from email {}.".format(email)
            logging.error(msg)
            raise IOError(msg)
        if len(gdrive_file_list) > 1:
            msg = "Actor submitted {} file from email {}.".format(len(gdrive_file_list), email)
            logging.error(msg)
            raise IOError(msg)

        submission = gdrive_file_list[0]
        if submission.md5_checksum is None:
            msg = 'Submission "{}" from email {} has no md5Checksum; only binary (non Google Docs) files can be verified.'.format(submission.name, email)
            logging.error(msg)
            raise IOError(msg)

        logging.info('Downloading "{}" from Actor "{}" last modified time "{}".'.format(submission.name, submission.email, submission.modified_epoch))
        local_filepath = self.download(submission, output_dirpath)

        # verify the downloaded bytes are the ones described by the metadata, and that the file was not modified during the download
        current = self.get_by_id(submission.id)
        local_md5 = md5_of_file(local_filepath)
        if local_md5 != submission.md5_checksum or current.md5_checksum != submission.md5_checksum or current.modified_epoch != submission.modified_epoch:
            os.remove(local_filepath)
            msg = 'Submission "{}" from email {} was modified while being downloaded.'.format(submission.name, email)
            logging.error(msg)
            raise IOError(msg)

        submission.save_json(metadata_filepath)
        return submission


