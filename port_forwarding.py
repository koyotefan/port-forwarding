"""
Port Fowarding. by koyotefan@gmail.com ( jhchoi )

python port_forwarding.py [local listen port] [remote ip]:[remote port]
"""

import sys
import socket
import select
import threading

class Forwarding(threading.Thread):
    def __init__(self, _source_conn):
        threading.Thread.__init__(self)
        self.source_conn = _source_conn
        self.dest_conn = None

    def __del__(self):
        if self.source_conn:
            self.source_conn.close()
            self.source_conn = None

        if self.dest_conn:
            self.dest_conn.close()
            self.dest_conn = None

        print 'call __del__()'

    def init(self, _dest_ip, _dest_port):
        try:
            self.dest_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.dest_conn.connect((_dest_ip, _dest_port))
        except:
            return False

        return True

    def run(self):
        try:
            while True:
                i, _, _ = select.select([self.source_conn, self.dest_conn], [], [], 1)

                if self.source_conn in i:
                    data = self.source_conn.recv(1024)

                    if not data:
                        print 'disconnect by source_conn'
                        return
                    sendn = self.dest_conn.send(data)
                    print 'S->D| send [{0}]'.format(sendn)

                if self.dest_conn in i:
                    data = self.dest_conn.recv(1024)

                    if not data:
                        print 'disconnect by source_conn'
                        return

                    sendn = self.source_conn.send(data)
                    print 'S<-D| send [{0}]'.format(sendn)

        except:
            print "flow - except"
            return

class PortFowarding(object):
    def __init__(self, _source_port, _dest_ip, _dest_port):
        self.listen_port = int(_source_port)
        self.dest_ip = _dest_ip
        self.dest_port = int(_dest_port)

        self.sock = None


    def init(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(('', self.listen_port))
        self.sock.listen(5)

    def service(self):

        list_sockets = []
        while True:
            i, _, _ = select.select(list_sockets + [self.sock], [], [], 5)

            if self.sock in i:
                conn, addr = self.sock.accept()
                print 'ACCEPT {0}'.format(addr)

                f = Forwarding(conn)

                if not f.init(self.dest_ip, self.dest_port):
                    print 'Forwarding init() failed'
                    continue

                f.start()

            print 'in service...'

if __name__ == '__main__':

    if len(sys.argv) != 3:
        print 'Invaild argument'
        print 'ex) python port_forwarding.py [source] [dest]'
        print 'ex) python port_forwarding.py 13306 192.168.10.188:3306'
        sys.exit()

    source_port = sys.argv[1]
    dest_ip = sys.argv[2].split(':')[0]
    dest_port = sys.argv[2].split(':')[1]

    inst = PortFowarding(source_port, dest_ip, dest_port)

    inst.init()
    inst.service()
