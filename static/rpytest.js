rpytest = angular.module('rpyTest', ['rpy']);

rpytest.controller('RPyTestController', ['$scope', 'rPyProxy', function($scope, rPyProxy) {
    rPyProxy("/testing").then(function (result) {
        console.log(result);
    });
}]);
