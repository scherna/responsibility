$(document).ready(function() {
    data = JSON.parse(data);
    signals = data.signals;
    alerts = data.alerts;
    stimuli = data.stimuli;
    obj = JSON.parse(data.obj)[0].fields;
    $(".trial-num").text(0);
    $(".alert").text(alerts[0]);
    $(".stimulus-number").text(stimuli[0]);
});