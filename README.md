
![Build Status] (https://secure.travis-ci.org/vmalloc/gossip.png )


![Downloads] (https://pypip.in/d/gossip/badge.png )

![Version] (https://pypip.in/v/gossip/badge.png )

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

For more advanced uses, please refer to [the documentation](http://gossip.readthedocs.org ) 
										

# Licence

BSD3

