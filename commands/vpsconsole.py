import gevent
import sys
from gevent.event import Event

from wssh.client import StdioPipedWebSocketClient
from wssh.common import StdioPipedWebSocketHelper

from ws4py.exc import HandshakeError
from ws4py.client.geventclient import WebSocketClient

from utils import hook, HookFlags, JsonResponse
from libs import centarra, substitutes, sub
from utils.domain import is_valid_host

class VPSArgsObject:
    def __init__(self):
        self.text_mode = 'auto'
        self.verbosity = 0
        self.new_lines = False
        self.quit_on_eof = True

class VPSConsoleIOHelper(StdioPipedWebSocketHelper):
    """
    The C library's stdio module on OS X 10.9 is finnicky.  So we patch things a little bit.
    Specifically, we tolerate that flush may fail, even though this is not posixly-compliant.
    """

    def __init__(self, shutdown_cond, opts):
        StdioPipedWebSocketHelper.__init__(self, shutdown_cond, opts)

    def received_message(self, websocket, m):
        chunk_size = 16
        to_write = len(m.data)
        while to_write > 0:
            try:
                sys.stdout.write(m.data[0:chunk_size])
                m.data = m.data[chunk_size:]
                to_write -= chunk_size
            except IOError:
                continue
            flushed = False
            while not flushed:
                try:
                    sys.stdout.flush()
                    flushed = True
                except IOError:
                    flushed = False

class VPSConsoleClient(StdioPipedWebSocketClient):
    def __init__(self, uri):
        WebSocketClient.__init__(self, uri)

        self.shutdown_cond = Event()
        self.opts = VPSArgsObject()
        self.iohelper = VPSConsoleIOHelper(self.shutdown_cond, self.opts)

@hook.command('vps console', args_amt=1, flags=None, doc=("Connect to the VPS console."))
def vps_console(args, flags):
    reply = centarra('/vps/%s' % args[0])
    service = reply['service']
    if not service:
        return 'Cannot find WSS-API endpoint'
    client = VPSConsoleClient(service['wss_console_uri'])
    print('[Console attached, press ^D to exit.]')
    try:
        client.connect_and_wait()
    except (IOError, HandshakeError), e:
        print >> sys.stderr, e
    return '[Console detached.]'
