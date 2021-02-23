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
  dbom_helper.py

<Author>
  Ryan Mathison <Ryan.Mathison2@unisys.com>

<Purpose>
  Provides helper functions for writing to the DBoM ledger

<Return Codes>
  1 if an exception occurred
  0 if no exception occurred

"""

#Encode and decodes dictionaries so that the data will properly store in mongodb
def encodeKey(key):
    return key.replace("\\", "\\\\").replace("\$", "\\u0024").replace(".", "\\u002e")


def decodeKey(key):
    return key.replace("\\u002e", ".").replace("\\u0024", "\$").replace("\\\\", "\\")

def encodeDict(dict1):
    dict2 = {}
    for key in dict1.keys():
        if isinstance(dict1[key], dict):
            dict2[encodeKey(key)] = encodeDict(dict1[key])
        else:
            dict2[encodeKey(key)] = dict1[key]
    return dict2

def decodeDict(dict1):
    dict2 = {}
    for key in dict1.keys():
        if isinstance(dict1[key], dict):
            dict2[decodeKey(key)] = decodeDict(dict1[key])
        else:
            dict2[decodeKey(key)] = dict1[key]
    return dict2
