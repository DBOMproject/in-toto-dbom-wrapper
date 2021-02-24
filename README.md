# in-toto-dbom-wrapper

in-toto-dbom-wrapper is a package that wraps the in-toto package so that the in-toto layouts and links are able to be stored in and retrieved from a Digital Bill of Materials (DBoM)

## Getting Started
### Installation

installed via [`pip`](https://pypi.org/project/pip/). See

#### python 2.7
```shell
pip install ./
```

#### python 3 >= 3.6
```shell
python3 -m pip install ./
```
### Environmental variables

| Name            | Description                        |
|-----------------|------------------------------------|
| CHANNEL_ID      | DBoM channel to access             |
| GATEWAY_ADDRESS | Address of the chainsource gateway |
| REPO_ID         | DBoM repo to access                |
| ASSET_ID        | DBoM asset to access               |

### Available Command

| Name                        |
|-----------------------------|
| in-toto-record-dbom-wrapper |
| in-toto-run-dbom-wrapper    |
| in-toto-verify-dbom-wrapper |

#### Command Options

| Name             | Description                        |
|------------------|------------------------------------|
| --assetID        | DBoM asset id                      |
| --channelID      | DBoM channel to access             |
| --gatewayAddress | Address of the chainsource gateway |
| --inTotoHelp     | Get the in-toto help               |
| --repoID         | DBoM repo to access                |

### Available Libraries

##### metadata-wrapper 

###### save_layout

| Name            | Required | Description                        |
|-----------------|----------|------------------------------------|
| asset_id        | true     | DBoM asset id                      |
| channel_id      | false    | DBoM channel to access             |
| gateway_address | false    | Address of the chainsource gateway |
| path            | true     | name of the layout                 |
| repo_id         | false    | DBoM repo to access                |

###### save_owner_key

| Name            | Required | Description                        |
|-----------------|----------|------------------------------------|
| asset_id        | true     | DBoM asset id                      |
| channel_id      | false    | DBoM channel to access             |
| gateway_address | false    | Address of the chainsource gateway |
| key             | true     | owner's key                        |
| repo_id         | false    | DBoM repo to access                |

### See the [into-toto docs](https://github.com/in-toto/docs/blob/master/in-toto-spec.md) for more information about in-toto
## Next Steps

To learn more about the wrapper, see this [example](example/README.md) which will walk through how the wrapper works
## Getting Help

If you have any queries on in-toto-dbom-wrapper, feel free to reach us on any of our [communication channels](https://github.com/DBOMproject/community/blob/master/COMMUNICATION.md) 

If you have questions, concerns, bug reports, etc, please file an issue in this repository's [issue tracker](https://github.com/DBOMproject/in-toto-dbom-wrapper/issues).

## Getting Involved

Find the instructions on how you can contribute in [CONTRIBUTING](CONTRIBUTING.md).