import datetime
import binascii
import uuid
import hashlib
import json


def _serialize_header(properties):
    header = ['{key}="{value}"'.format(key=k, value=v) for k, v in properties.items()]
    return ', '.join(header)


def build_headers(password, username):
        nonce = str(uuid.uuid4())
        base64nonce = binascii.b2a_base64(binascii.a2b_qp(nonce))
        created_date = datetime.datetime.utcnow().isoformat() + 'Z'
        sha = nonce + created_date + password
        sha_object = hashlib.sha1(sha.encode())
        password_64 = binascii.b2a_base64(sha_object.digest())
        
        properties = {
            "Username": username,
            "PasswordDigest": password_64.decode().strip(),
            "Nonce": base64nonce.decode().strip(),
            "Created": created_date
        }
        header = 'UsernameToken ' + _serialize_header(properties)
        return {'X-WSSE': header}