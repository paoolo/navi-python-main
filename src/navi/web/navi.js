$(document).ready(function(){
    var socket = io.connect('http://' + document.domain + ':' + location.port + '/navi');

    socket.on('log_response', function(msg) {
        $('#log').append('<p>' + msg.data + '</p>');
    });
    names = ['manual', 'randomize', 'rodeo_swap', 'back', 'controller', 'stop', 'pid', 'driver']
    for (var i = 0; i < names.length; i++) {
        var name = names[i];
        socket.on(name + '_response', function(msg) {
            $('#'+name+'_comp' ).append('<p>' + msg.data + '</p>');
        });
    }
});