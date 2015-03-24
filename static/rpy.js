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

    function makeObject(base_url, id, methods, members) {
        var o = new Object();
        Object.defineProperty(o, '_rpy_id', { value: id, enumerable: false })

        Object.keys(members).forEach(function (m) {
            Object.defineProperty(o, m, {
                value: members[m],
                writable: false,
                enumerable: true,
            });
        });

        methods.forEach(function (m) {
            Object.defineProperty(o, m, {
                get: function() {
                    // i hate this fucking primitive language
                    return function(args, varargs) {
                        return rPyProxy(base_url, id, m, { args: args, varargs: varargs });
                    }
                },
                enumerable: true,
            });
        });

        return o;
    };

    function rPyProxy(base_url, id, method, args)
    {
        if (id == undefined) var config = GET(base_url)
        else var config = POST(base_url + '/' + id + '/' + method, args)

        var p = $http(config).then(function (result) {
            return makeObject(base_url, result.data.id, result.data.methods, result.data.members);
        });

        return p;
    };

    return rPyProxy;
});
