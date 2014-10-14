import json
import requests

class RegisterException(Exception):
    pass

class LockException(Exception):
    pass

class UnlockException(Exception):
    pass

class ListException(Exception):
    pass



class LockRPC(object):
    headers = {'content-type': 'application/json'}

    def __init__(self, server, base_url="json/", register_url="register/",
            username=None, password=None):
        self.server = server
        self.base_url = base_url
        self.register_url = register_url
        self.username = username
        self.password = password

    def call(self, request, *data):
        payload = {
            "method": request,
            "params": list(data),
            "jsonrpc": "2.0",
            "id": 0,
        }
        r = requests.post("%s/%s" % (self.server, self.base_url),
            data=json.dumps(payload),
            headers=self.headers)
        return r

    def register(self):
        r = requests.get('%s/%s' % (self.server, self.register_url))
        if r.status_code == 400:
            raise RegisterException("Machine already registered. Please delete old account first and then retry.")

        self.username = r.json()['username']
        self.password = r.json()['password']
        return (self.username, self.password)

    def lock(self, lock):
        r = self.call("locksmith.lock", self.username, self.password, lock)
        if r.status_code == 200:
            try:
                rc = json.loads(r.json()['result'])
            except (Exception,e):
                raise Exception("Malformed reply. Aborting...")

            return [ l['fields'] for l in rc ]

        raise LockException(r.json()['error']['message'])

    def unlock(self, lock):
        r = self.call("locksmith.unlock", self.username, self.password, lock)
        rc = r.json()
        if r.status_code == 200:
            try:
                rc = json.loads(r.json()['result'])
            except (Exception,e):
                raise Exception("Malformed reply. Aborting...")

            return [ l['fields'] for l in rc ]

        raise UnlockException(r.json()['error']['message'])

    def list(self):
        r = self.call("locksmith.list", self.username, self.password)
        if r.status_code == 200:
            try:
                rc = json.loads(r.json()['result'])
            except (Exception,e):
                raise Exception("Malformed reply. Aborting...")

            return [ l['fields'] for l in rc ]

        raise ListException(r.json()['error']['message'])
