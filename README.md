# Setup Drive API Access

Goto the Developer console
https://console.developers.google.com/

- Create a new project 'drive_io'

- Enable APIs - Enable Google Drive API

- Configure OAuth2 Screen

  Click on 'Credentials' in the LHS page menu.
  + Click on 'Configure Consent Screen'
  + Select 'Internal' for 'User Type' and click on 'Create'
  + Set the 'Application name' field to 'io_app'
  + Add the following scope: '../auth/drive'
  + Click on 'Save'

- Create Credentials (OAuth2)
  + Click on 'Credentials'
  + Click on 'Create Credentials'
  + Choose 'OAuth Client ID'
  + Choose 'Other' as 'Application type'
  + Set 'Name' to 'io_app'
  + Click on 'Save' or 'Create'

	Creates 'OAuth client' and gives 'Client ID' and 'Client Secret',
    which look like a public-private key pair.

  + Click OK

- Download credential, rename to credentials.json

- Copy credentials.json to folder containing drive_io.py

-------------------------------------------------------------------------------

# Setup Python for Google Drive Access

Based on https://developers.google.com/drive/api/v3/quickstart/python

python3 -m venv drive_io
source ./drive_io/bin/activate
pip install --upgrade pip
pip install --upgrade requirements.txt

-------------------------------------------------------------------------------

# Create and Downlaod OAuth Token

- Run the following command; make sure paths are *right*.

```
	python3 create_auth_token.py \
	--credentials-filepath credentials.json \
	--token-pickle-filepath token.pickle
```

-------------------------------------------------------------------------------

With your 'token.pickle' you can now use drive_io.py to connect to the linked Google Drive account; list, download, and upload files. 
