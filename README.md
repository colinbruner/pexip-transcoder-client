# Pexip Transcoder Client
A simple CLI library for manually configuring Pexip Transcoder Nodes in a cloud. The specific
use-case that this is intended for is in spinning up Pexip Transcoder nodes in AWS using Terraform 
outputs the inputs to the code.

Are there better ways to do this? Yes, [probably](https://docs.pexip.com/admin/smart_scale.htm). But this way also does work, and it was an opportunity
for me to mimic the layout of a piece of Python code that inspired me to work on this in the first place,
[httpie](https://github.com/httpie/httpie)

# Configuration
A `config.json` configuration file is searched for in order at the following places:
1. An absolute path specified within an environment variable `ENV_PEXIP_CONFIG_DIR`
2. A file local to where the script is being executed, e.g. `.pexip/config.json`
3. The running users home directory, e.g. `~/.pexip/config.json`

If no configuration file is found, all required arguments will be expected to be passed over the CLI.

## Example Config
The following is a simple example configuration file

```json
{
  "MANAGER_URL": "https://manager01.pexip.company.com",

  "DOMAIN": "company.com",
  "NETMASK": "255.255.255.0",
  "GATEWAY": "192.168.1.1",
  "TLS_CERTIFICATE_SUBJECT_NAME": "*.pexip.company.com",
  "SYSTEM_LOCATION_NAME": "pexip-production"
}
```
These values will be used as explicit defaults for all nodes created or deleted from the specified manager. 

Any values passed via CLI *will* override these values specified in the configuration.

# Usage
The following is a usage example for full node creation via CLI, without any local configuration file found.

```bash
$ pexip create --manager-url 'https://manager01.pexip.company.com' \
  --hostname "transcoder01.pexip.company.com" \
  --domain "company.com" \
  --gateway "192.168.1.1" \
  --private-ip "192.168.1.111" \
  --public-ip "52.41.93.113" \
  --tls-certificate-subject-name "*.pexip.company.com" \
  --system-location-name "pexip-production"
```

## Creating With Terraform
TODO
