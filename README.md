[![Build Status](https://travis-ci.org/stewrutledge/gelfHandler.svg?branch=master)](https://travis-ci.org/stewrutledge/gelfHandler)
[![Coverage Status](https://coveralls.io/repos/github/stewrutledge/gelfHandler/badge.svg)](https://coveralls.io/github/stewrutledge/gelfHandler)
# GelfHandler

GelfHandler is a basic logging handler for sending to a graylog2 instance via UDP or TCP

## Basic usage

Install via pip:

`pip install gelfHandler`

```python
from gelfHandler import GelfHandler
import logging

logger = logging.getLogger()
gelfHandler = GelfHandler(
    host='mylogserver.example.com',
    port=12202,
    protocol='UDP'
)
logger.addHandler(gelfHandler)
logger.warning("Something went wrong")
```

There are four additional arguments:

`from_host='myhost'` which is the hostname field sent to graylog2 (default fqdn)

`facility='superlogger'` which is sent as the facility field in graylog2 (default is the loggers name)

`full_info=True` which sends the module the message came in, the pid of the process and the process name with the message

`tls=False` which enables TLS (`ssl_version=PROTOCOL_TLSv1, cert_reqs=CERT_NONE`) for TCP connections

The only protocols supports are UDP and TCP

To send additional fields to graylog2, use the keyword extra and send a dict starting with `{'gelfProps':`


```python
    logger.warn(
        'DANGER DANGER',
        extra={
            'gelf_props': {
                'name':'W. Robinsson',
                'planet':'Unkown'
            }
        }
    )
```

## Fallbacks

There are currently a number of things that need to be done:

* ~~Make the manner in which an extra dict is presented more deterministic, that is with a specific argument rather than taking over the whole argument argument.~~
* More error checking (for example make it clear that TCP and UDP are needed)
* ~~Compress TCP logging (currently only UDP is compressed using zlib)~~
* ~~Allow for an option to create full dumps from the message (essentially mapping the whole dictionary presented in a normal log message)~~


