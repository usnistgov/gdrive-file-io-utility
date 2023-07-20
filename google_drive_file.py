# NIST-developed software is provided by NIST as a public service. You may use, copy and distribute copies of the software in any medium, provided that you keep intact this entire notice. You may improve, modify and create derivative works of the software or any portion of the software, and you may copy and distribute such modifications or works. Modified works should carry a notice stating that you changed the software and should note the date and nature of any such change. Please explicitly acknowledge the National Institute of Standards and Technology as the source of the software.

# NIST-developed software is expressly provided "AS IS." NIST MAKES NO WARRANTY OF ANY KIND, EXPRESS, IMPLIED, IN FACT OR ARISING BY OPERATION OF LAW, INCLUDING, WITHOUT LIMITATION, THE IMPLIED WARRANTY OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, NON-INFRINGEMENT AND DATA ACCURACY. NIST NEITHER REPRESENTS NOR WARRANTS THAT THE OPERATION OF THE SOFTWARE WILL BE UNINTERRUPTED OR ERROR-FREE, OR THAT ANY DEFECTS WILL BE CORRECTED. NIST DOES NOT WARRANT OR MAKE ANY REPRESENTATIONS REGARDING THE USE OF THE SOFTWARE OR THE RESULTS THEREOF, INCLUDING BUT NOT LIMITED TO THE CORRECTNESS, ACCURACY, RELIABILITY, OR USEFULNESS OF THE SOFTWARE.

# You are solely responsible for determining the appropriateness of using and distributing the software and you assume all risks associated with its use, including but not limited to the risks and costs of program errors, compliance with applicable laws, damage to or loss of data, programs or equipment, and the unavailability or interruption of operation. This software is not intended to be used in any situation where a failure could cause risk of injury or damage to property. The software developed by NIST employees is not subject to copyright protection within the United States.

import json_io
import datetime


class GoogleDriveFile(object):
    def __init__(self, email: str, file_name: str, file_id: str, modified_timestamp: str, parents: str, mime_type: str):
        self.email = email
        self.name = file_name
        self.id = file_id
        self.modified_epoch = GoogleDriveFile.__convert_to_epoch(modified_timestamp)
        self.parents = parents
        self.mime_type = mime_type

    def __str__(self):
        msg = 'file id: "{}", name: "{}", modified_epoch: "{}", email: "{}", parents: "{}", mime_type: "{}"'.format(self.id, self.name, self.modified_epoch, self.email, self.parents, self.mime_type)
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
