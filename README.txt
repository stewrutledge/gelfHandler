===========
gelfHandler
===========

gelfHandler is a basic logging handler for sending to a graylog2 instance via UDP or TCP

Basic usage
===========

Usage is pretty much like any handler::


    gHandler = gelfHandler(host='mylogserver.example.com',port=12202,proto='UDP')
    logger.addHandler(gHandler)

Support for additional fields is available if you send an arg as a dict::

    logger.warn('DANGER DANGER',{'name':'W. Robinsson'})



