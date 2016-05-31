|                       |                                                                                         |
|-----------------------|-----------------------------------------------------------------------------------------|
| Build Status          | ![Build Status] (https://secure.travis-ci.org/getslash/gossip.png?branch=master,develop) |
| Supported Versions    | ![Supported Versions] (https://img.shields.io/pypi/pyversions/gossip.svg)               |
| Latest Version        | ![Latest Version] (https://img.shields.io/pypi/v/gossip.svg)                            |


# Overview

`gossip` is a library implementing a basic hook mechanism for implementing callbacks. It provides flexible configuration, hook namespaces and error handling strategies.

# Installation

```
$ pip install gossip
```

# Usage

The simplest use case when we want to register a callback to be called later. We start by registering a callback through `gossip.register`:

```python

>>> from __future__ import print_function
>>> import gossip
>>> @gossip.register('hook_name')
... def func():
...     print('Called')

```

Now we can call the hook:

```python

>>> gossip.trigger('hook_name')
Called

```

# And There's A Lot More!

Plain publish/subscribe is just the tip of the iceberg. Gossip is geared towards implementing complex plugin systems, and supports many more advanced features, such as:

1. Token (bulk) unregistration of hooks
2. Hook dependencies - control the order of hook callbacks, either implicitly or explicitly
3. Non-reentrant hooks
4. Custom exception handling strategies

And much more. For more information, please refer to [the documentation](http://gossip.readthedocs.org ) 
										

# Licence

BSD3

