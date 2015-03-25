"use strict";

var rpy = angular.module('rpy', []);

rpy.factory('rPyProxy', function($q, $http) {

    function GET(url) {
        return {
            method: 'GET',
            url: url
        };
    };

    function POST(url, data) {
        return {
            method: 'POST',
            url: url,
            data: data
        };
    };

    function makeObject(base_url, data) {
        if (typeof data == 'object' && ('serializer' in data) && ('id' in data) && ('class' in data))
        {
            var o = new Object();
            Object.defineProperty(o, '_id', { value: data.id, enumerable: false });
            Object.defineProperty(o, '_class', { value: data.class, enumerable: false });
            Object.defineProperty(o, '_serializer', { value: data.serializer, enumerable: false });

            o.toJSON = function() {
                return { id: data.id, class: data.class, serializer: data.serializer }
            };

            Object.keys(data.members).forEach(function (m) {
                Object.defineProperty(o, m, {
                    value: data.members[m],
                    writable: false,
                    enumerable: true,
                });
            });

            data.methods.forEach(function (m) {
                Object.defineProperty(o, m, {
                    get: function() {
                        // i hate this fucking primitive language
                        return function(args, kwargs) {
                            return rPyProxy(base_url, data.id, m, { args: args, kwargs: kwargs });
                        }
                    },
                    enumerable: true,
                });
            });

            return o;
        }
        else return data;
    };

    function rPyProxy(base_url, id, method, args)
    {
        if (id == undefined) var config = GET(base_url)
        else var config = POST(base_url + '/' + id + '/' + method, args)

        var p = $http(config).then(function (result) {
            return makeObject(base_url, result.data);
        });

        return p;
    };

    return rPyProxy;
});
