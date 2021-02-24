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
  in_toto_run_dbom_wrapper.py

<Author>
  Ryan Mathison <Ryan.Mathison2@unisys.com>

<Purpose>
  Provides a wrapper for command line interface for runlib.in_toto_run
  that allows in-toto information to be stored in a DBoM ledger.

<Return Codes>
  1 if an exception occurred
  0 if no exception occurred

"""

import sys
import argparse
import json
#parser = argparse.ArgumentParser(description='something')
#parser.add_argument('--my_env', help='my environment')
import subprocess
import os
import glob
from os import environ
import requests 
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
  parent_parser.add_argument("-n", "--step-name", type=str, required=True,
      metavar="<name>")

  try:
    child_args, rest = child_parser.parse_known_args()
  except:
    print("\n-------------------- in-toto-run help --------------------\n")
    os.system('in-toto-run --help')
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

  LOG.debug("---------- childArgs ----------")
  LOG.debug(child_args)
  LOG.debug(rest)
  rest_arg = ['in-toto-run']
  rest_arg.extend(rest)
  sys.argv = rest_arg
  #subprocess.Popen(rest_arg).wait()

  with subprocess.Popen(rest_arg, stdout=subprocess.PIPE) as proc:
    LOG.info("---------- Started in-toto-run ----------")
    proc.wait()
    if proc.returncode != 0:
      LOG.error("---------- Failed in-toto-run ----------")
      LOG.error(proc.returncode)
      sys.exit(1)
    LOG.info("---------- Success in-toto-run ----------")
    #dir_path = os.getcwd()
    #f = []

    #print("---------- Matching Files ----------")
    #os.chdir(dir_path)
    #for file in glob.glob(args.step_name+".*"):
    #  print(file)

    args, rest = parent_parser.parse_known_args()

    list_of_files = glob.glob(args.step_name+".*") 
    latest_file = max(list_of_files, key=os.path.getctime)
    LOG.debug("---------- Latest File ----------")
    LOG.debug(latest_file)

    with open(latest_file) as json_file:
      data = json.load(json_file)
      LOG.debug(data)

      LOG.info("---------- Get asset ----------")
      url = gateway_address + "/api/v1/repo/"+repo_id + "/chan/" + channel_id + "/asset/" + asset_id
      LOG.debug(url)
      res = requests.get(url=url)
      LOG.debug(res)
      if res.status_code != 200:
        LOG.error(res.json())
        sys.exit(1)
      asset = res.json()
      LOG.debug(asset)

      if 'inToto' not in asset['assetMetadata']:
        asset['assetMetadata']['inToto'] = {}
      if 'links' not in asset['assetMetadata']['inToto']:
        asset['assetMetadata']['inToto']['links'] = {}
      asset = dbom_helper.decodeDict(asset)
      asset['assetMetadata']['inToto']['links'] [latest_file] = data
      LOG.debug("---------- Updated Metadata ----------")
      LOG.debug(json.dumps(asset))

      LOG.info("---------- Update asset ----------")
      res = requests.put(url = url, data = json.dumps(dbom_helper.encodeDict(asset))) 
      LOG.debug(res)
      if res.status_code != 200:
        LOG.error(res.json())
        sys.exit(1)
      response = res.json()
      LOG.debug(response)
      LOG.info("---------- Update complete ----------")

if __name__ == '__main__':
  main()
