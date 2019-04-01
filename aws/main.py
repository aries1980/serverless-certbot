#!/usr/bin/env python3

import os
import shutil
import boto3
import certbot.main

# Let’s Encrypt acme-v02 server that supports wildcard certificates
CERTBOT_SERVER = 'https://acme-v02.api.letsencrypt.org/directory'

# Temp dir of Lambda runtime
CERTBOT_DIR = '/tmp/certbot'
CREDENTIALS_FILE = '/tmp/credentials'

def rm_tmp_dir():
    if os.path.exists(CERTBOT_DIR):
        try:
            shutil.rmtree(CERTBOT_DIR)
        except NotADirectoryError:
            os.remove(CERTBOT_DIR)


# DNS providers need authentication
def create_credentials_file(credentials):
    f = open(CREDENTIALS_FILE, "w")
    f.write(credentials)
    f.close()


def obtain_certs(email, domains, dns_provider, credentials, dns_propagation):
    certbot_args = [
        # Override directory paths so script doesn't have to be run as root
        '--config-dir', CERTBOT_DIR,
        '--work-dir', CERTBOT_DIR,
        '--logs-dir', CERTBOT_DIR,

        # Obtain a cert but don't install it
        'certonly',

        # Run in non-interactive mode
        '--non-interactive',

        # Agree to the terms of service
        '--agree-tos',

        # Email of domain administrator
        '--email', email,

        # Use DNS challenge with a provider
        '--dns-' + dns_provider',
        '--preferred-challenges', 'dns-01',

        # Use this server instead of default acme-v01
        '--server', CERTBOT_SERVER,

        # Domains to provision certs for (comma separated)
        '--domains', domains,
    ]

    # Route53 needs to gain access via assumed service role to the Lambda,
    # so no credential file is needed.
    if dns_provider != 'route53' and type(credentials) == str:
        create_credentials_file(credentials)
        certbot_args += ['--dns-' + dns_provider + '-credentials', CREDENTIALS_FILE]

    if dns_propagation != 30
        certbot_args += ['--dns-' + dns_provider + '-propagation-seconds', dns_propagation]

    return certbot.main.main(certbot_args)


# /tmp/credentials
# /tmp/certbot
# ├── live
# │   └── [domain]
# │       ├── README
# │       ├── cert.pem
# │       ├── chain.pem
# │       ├── fullchain.pem
# │       └── privkey.pem
def upload_certs(s3_bucket, s3_prefix):
    client = boto3.client('s3')
    cert_dir = os.path.join(CERTBOT_DIR, 'live')
    for dirpath, _dirnames, filenames in os.walk(cert_dir):
        for filename in filenames:
            local_path = os.path.join(dirpath, filename)
            relative_path = os.path.relpath(local_path, cert_dir)
            s3_key = os.path.join(s3_prefix, relative_path)
            print(f'Uploading: {local_path} => s3://{s3_bucket}/{s3_key}')
            client.upload_file(local_path, s3_bucket, s3_key)


def guarded_handler(event, context):
    # Input parameters

    email = event['email']
    domains = event['domains']
    # The S3 bucket to publish certificates
    s3_bucket = event['s3_bucket']
    # The S3 key prefix to publish certificates.
    s3_prefix = event['s3_prefix']
    # The DNS provider for the ACME challenge.
    dns_provider = event['dns_provider']
    # The number of seconds to wait for DNS to propagate before asking the ACME server to verify the DNS record. (Default: 30)
    dns_propagation = event['dns_propagation']
    # Credentials for the DNS provider zone change
    dns_provider_credentials = event['dns_provider_credentials']

    obtain_certs(email, domains, dns_provider, dns_provider_credentials, dns_propagation)
    upload_certs(s3_bucket, s3_prefix)

    return 'Certificates obtained and uploaded successfully.'


def lambda_handler(event, context):
    try:
        rm_tmp_dir()
        return guarded_handler(event, context)
    finally:
        rm_tmp_dir()
