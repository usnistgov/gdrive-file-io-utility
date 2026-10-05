# NIST-developed software is provided by NIST as a public service. You may use, copy and distribute copies of the software in any medium, provided that you keep intact this entire notice. You may improve, modify and create derivative works of the software or any portion of the software, and you may copy and distribute such modifications or works. Modified works should carry a notice stating that you changed the software and should note the date and nature of any such change. Please explicitly acknowledge the National Institute of Standards and Technology as the source of the software.

# NIST-developed software is expressly provided "AS IS." NIST MAKES NO WARRANTY OF ANY KIND, EXPRESS, IMPLIED, IN FACT OR ARISING BY OPERATION OF LAW, INCLUDING, WITHOUT LIMITATION, THE IMPLIED WARRANTY OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, NON-INFRINGEMENT AND DATA ACCURACY. NIST NEITHER REPRESENTS NOR WARRANTS THAT THE OPERATION OF THE SOFTWARE WILL BE UNINTERRUPTED OR ERROR-FREE, OR THAT ANY DEFECTS WILL BE CORRECTED. NIST DOES NOT WARRANT OR MAKE ANY REPRESENTATIONS REGARDING THE USE OF THE SOFTWARE OR THE RESULTS THEREOF, INCLUDING BUT NOT LIMITED TO THE CORRECTNESS, ACCURACY, RELIABILITY, OR USEFULNESS OF THE SOFTWARE.

# You are solely responsible for determining the appropriateness of using and distributing the software and you assume all risks associated with its use, including but not limited to the risks and costs of program errors, compliance with applicable laws, damage to or loss of data, programs or equipment, and the unavailability or interruption of operation. This software is not intended to be used in any situation where a failure could cause risk of injury or damage to property. The software developed by NIST employees is not subject to copyright protection within the United States.


from google_auth_oauthlib.flow import InstalledAppFlow
from drive_io import DriveIO, write_private_file


def create_auth_token(credentials_filepath, token_filepath):
    flow = InstalledAppFlow.from_client_secrets_file(credentials_filepath, DriveIO.SCOPES)
    creds = flow.run_local_server(port=0)
    # Save the credentials for the next run as owner-only json
    write_private_file(token_filepath, creds.to_json())
    return creds


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Build token.json file for authenticating Google Drive API access.')

    parser.add_argument('--token-filepath', '--token-pickle-filepath', dest='token_filepath', type=str,
                        help='Path token.json file holding the oauth keys. token.json will be generated after opening a web-browser to have the user accept the app permissions',
                        default='token.json')
    parser.add_argument('--credentials-filepath',
                        type=str,
                        help='Path to the credentials.json file holding the Google Cloud Project with API access to trojai@nist.gov Google Drive.',
                        default='credentials.json')

    args = parser.parse_args()
    token = args.token_filepath
    credentials = args.credentials_filepath
    create_auth_token(credentials, token)