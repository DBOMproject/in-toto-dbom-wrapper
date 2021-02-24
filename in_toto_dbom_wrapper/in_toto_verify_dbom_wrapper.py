"""
 * Copyright 2020 Unisys Corporation
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 *
 * 
"""

#!/usr/bin/env python
"""
<Program Name>
  in_toto_verify_dbom_wrapper.py

<Author>
  Ryan Mathison <Ryan.Mathison2@unisys.com>

<Purpose>
  Provides a wrapper for command line interface for runlib.in_toto_verify
  that allows in-toto information to be read from a DBoM ledger.

<Return Codes>
  1 if an exception occurred
  0 if no exception occurred

"""

import sys
import argparse
import in_toto
import json
#parser = argparse.ArgumentParser(description='something')
#parser.add_argument('--my_env', help='my environment')
import subprocess
import os
import glob
from os import environ
# importing the requests library 
import requests 
import tempfile
import base64
from distutils.dir_util import copy_tree
import textwrap
import logging
from  in_toto_dbom_wrapper import dbom_helper

LOG = logging.getLogger("in_toto_run-wrapper")
OUT_HDLR = logging.StreamHandler(sys.stdout)
OUT_HDLR.setFormatter(logging.Formatter('%(asctime)s %(message)s'))
OUT_HDLR.setLevel(logging.INFO)
LOG.addHandler(OUT_HDLR)
LOG.setLevel(logging.INFO)

ASSET_ID = environ.get('ASSET_ID')
CHANNEL_ID = environ.get('CHANNEL_ID')
REPO_ID = environ.get('REPO_ID')
GATEWAY_ADDRESS = environ.get('GATEWAY_ADDRESS')

def main():
  child_parser = argparse.ArgumentParser(parents=[], add_help=True,
      epilog=textwrap.dedent('''\
         IMPORTANT:
            This command wraps the in-toto-run command
            See the help for in-toto-run below for required and optional paramaters
         '''))
  child_parser.add_argument("--assetID", type=str, required=False,
        metavar="<assetID>", help=(
        "ID of the asset that a link is being created for "))
  child_parser.add_argument("--channelID", type=str, required=False,
        metavar="<channelID>", help=(
        "ID of the channel the asset is stored on "))
  child_parser.add_argument("--repoID", type=str, required=False,
        metavar="<repoID>", help=(
        "ID of the DBoM repo the asset is stored in "))
  child_parser.add_argument("--gatewayAddress", type=str, required=False,
        metavar="<gatewayAddress>", help=(
        "The http address of the DBoM gateway "))
  child_parser.add_argument("--inTotoHelp", action="store_true", required=False,
        dest="in_toto_help", help=(
        "Returns help response for in-toto-run "))         
  parent_parser = argparse.ArgumentParser(parents=[], add_help=False)
  parent_parser.add_argument("-k", "--layout-keys", type=str, metavar="<path>",
      nargs="+")

  try:
    child_args, rest = child_parser.parse_known_args()
  except:
    print("\n-------------------- in-toto-verify help --------------------\n")
    os.system('in-toto-verify --help')
    sys.exit(1)
  asset_id = child_args.assetID if child_args.assetID is not None else ASSET_ID
  if asset_id is None:
    LOG.error("Missing AssetID")
    sys.exit(1)

  channel_id = child_args.channelID if child_args.channelID is not None else CHANNEL_ID
  if channel_id is None:
    LOG.error("Missing ChannelID")
    sys.exit(1)

  repo_id = child_args.repoID if child_args.repoID is not None else REPO_ID
  if repo_id is None:
    LOG.error("Missing RepoID")
    sys.exit(1)

  gateway_address = child_args.gatewayAddress if child_args.gatewayAddress is not None else GATEWAY_ADDRESS
  if gateway_address is None:
    LOG.error("Missing GatewayAddress")
    sys.exit(1)

  LOG.debug("childArgs")
  LOG.debug(child_args)
  LOG.debug(rest)
  rest_arg = ['in-toto-verify']
  rest_arg.extend(rest)
  sys.argv = rest_arg
  #subprocess.Popen(rest_arg).wait()

  args, rest = parent_parser.parse_known_args()

  #Read the dbom asset
  url = gateway_address + "/api/v1/repo/"+repo_id + "/chan/" + channel_id + "/asset/" + asset_id
  LOG.debug(url)
  res = requests.get(url=url)
  LOG.debug(res)
  if res.status_code != 200:
    LOG.error(res.json())
    sys.exit(1)
  asset = res.json()
  asset = dbom_helper.decodeDict(asset)
  LOG.debug(json.dumps(asset))

  #Validate asset has in-toto data
  if 'inToto' not in asset['assetMetadata'] : 
    LOG.error("Not in-toto data found for assetID " + asset_id)
    sys.exit(1)

  if 'links' not in asset['assetMetadata']['inToto'] : 
    LOG.error("No in-toto link data found for assetID " + asset_id)
    sys.exit(1)

  if 'layouts' not in asset['assetMetadata']['inToto'] : 
    LOG.error("No in-toto layout data found for assetID " + asset_id)
    sys.exit(1)

  #Open a temp directory to do the validation and write all the in-toto links, layouts, and public keys to the directory
  with tempfile.TemporaryDirectory() as directory:
    copy_tree("./", directory) 
    os.chdir(directory)
    #f = open("demofile3.txt", "w")
    LOG.debug('The created temporary directory is %s' % directory)
    for linkFile in asset['assetMetadata']['inToto']['links']:
      LOG.debug('---------- ' + linkFile + ' ----------' )
      #print(json.dumps(asset['assetMetadata']['inToto']['links'][linkFile]))
      f = open(linkFile, "w")
      f.write(json.dumps(asset['assetMetadata']['inToto']['links'][linkFile]))
      f.close()

    for layoutFile in asset['assetMetadata']['inToto']['layouts']:
      LOG.debug('---------- ' + layoutFile + ' ----------' )
      #print(json.dumps(asset['assetMetadata']['inToto']['layouts'][layoutFile]))
      f = open(layoutFile, "w")
      f.write(json.dumps(asset['assetMetadata']['inToto']['layouts'][layoutFile]))
      f.close()

    f = open("./"+args.layout_keys[0], "w")
    LOG.debug(asset['assetMetadata']['inToto']['ownerKey'])
    key_bytes = base64.standard_b64decode(asset['assetMetadata']['inToto']['ownerKey'])
    key = key_bytes.decode('utf-8')
    LOG.debug(key)
    f.write(key)
    f.close()

    #run in-toto-verify
    with subprocess.Popen(rest_arg, stdout=subprocess.PIPE) as proc:
      LOG.info("---------- Started in-toto-verify ----------")
      proc.wait()
      if proc.returncode != 0:
        LOG.error("---------- Failed in-toto-verify ----------")
        LOG.error(proc.returncode)
        sys.exit(1)
      LOG.info("---------- Success in-toto-verify ----------")

if __name__ == '__main__':
  main()
