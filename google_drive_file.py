import json_io
import datetime


class GoogleDriveFile(object):
    def __init__(self, email: str, file_name: str, file_id: str, modified_timestamp: str):
        self.email = email
        self.name = file_name
        self.id = file_id
        self.modified_epoch = GoogleDriveFile.__convert_to_epoch(modified_timestamp)

    def __str__(self):
        msg = 'file id: "{}", name: "{}", modified_epoch: "{}", email: "{}" '.format(self.id, self.name, self.modified_epoch, self.email)
        return msg

    @staticmethod
    def __convert_to_epoch(time_str: str) -> int:
        """
        Convert an ISO time-date string into an epoch number.
        :param time_str: An iso time-date string
        :return int: unix epoch (seconds since Jan 1st 1970 (UTC))
        """
        time = datetime.datetime.strptime(time_str[:19], "%Y-%m-%dT%H:%M:%S")
        time = time.replace(tzinfo=datetime.timezone.utc)
        return int(time.timestamp())

    def save_json(self, file_path: str):
        json_io.write(file_path, self)

    @staticmethod
    def load_json(file_path: str):
        return json_io.read(file_path)
