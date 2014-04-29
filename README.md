
![Build Status] (https://secure.travis-ci.org/vmalloc/capnhook.png )


![Downloads] (https://pypip.in/d/capnhook/badge.png )

![Version] (https://pypip.in/v/capnhook/badge.png )

# Overview

`capnhook` is a library implementing a basic hook mechanism for implementing callbacks. It provides flexible configuration, hook namespaces and error handling strategies.

# Installation

```
$ pip install capnhook
```

# Usage

The simplest use case when we want to register a callback to be called later. We start by registering a callback through `capnhook.register`:

```python

>>> from __future__ import print_function
>>> import capnhook
>>> @capnhook.register('hook_name')
... def func():
...     print('Called')

```

Now we can call the hook:

```python

>>> capnhook.trigger('hook_name')
Called

```

For more advanced uses, please refer to [the documentation](http://capnhook.readthedocs.org ) 
										

# Licence

BSD3

