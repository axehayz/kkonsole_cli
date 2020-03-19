# kkonsole

kkonsole command-line project (docker + python based) for Kentik SE/CSE to perform common tasks.

## Installation

The project is meant to be installed locally and run as a lightweight python docker container(s)

1. Download and install [Docker](https://www.docker.com/products/docker-desktop). Skip if already installed and logged in.
2. Run Docker Container by issuing `docker run -it --rm axehayz:kkonsole_cli:latest`
3. (Optionally) Clone the repository and build container yourself if you wish to change source files
   1. Clone the repository `git clone https://github.com/axehayz/kkonsole_cli.git`
   2. Build the container using `docker build -t kkonsole_cli:myversion .`
   3. Run the container using `docker-compose run -it --rm kkonsole_cli:myversion`
4. On successful run, you will land on bash shell inside the container, ready for use.

## Usage

The project currently has two major command entrypoints

1. kkonsole (used to login and validate API creds)
2. kperform (used to perform CRUD tasks against Kentik v5 Admin API)

and,
3. klookup (used to query Redash over APIs. Not Implemented yet)

All the entrypoint commands and subcommands support `--help` functionality. Feel free to explore.

### kkonsole entrypoint

This is used for most basic tasks like using API credentials from environment file to maintain a persistant login for wherever you need to use the credentials, check for new API credentials, and find what credentials are currently in use.

```bash
bash-4.4# kkonsole --help
Usage: kkonsole [OPTIONS] COMMAND [ARGS]...

  kentik konsole utility for SEs/CSEs

Options:
  --help  Show this message and exit.

Commands:
  login   Use to login or test API Credentials with --prod flag
  whoami
```

Use `kkonsole login` to evaluate necessary credentials stored in kkonsole_env.env file.

```bash
bash-4.4# kkonsole login
Api token [mykey_from_env_file]:
Api email [myemail_from_env_file]:
[INFO]: Login successful.
[INFO]: Welcome Akshay Dhawale:[74354]

bash-4.4# kkonsole whoami
[INFO]: Currently logged in as Akshay Dhawale UID:74354 CID:49769

bash-4.4# kkonsole login --api-token mykey --api-email myemail
[INFO]: Login successful.
[INFO]: Welcome Akshay Dhawale:[74354]
```

Logs are stored in `/var/log/kkonsole.log`

---

### kperform entrypoint

kperform is used to create, update, delete kentik objects via Kentik v5 API. It is *required* to login before issuing kperform via `kkonsole login` command.

```bash
bash-4.4# kperform --help
Usage: kperform [OPTIONS] COMMAND [ARGS]...

  Use kperform to add/delete/update various kentik dimensions

Options:
  --help  Show this message and exit.

Commands:
  create  create group routines for POST API methods against kentik v5 api
  delete  delete group routines (not implemented yet)
  update  update group routines (not implemented yet)
```

Emperically, `kperform create` is used the most. Here is what it looks like.

```bash
bash-4.4# kperform create --help
Usage: kperform create [OPTIONS] COMMAND [ARGS]...

  create group routines for POST API methods against kentik v5 api

Options:
  -p, --prod / --no-prod  PROD credentials.
  --help                  Show this message and exit.

Commands:
  devices        create devices
  devices-sites  create devices and sites recursively (not implemented)
  populators     create populators
  sites          create sites
  users          create users
```

The `kperform create` subcommands for devices, sites, etc are self-explanatory. Each require the path to file which will be used as source_file to create the objects. Some subcommands will require other mandatory parameters. If the source_file does not contain some of the required parameters for the subcommand object in question, the program will prompt automatically or wont proceed.

```bash
bash-4.4# kkonsole whoami
[INFO]: Currently logged in as Akshay Dhawale UID:74354 CID:49769

bash-4.4# kperform create devices -f /path/does/not/resolve
Usage: kperform create devices [OPTIONS]
Try "kperform create devices --help" for help.
Error: Invalid value for "--file" / "-f": File "/path/does/not/resolve" does not exist.

bash-4.4# kperform create devices -f /kkonsole/docs/sample_createDevices.csv
```

`kperform create devices -f /kkonsole/docs/sample_createDevices.csv` will create 2 sample devices from the /kkonsole/docs/sample_createDevices.csv in the account which is logged in.

>Note:
>The source_file should be present inside the container. To use your custom .csv file as source_file, proceed to add/copy the file in the container.
>`docker cp /source_file/on/local/machine <container>:/path/inside/container/source_file`
>Find docker container using `docker container ls`

## Logs

Most of the functionality comes with extensive logging. Logs are present in `/var/log/*`.
Important logs come with a random (fugazy) number to lookup (read:grep) said transaction logs.

## Built with

* [Docker](https://www.docker.com/products/docker-desktop)
* [click/python](https://click.palletsprojects.com/en/7.x/)
* [requests/python](http://docs.python-requests.org/en/master/)

## Contribute

There is a [feature-wishlist](docs/feature_wishlist.txt) which contributers can help with.
Contribution guidelines will be provided soon for contributing on create/delete scripts under kperform.

## License

This project is licensed under the MIT License - see the LICENSE.md(LICENSE.md) for details.
