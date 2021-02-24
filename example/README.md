# in-toto-dbom-wrapper example

This example modifies the [in-toto demo](https://github.com/in-toto/demo/blob/master/README.md) 
to show how easy it is to store in-toto attestations in DBoM repositories using the
in-toto-dbom-wrapper.

## Prerequisites and setup

- 2 or more machines/VMs

    - If you don't have access to a second machine, use a second terminal running in a different directory to simulate the second device

- Machine 1

    - Stand up a DBoM node using the [getting stated insturctions](https://dbom-project.readthedocs.io/en/latest/getting-started.html)

    - Clone the in-toto demo repository

        ```
        git clone https://github.com/in-toto/demo.git
        ```
- Machine 1 and 2

    - Install the in-toto-dbom-wrapper using the following [instruction](https://github.com/DBOMproject/in-toto-dbom-wrapper#installation)

## Running the example

### Machine 1

Start the terminal in the in-toto demo repository

#### Step 1

Set your environmental variables

```
export GATEWAY_ADDRESS=http://localhost:3000
export REPO_ID=DB1
export CHANNEL_ID=IN-TOTO-EXAMPLE
export ASSET_ID=EXAMPLE-ASSET
```

#### Step 2

Create the dbom asset

```
curl -f --location --request POST "$GATEWAY_ADDRESS/api/v1/repo/$REPO_ID/chan/$CHANNEL_ID/asset/$ASSET_ID" \
--header 'Content-Type: application/json' \
--data-raw '{
    "standardVersion": 1.0,
    "documentName": "Test Asset 01",
    "documentCreator": "DBoM Organisation",
    "documentCreatedDate": "2020-10-01T10:06:47+0000",
    "assetType": "HardwareComponent",
    "assetSubType": "SubType1",
    "assetManufacturer": "DBoM Organisation",
    "assetModelNumber": "ABCXYZ",
    "assetDescription": "A DBoM Asset",
    "assetMetadata": {
        "aKey": "aValue"
    },
    "manufactureSignature": "UNSIGNED(TEST)"
}'
```

#### Step 3

Update create_layout.py in owner_alice so that it uses the DBoM Metablock wrapper.  
The wrapper extends the in-toto Metablock module with two new functions so that the layout file and
owner public key can be stored to a dbom.

```
    cd owner_alice
```

Add the dbom metablock wrapper and also read the asset id

```
    import os
    from in_toto_dbom_wrapper.metadata_dbom_wrapper import DbomMetablock
    assetID = os.getenv('ASSET_ID')
```

Use the dbom metadata wrapper

- Before
    ```
        metadata = Metablock(signed=layout)
        # Sign and dump layout to "root.layout"
        metadata.sign(key_alice)
        metadata.dump("root.layout")
    ```

- After
    ```
        metadata = DbomMetablock(signed=layout)
        # Sign and dump layout to "root.layout"
        metadata.sign(key_alice)
        metadata.save_owner_key(key_alice, assetID)
        metadata.dump("root.layout")
        metadata.save_layout("root.layout", assetID)
    ```

See [create_layout.py](create_layout.py) for the final product

#### Step 4

Create the in-toto layout and confirm the update in the dbom

```
    python3 create_layout.py
```

Get the DBoM

```
curl -f --location --request GET "$GATEWAY_ADDRESS/api/v1/repo/$REPO_ID/chan/$CHANNEL_ID/asset/$ASSET_ID" \
--header 'Content-Type: application/json' 
```

In the assetMetadata section of the response, there is now an inToto section that includes the layout file that created.

```
"assetMetadata": {
		"aKey": "aValue",
		"inToto": {
			"layouts": {
				"root\\u002elayout": {
					"signatures": [
                        .
                        .
                        .
```

#### Step 5

Create the in-toto links and confirm the update in the dbom

```
cd ../functionary_bob
in-toto-run-dbom-wrapper --step-name clone --products demo-project/foo.py --key bob -- git clone https://github.com/in-toto/demo-project.git
in-toto-record-dbom-wrapper start --step-name update-version --key bob --materials demo-project/foo.py
cat <<EOF > demo-project/foo.py
VERSION = "foo-v1"
EOF
in-toto-record-dbom-wrapper stop --step-name update-version --key bob --products  demo-project/foo.py
cp -r demo-project ../functionary_carl/
cd ../functionary_carl
in-toto-run-dbom-wrapper --step-name package  --products demo-project.tar.gz --key carl -- tar --exclude ".git" -zcvf demo-project.tar.gz demo-project
cd ..
cp functionary_carl/demo-project.tar.gz final_product/
```

Get the DBoM

```
curl -f --location --request GET "$GATEWAY_ADDRESS/api/v1/repo/$REPO_ID/chan/$CHANNEL_ID/asset/$ASSET_ID" \
--header 'Content-Type: application/json' 
```

In the assetMetadata section of the response, there is now a links section in the in-toto metadata that has all the links created
```
"assetMetadata": {
		"aKey": "aValue",
		"inToto": {
			"layouts": 
                    .
                    .
                    .
            "links": {
				"clone\\u002e776a00e2\\u002elink": {
                    .
                    .
                    .
                "package\\u002e2f89b927\\u002elink": {
                    .
                    .
                    .
                "update-version\\u002e776a00e2\\u002elink": {
					"signatures": [
						{
                    .
                    .
                    .
```

### Machine 2

#### Step 6

Set your environmental variables

```
export GATEWAY_ADDRESS=http://machine1Address:3000
export REPO_ID=DB1
export CHANNEL_ID=IN-TOTO-EXAMPLE
export ASSET_ID=EXAMPLE-ASSET
```

#### Step 7

Create an empty directory and transfer the final product, demo-project.tar.gz, to the new directory

#### Step 8

Verify the final product. Rather than requiring the layout and link files, the wrapper pulls all of the in-toto attestations from the dbom

```
in-toto-verify-dbom-wrapper --layout root.layout --layout-key alice.pub
```
This will return that the verification was successful

```
2021-02-24 15:52:03,814 ---------- Started in-toto-verify ----------
2021-02-24 15:52:04,124 ---------- Success in-toto-verify ----------
```

#### Step 9

Repackage the final product and see the failure message

```
tar -xvzf demo-project.tar.gz
rm demo-project.tar.gz
tar --exclude ".git" -zcvf demo-project.tar.gz demo-project
rm -rf demo-project
```

```
2021-02-24 15:59:21,484 ---------- Started in-toto-verify ----------
(in-toto-verify) RuleVerificationError: 'DISALLOW *' matched the following artifacts: ['demo-project.tar.gz']
Full trace for 'expected_materials' of item 'untar':
Available materials (used for queue):
['.keep', 'alice.pub', 'demo-project.tar.gz', 'root.layout']
Available products:
['.keep', 'alice.pub', 'demo-project.tar.gz', 'root.layout', 'demo-project/foo.py']
Queue after 'MATCH demo-project.tar.gz WITH PRODUCTS FROM package':
['demo-project.tar.gz', 'alice.pub', '.keep', 'root.layout']
Queue after 'ALLOW .keep':
['demo-project.tar.gz', 'alice.pub', 'root.layout']
Queue after 'ALLOW alice.pub':
['demo-project.tar.gz', 'root.layout']
Queue after 'ALLOW root.layout':
['demo-project.tar.gz']

2021-02-24 15:59:21,789 ---------- Failed in-toto-verify ----------
2021-02-24 15:59:21,790 1
```

## In Review

This example showed how easy it was modify the in-toto demo with the in-toto-dbom-wrapper so that all of the
in-toto attestations were stored and retrieved from a dbom asset. By using dbom for storage of the in-toto 
attestations, the attestations are now stored in a common locations there they can easily be shared with the
client by using a secure dbom channel.  DBoM also allows the use of multiple storage back ends including DLTs
and transparency logs which ensures that the attestations have not been tampered with.

## Getting Help

If you have any queries on in-toto-dbom-wrapper, feel free to reach us on any of our [communication channels](https://github.com/DBOMproject/community/blob/master/COMMUNICATION.md) 

If you have questions, concerns, bug reports, etc, please file an issue in this repository's [issue tracker](https://github.com/DBOMproject/in-toto-dbom-wrapper/issues).
