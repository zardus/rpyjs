import json
import flask
import random

class RPyJSSerializer(object):
    def __init__(self):
        self._ids = { }
        self._objects = { }
        self._proto_name = 'rpyjs'

    @staticmethod
    def _next_id():
        return random.randint(0, 2**53) # freaking primitive javascript only supports doubles. WTF

    @staticmethod
    def _serialize_methods(o):
        return [ k for k in dir(o) if not k.startswith('_') and hasattr(getattr(o, k), '__call__') ]

    @staticmethod
    def _serialize_members(o):
        return { k:getattr(o, k) for k in dir(o) if not k.startswith('_') and not hasattr(getattr(o, k), '__call__') }

    def serialize_object(self, o):
        if o in self._ids:
            obj_id = self._ids[o]
        else:
            obj_id = self._next_id()
            self._ids[o] = obj_id
            self._objects[int(obj_id)] = o

        serializer = self._proto_name
        members = self._serialize_members(o)
        methods = self._serialize_methods(o)

        return { 'id': obj_id, 'class': type(o).__name__, 'serializer': serializer, 'members': members, 'methods': methods }

    def _serialize(self, o):
        if type(o) is dict:
            return { k:self.serialize(v) for k,v in o.items() }
        if type(o) in (tuple, list, set):
            return [ self.deserialize(v) for v in o ]
        elif type(o) in (int, str, float, long, bool):
            return o
        else:
            return self.serialize_object(o)

    def serialize(self, o):
        return json.dumps(self._serialize(o))

    def deserialize_id(self, obj_id):
        return self._objects[obj_id]

    def deserialize(self, o):
        if type(o) is dict and 'id' in o and 'class' in o and 'serializer' in o:
            return self.deserialize_id(o['id'])
        elif type(o) is dict:
            return { k:self.deserialize(v) for k,v in o.items() }
        elif type(o) is list:
            return [ self.deserialize(v) for v in o ]
        else:
            return o

class RPyJS(object):
    def __init__(self, base, entry, flask_app=None, serializer=None):
        self._entry = entry
        self._serializer = RPyJSSerializer() if serializer is None else serializer

        if flask_app is not None:
            flask_app.route('/' + base)(self.handle_entry)
            flask_app.route('/' + base + '/<int:obj_id>/<method>', methods=['POST'])(self.handle_call)

    def handle_entry(self):
        return self._serializer.serialize(self._entry)

    def handle_call(self, obj_id, method):
        if 'args' in flask.request.json and flask.request.json['args']:
            json_args = flask.request.json['args']
        else:
            json_args = ()

        if 'kwargs' in flask.request.json and flask.request.json['kwargs']:
            json_kwargs = flask.request.json['kwargs']
        else:
            json_kwargs = {}

        args = self._serializer.deserialize(json_args)
        kwargs = self._serializer.deserialize(json_kwargs)
        o = self._serializer.deserialize_id(obj_id)

        v = getattr(o, method)(*args, **kwargs)
        return self._serializer.serialize(v)

def test():
    class TestCount(object):
        def __init__(self, i):
            self.v = i

        def up(self, delta=0):
            return TestCount(self.v+1+delta)

        def down(self, delta=0):
            return TestCount(self.v-1-delta)

        def add(self, other):
            return TestCount(self.v+other.v)

        def add_int(self, i):
            return TestCount(self.v+i)

        def sum(self, others):
            return self.v + sum(o.v for o in others)

    entry = TestCount(1337)
    app = flask.Flask(__name__, static_folder='static')
    RPyJS('testing', entry, flask_app=app)
    app.run(host='0.0.0.0', port=8080, debug=True)

if __name__ == '__main__':
    test()
