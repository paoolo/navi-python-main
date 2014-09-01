jQuery.fn.visible = function() {
    this.css('display', '')
    this.css('visibility', '');
    return this;
};

charts = {}

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

    charts[name] = { 'name': name, 'stamp': stamp, 'left': left, 'right': right, 'chart': chart };

    $('#' + name + '_panel').visible();
    $('#' + name + '_chart').visible();
}

function fill_chart(chart, data) {
    if (typeof chart === 'undefined')
        return;

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
    var ws = new WebSocket('ws://' + document.domain + ':8888/');

    ws.onmessage = function (event) {
        var data = $.parseJSON(event.data);
        fill_chart(charts[data.target], data);
    }
});