class ClientData:
    def __init__(self, conn, ip_address,  port):
        self._conn = conn
        self._ip_address = ip_address
        self._port = port
        self.online_status = False
        self.file_list = []

    def to_dict(self):
        return {
            "ip_address": self._ip_address,
            "online_status": self.online_status,
        }


    @property
    def conn(self):
        return self._conn

    @property
    def ip_address(self):
        return self._ip_address


    @property
    def port(self):
        return self._port