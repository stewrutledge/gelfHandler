===========
gelfHandler
===========

gelfHandler is a basic logging handler for sending to a graylog2 instance via UDP or TCP

Basic usage
===========

Usage is pretty much like any handler::

    from gelfHandler import GelfHandler
    gHandler = GelfHandler(
        host='mylogserver.example.com',
        port=12202,
        protocol='UDP'
    )
    logger.addHandler(gHandler)

Support for additional fields is available if you send a dict using the extra keyword that begins with gelfProps::

    logger.warn('DANGER DANGER',extra={'gelf_props':{'name':'W. Robinsson', 'planet':'unknown'}})

More info can be found on the github page.

