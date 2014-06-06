function create_chart(name) {
    var stamp = 0;

    var left = [];
    var right = [];

    var chart = new CanvasJS.Chart(name + '_chart', {
        data: [
            { type: 'line', dataPoints: left },
            { type: 'line', dataPoints: right }
        ]
    });

    return { 'name': name, 'stamp': stamp, 'left': left, 'right': right, 'chart': chart };
}

function fill_chart(chart, data) {
    chart['stamp'] = chart['stamp'] + 1;

    chart['left'].push({x: chart['stamp'], y: data.x});
    chart['right'].push({x: chart['stamp'], y: data.y});

    if (chart['left'].length >= 50) {
        chart['left'].shift();
    }
    if (chart['right'].length >= 50) {
        chart['right'].shift();
    }

    chart['chart'].render();

    $('#' + chart['name'] + '_left').html(data.x);
    $('#' + chart['name'] + '_right').html(data.y);
}

$(document).ready(function () {
    var charts_names = ['manual', 'randomize', 'rodeo_swap', 'back', 'controller', 'stop', 'pid', 'driver'];
    var charts = {}

    for (var index = 0; index < charts_names.length; index++) {
        var name = charts_names[index];
        charts[name] = create_chart(name);
    }

    var ws = new WebSocket('ws://' + document.domain + ':8888/');

    ws.onmessage = function (event) {
        var data = $.parseJSON(event.data);
        $('#log').prepend(data.target + ' => ' + data.data + '<br/>');
        fill_chart(charts[data.target], data);
    }
});