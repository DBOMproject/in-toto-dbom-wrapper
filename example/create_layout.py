from securesystemslib import interface
from in_toto.models.layout import Layout
from in_toto.models.metadata import Metablock
import os
from in_toto_dbom_wrapper.metadata_dbom_wrapper import DbomMetablock
assetID = os.getenv('ASSET_ID')

def main():
  # Load Alice's private key to later sign the layout
  key_alice = interface.import_rsa_privatekey_from_file("alice")
  # Fetch and load Bob's and Carl's public keys
  # to specify that they are authorized to perform certain step in the layout
  key_bob = interface.import_rsa_publickey_from_file("../functionary_bob/bob.pub")
  key_carl = interface.import_rsa_publickey_from_file("../functionary_carl/carl.pub")

  layout = Layout.read({
      "_type": "layout",
      "keys": {
          key_bob["keyid"]: key_bob,
          key_carl["keyid"]: key_carl,
      },
      "steps": [{
          "name": "clone",
          "expected_materials": [],
          "expected_products": [["CREATE", "demo-project/foo.py"], ["DISALLOW", "*"]],
          "pubkeys": [key_bob["keyid"]],
          "expected_command": [
              "git",
              "clone",
              "https://github.com/in-toto/demo-project.git"
          ],
          "threshold": 1,
        },{
          "name": "update-version",
          "expected_materials": [["MATCH", "demo-project/*", "WITH", "PRODUCTS",
                                "FROM", "clone"], ["DISALLOW", "*"]],
          "expected_products": [["ALLOW", "demo-project/foo.py"], ["DISALLOW", "*"]],
          "pubkeys": [key_bob["keyid"]],
          "expected_command": [],
          "threshold": 1,
        },{
          "name": "package",
          "expected_materials": [
            ["MATCH", "demo-project/*", "WITH", "PRODUCTS", "FROM",
             "update-version"], ["DISALLOW", "*"],
          ],
          "expected_products": [
              ["CREATE", "demo-project.tar.gz"], ["DISALLOW", "*"],
          ],
          "pubkeys": [key_carl["keyid"]],
          "expected_command": [
              "tar",
              "--exclude",
              ".git",
              "-zcvf",
              "demo-project.tar.gz",
              "demo-project",
          ],
          "threshold": 1,
        }],
      "inspect": [{
          "name": "untar",
          "expected_materials": [
              ["MATCH", "demo-project.tar.gz", "WITH", "PRODUCTS", "FROM", "package"],
              # FIXME: If the routine running inspections would gather the
              # materials/products to record from the rules we wouldn't have to
              # ALLOW other files that we aren't interested in.
              ["ALLOW", ".keep"],
              ["ALLOW", "alice.pub"],
              ["ALLOW", "root.layout"],
              ["DISALLOW", "*"]
          ],
          "expected_products": [
              ["MATCH", "demo-project/foo.py", "WITH", "PRODUCTS", "FROM", "update-version"],
              # FIXME: See expected_materials above
              ["ALLOW", "demo-project/.git/*"],
              ["ALLOW", "demo-project.tar.gz"],
              ["ALLOW", ".keep"],
              ["ALLOW", "alice.pub"],
              ["ALLOW", "root.layout"],
              ["DISALLOW", "*"]
          ],
          "run": [
              "tar",
              "xzf",
              "demo-project.tar.gz",
          ]
        }],
  })

  metadata = DbomMetablock(signed=layout)

  # Sign and dump layout to "root.layout"
  metadata.sign(key_alice)
  metadata.save_owner_key(key_alice, assetID)
  metadata.dump("root.layout")
  metadata.save_layout("root.layout", assetID)
  #print(metadata.__repr__)

if __name__ == '__main__':
  main()
