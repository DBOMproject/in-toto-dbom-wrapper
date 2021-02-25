"""
 * Copyright 2021 Unisys Corporation
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
  metadata_dbom_wrapper.py

<Author>
  Ryan Mathison <Ryan.Mathison2@unisys.com>

<Purpose>
  Provides a wrapper for in-toto metadata class
  that allows in-toto information to be stored in a DBoM ledger.

<Return Codes>
  1 if an exception occurred
  0 if no exception occurred

"""

from in_toto.models.metadata import Metablock
from os import environ
import sys
import requests 
import json
import base64
import logging
from  in_toto_dbom_wrapper import dbom_helper

LOG = logging.getLogger("in_toto_run-wrapper")
OUT_HDLR = logging.StreamHandler(sys.stdout)
OUT_HDLR.setFormatter(logging.Formatter('%(asctime)s %(message)s'))
OUT_HDLR.setLevel(logging.INFO)
LOG.addHandler(OUT_HDLR)
LOG.setLevel(logging.INFO)

class DbomMetablock(Metablock):
  """Extends the in-toto metablock to store layout and owner keys to a DBoM

    """
  def save_layout(self, path, asset_id, *args, **kwargs):
    LOG.info("DbomMetablock.save_layout")
    """Saves an in-toto layout to an asset's DBoM 

    Arguments:
      path: The path to write the file to.
      asset_id: DBoM asset id

    Key Arguments:
      channel_id: DBoM channel to access
      gateway_address: Address of the chainsource gateway  
      repo_id: DBoM repo to access    


    """

    channel_id = kwargs.get("channelID", environ.get('CHANNEL_ID'))
    repo_id = kwargs.get("repoID", environ.get('REPO_ID'))
    gateway_address = kwargs.get("gatewayAddress", environ.get('GATEWAY_ADDRESS'))
    LOG.debug(asset_id)
    if asset_id is None:
      LOG.error("Missing AssetID")
      sys.exit(1)
    LOG.debug(channel_id)
    if channel_id is None:
      LOG.error("Missing ChannelID")
      sys.exit(1)
    LOG.debug(repo_id)
    if repo_id is None:
      LOG.error("Missing RepoID")
      sys.exit(1)
    LOG.debug(gateway_address)
    if gateway_address is None:
      LOG.error("Missing GatewayAddress")
      sys.exit(1)
      
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
      asset['assetMetadata']['inToto'] =  {}
    if 'layouts' not in asset['assetMetadata']['inToto']: 
      asset['assetMetadata']['inToto']['layouts'] =  {}
    LOG.debug(json.loads("{}".format(self)))
    asset = dbom_helper.decodeDict(asset)
    asset['assetMetadata']['inToto']['layouts'][path] = json.loads("{}".format(self))
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
    LOG.info("---------- Updated asset ----------")

  def save_owner_key(self, key, asset_id, *args, **kwargs):
    """Saves an in-toto owner's key to an asset's DBoM 

    Arguments:
      key: The owner's key
      asset_id: DBoM asset id

    Key Arguments:
      channel_id: DBoM channel to access
      gateway_address: Address of the chainsource gateway  
      repo_id: DBoM repo to access    

    """
    LOG.info("DbomMetablock.save_owner_key")
    signature = Metablock.sign(self,key)
    write_dbom = kwargs.get("writeDBoM", False)

    channel_id = kwargs.get("channelID", environ.get('CHANNEL_ID'))
    repo_id = kwargs.get("repoID", environ.get('REPO_ID'))
    gateway_address = kwargs.get("gatewayAddress", environ.get('GATEWAY_ADDRESS'))
    LOG.debug(asset_id)
    if asset_id is None:
      LOG.error("Missing AssetID")
      sys.exit(1)
    LOG.debug(channel_id)
    if channel_id is None:
      LOG.error("Missing ChannelID")
      sys.exit(1)
    LOG.debug(repo_id)
    if repo_id is None:
      LOG.error("Missing RepoID")
      sys.exit(1)
    LOG.debug(gateway_address)
    if gateway_address is None:
      LOG.error("Missing GatewayAddress")
      sys.exit(1)
      
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
      asset['assetMetadata']['inToto'] =  {}
    key_bytes = base64.standard_b64encode(key['keyval']['public'].encode('utf-8'))
    asset = dbom_helper.decodeDict(asset)
    asset['assetMetadata']['inToto']['ownerKey'] = key_bytes.decode('utf-8')
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
    LOG.info("---------- Updated asset ----------")