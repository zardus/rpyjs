import json
import flask
import random

app = flask.Flask(__name__, static_folder='static')

class RPyJS(object):
    def __init__(self, base, entry, flask_app):
        self._ids = { }
        self._objects = { }
        self._entry = entry
        flask_app.route('/' + base)(self.handle_entry)
        flask_app.route('/' + base + '/<obj_id>/<method>', methods=['POST'])(self.handle_call)

    @staticmethod
    def _next_id():
        return random.randint(0, 2**53)

    def serialize(self, o): #pylint:disable=no-self-use
        if o in self._ids:
            obj_id = self._ids[o]
        else:
            obj_id = self._next_id()
            self._ids[o] = obj_id
            self._objects[int(obj_id)] = o

        members = { k:getattr(o, k) for k in dir(o) if not k.startswith('_') and not hasattr(getattr(o, k), '__call__') }
        methods = [ k for k in dir(o) if not k.startswith('_') and hasattr(getattr(o, k), '__call__') ]

        return json.dumps({ 'id': obj_id, 'members': members, 'methods': methods })

    def handle_entry(self):
        return self.serialize(self._entry)

    def handle_call(self, obj_id, method, args=None, kwargs=None):
        args = () if args is None else args
        kwargs = {} if kwargs is None else kwargs

        o = self._objects[int(obj_id)]
        v = getattr(o, method)(*args, **kwargs)

        return self.serialize(v)

def test():
    class TestCount(object):
        def __init__(self, i):
            self.v = i

        def up(self):
            return TestCount(self.v+1)

        def down(self):
            return TestCount(self.v-1)

    entry = TestCount(0)
    RPyJS('testing', entry, app)
    app.run(host='0.0.0.0', port=8080, debug=True)

if __name__ == '__main__':
    test()
