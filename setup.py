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
  setup.py

<Author>
  Ryan Mathison <Ryan.Mathison2@unisys.com>

<Copyright>
  See LICENSE for licensing information.

<Purpose>
  setup.py script to install the dbom in-toto-wrapper scripts

"""
import io
import os
import re

from setuptools import setup, find_packages

base_dir = os.path.dirname(os.path.abspath(__file__))

def get_version(filename="in_toto_dbom_wrapper/__init__.py"):
  with io.open(os.path.join(base_dir, filename), encoding="utf-8") as initfile:
    for line in initfile.readlines():
      m = re.match("__version__ *= *['\"](.*)['\"]", line)
      if m:
        return m.group(1)

with open("README.md") as f:
  long_description = f.read()

setup(
  name="in-toto-dbom-wrapper",
  author="Ryan Mathison",
  author_email="Ryan.Mathison2@unisys.com",
  description=("A wrapper for running in-toto commands and using dbom repositories as the storage medium for the in-toto attestations"),
  long_description_content_type="text/markdown",
  long_description=long_description,
  license="Apache-2.0",
  python_requires=">=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*, !=3.5.*, <4",
  packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests",
      "debian"]),
  install_requires=["in_toto","requests"],
  entry_points={
    "console_scripts": ["in-toto-run-dbom-wrapper = in_toto_dbom_wrapper.in_toto_run_dbom_wrapper:main",
                        "in-toto-record-dbom-wrapper = in_toto_dbom_wrapper.in_toto_record_dbom_wrapper:main",
                        "in-toto-verify-dbom-wrapper = in_toto_dbom_wrapper.in_toto_verify_dbom_wrapper:main"]
  },
  project_urls={
    "Source": "https://github.com/DBOMproject/in-toto-dbom-wrapper",
    "Bug Reports": "https://github.com/DBOMproject/in-toto-dbom-wrapper/issues",
  },
  version=get_version(),
)
