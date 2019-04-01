#!/usr/bin/env bash
# vim: et sr sw=2 ts=2 smartindent:

set -xe

##
# Sets up the environment, sets constants and variables.
##
setenv() {
  AWS_PYTHON_VERSION="${AWS_PYTHON_VERSION:-"3.7"}"
  CERTBOT_VERSION="${CERTBOT_VERSION:-"0.32.0"}"
  WORKSPACE="${TRAVIS_BUILD_DIR:-$(pwd)}"

  [ ! -d .python_cache ] && mkdir .python_cache
  [ ! -d .build_artifacts ] && mkdir .build_artifacts
  
  return 0
}

##
# Downloads a given version of Certbot with the DNS plugins
##
build_for_aws() {
  local certbot_filename="certbot-awslambda-${1}.zip"
  local certbot_version=$1
  local aws_python_version=$2

  docker run \
    --rm \
    -v ${WORKSPACE}/.python_cache:/root/.cache/pip \
    -v ${WORKSPACE}:/workspace \
    -w /workspace \
    python:${aws_python_version}-slim \
      bash -c -e -x " \
        chown -R root /root/.cache && \
        pip install virtualenv && \
        virtualenv venv && \
        source venv/bin/activate && \
        pip install \
          certbot==${certbot_version} \
          certbot-dns-cloudflare==${certbot_version} \
          certbot-dns-cloudxns==${certbot_version} \
          certbot-dns-digitalocean==${certbot_version} \
          certbot-dns-dnsimple==${certbot_version} \
          certbot-dns-dnsmadeeasy==${certbot_version} \
          certbot-dns-google==${certbot_version} \
          certbot-dns-linode==${certbot_version} \
          certbot-dns-luadns==${certbot_version} \
          certbot-dns-nsone==${certbot_version} \
          certbot-dns-ovh==${certbot_version} \
          certbot-dns-rfc2136==${certbot_version} \
          certbot-dns-route53==${certbot_version}
      "

  sudo chown -R $UID venv
  cd venv/lib/python${aws_python_version}/site-packages
  cp ${WORKSPACE}/aws/main.py .
  zip -q -r -9 $WORKSPACE/.build_artifacts/${certbot_filename} .
}

##
# Removes intermediary build artifacts.
##
cleanup() {
  rm -rf venv
}

##
# Run this function to run the build.
##
run() {
  setenv
  build_for_aws ${CERTBOT_VERSION} ${AWS_PYTHON_VERSION}
  cleanup
}

