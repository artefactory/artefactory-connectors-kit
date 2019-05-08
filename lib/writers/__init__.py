import os
from config import config


secret_path = config.get("SECRETS_PATH")
google_credentials_file = config.get("GOOGLE_APPLICATION_CREDENTIALS")
google_credentials = os.path.join(secret_path, google_credentials_file)
