[![Build Status](https://travis-ci.org/aries1980/serverless-certbot.svg?branch=master)](https://travis-ci.org/aries1980/serverless-certbot)

## The Problem

> Run Certbot on the first of every month and upload the certificates to a cloud storage.

SSL/TLS certificates is a must for any external communication. Not just because the served traffic is a secret, but also
to hide the endpoint that is serving. Also it is a must for SEO, HTTP/2, but it is a good practice in general.

Company-provided TLS certificates are expensive, thank God we have the free [Let's Encrypt](https://letsencrypt.org)
and [Certbot](https://certbot.eff.org)!  Because the letsencrypted TLS certificates have to be renewed in every 90
days the least.  So let's say, this task should run monthly.  Because it is written in Python, it would make sense to
run it as a serverless application.  Unfortunately Certbot saves the certificates on a local storage, so an extra code
needs to bundled to handle the serverless requests and


## The Solution

- Have a code that glues the serverless event and Certbot. Luckly there is a [code snippet for AWS Lambda](https://github.com/rog2/certbot-lambda/blob/master/main.py)
what I borrowed.  Cheers, mate!

The process is inspired by [Deploying EFF's Certbot in AWS Lambda](https://arkadiyt.com/2018/01/26/deploying-effs-certbot-in-aws-lambda/).

- Create a build pipeline
  - Installs a given version of Certbot into a Python virtual environment.
  - Adds the snippet
  - Zips it up
  - Provide a release artifact on Github.

## Usage

- Copy the certbot-lambda-[certbot_version].zip into AWS S3.  (More cloud provider support is planned.  Feel free to create a PR!)
- Terraform the serverless application.
