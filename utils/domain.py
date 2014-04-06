#!/usr/bin/env python
"""
Copyright (c) 2012, 2013, 2014 Centarra Networks, Inc.

Permission to use, copy, modify, and/or distribute this software for any
purpose with or without fee is hereby granted, provided that the above
copyright notice, this permission notice and all necessary source code
to recompile the software are included or otherwise available in all
distributions.

This software is provided 'as is' and without any warranty, express or
implied.  In no event shall the authors be liable for any damages arising
from the use of this software.
"""

def is_valid_host(host):
    '''IDN compatible domain validator'''
    if '.arpa' in host:
        return True
    try:
        host = host.encode('idna').lower()
    except:
        return False
    if not hasattr(is_valid_host, '_re'):
        import re
        is_valid_host._re = re.compile(r'^([0-9a-z_]([-\w]*[0-9a-z_]|)\.)+[a-z0-9\-_]{1,15}$')
    checkhost = host
    if host[0] == '*':
        checkhost = host[2:]
    return bool(is_valid_host._re.match(checkhost))