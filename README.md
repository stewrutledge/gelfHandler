# gelfHandler

gelfHandler is a basic logging handler for sending to a graylog2 instance via UDP or TCP

## Basic usage

```python
gHandler = gelfHandler(host='mylogserver.example.com',port=12202,proto='UDP')
logger.addHandler(gHandler)
```

The only protocols supports are UDP and TCP

Support for additional fields is available if you send an arg as a dict:

```python
    logger.warn('DANGER DANGER',{'name':'W. Robinsson'})
```

## Fallbacks

There are currently a number of things that need to be done:

* Make the manner in which an extra dict is presented more deterministic, that is with a specific argument rather than taking over the whole argument argument.
* More error checking (for example make it clear that TCP and UDP are needed)
* Compress TCP logging (currently only UDP is compressed using zlib)
* Allow for an option to create full dumps from the message (essentially mapping the whole dictionary presented in a normal log message)


