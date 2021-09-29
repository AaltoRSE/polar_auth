import base64
import paramiko
import time
import os

from django.conf import settings
from polar_auth.settings import data_server, data_folder, data_server_key
from polar_auth.settings import rsa_key_file, ssh_username


# Set up an SSH client and add the data server key
try:
    server_key = paramiko.RSAKey(data=base64.decodebytes(data_server_key))
    ssh_client = paramiko.SSHClient()
    ssh_client.get_host_keys().add(data_server, 'ssh-rsa', server_key)
    rsa_key = paramiko.RSAKey.from_private_key_file(rsa_key_file)
except:
    from django.conf import settings
    if not settings.DEBUG:
        raise
    print("Can not load SSH keys.  Ignoring because this is debug mode.")


# Communicate the access token to the data server
def communicate_token(polar_id, access_token, subject_id):
    ''' Communicate a token to the data server over ssh. '''

    remote_file = data_folder + '/new_tokens'
    if data_server is not None:
        ssh_client.connect(
            hostname=data_server,
            username=ssh_username,
            pkey=rsa_key
        )
        sftp_client = ssh_client.open_sftp()
        token_file = sftp_client.file(remote_file, mode='a', bufsize=1)
        token_file.write(f'{access_token} {polar_id} {subject_id}\n')
        token_file.flush()
        token_file.close()

    else:
        # For debugging: read a local file in the data folder
        if not os.path.exists(data_folder):
            os.makedirs(data_folder)
        with open(remote_file, 'a') as token_file:
            token_file.write(f'{access_token} {polar_id} {subject_id}\n')


# Communicate the access token to the data server
def delete_token(subject_id):
    ''' Communicate a token to the data server over ssh. '''

    remote_file = data_folder + '/delete_tokens'
    if data_server is not None:
        ssh_client.connect(hostname=data_server, username=ssh_username, pkey=rsa_key)
        sftp_client = ssh_client.open_sftp()
        token_file = sftp_client.file(remote_file, mode='a', bufsize=1)
        token_file.write(f'{subject_id}\n')
        token_file.flush()
        token_file.close()
    else:
        # For debugging: write to a local file in the data folder
        if not os.path.exists(data_folder):
            os.makedirs(data_folder)
        with open(remote_file, 'a') as token_file:
            token_file.write(f'{subject_id}\n')


# Read the list of IDs with gathered date
previous_time = 0
ids = []


def get_ids_with_data():
    ''' Fetch the list of tokens with data over ssh. '''

    global previous_time
    global ids

    if settings.TESTING:
        # Rerun every time in debug mode
        previous_time = 0

    this_time = time.time()
    if this_time - previous_time > 60:
        remote_file = data_folder + '/ids_with_data'

        if data_server is not None:
            ssh_client.connect(hostname=data_server, username=ssh_username, pkey=rsa_key)
            sftp_client = ssh_client.open_sftp()
            try:
                id_file = sftp_client.file(remote_file, mode='r', bufsize=1)
                ids = []
                for line in id_file.readlines():
                    id, date = line.split(' ')
                    ids.append((int(id), date))
                id_file.close()
            except:
                # Assume unchanged if reading fails
                pass
        else:
            # Data server not set, assume local file
            try:
                with open(remote_file, 'r') as id_file:
                    ids = []
                    for line in id_file.readlines():
                        id, date = line.split(' ')
                        ids.append((int(id), date))
            except Exception as e:
                print(e)
                # Assume unchanged if reading fails
                pass

        previous_time = this_time

    return ids
