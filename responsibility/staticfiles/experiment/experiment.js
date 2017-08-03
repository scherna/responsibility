var moduleNum = 0;
var obj;
var signals;
var alerts;
var stimuli;
var trialNum;
var score;
var responses;
var outcomes;
var alertTimeout;
var stimulusTimeout;
var trialTimeout;
var trialBeginTime;
var trialEndTime;
var results = {
    'experiment_id': experimentId,
    'blocks': [],
    'questionnaires': [],
};

$(document).ready(function() {
    renderModule(moduleNum);
});

function renderModule(moduleNum) {
    if (moduleNum < modules.length) {
        var module = modules[moduleNum];
        if (module.constructor === Array) {
            if (module[0].model === "experiment.text") {
                renderText(module);
            }
        }
        else {
            if (module.obj[0].model === 'experiment.block') {
                renderBlock(module);
            }
            else {
                renderQuestionnaire(module);
            }
        }
    }
    else {
        var csrftoken = $.cookie('csrftoken');
        $.ajaxSetup({
            beforeSend: function(xhr, settings) {
                if (!this.crossDomain) {
                    xhr.setRequestHeader("X-CSRFToken", csrftoken);
                }
            }
        });
        results['blocks'] = JSON.stringify(results['blocks'])
        results['questionnaires'] = JSON.stringify(results['questionnaires'])
        $.post("/experiment/results/", results, function() {
            $(".content").html('<h5>Your results have been successfully uploaded. Thank you for your participation.</h5>');
        });
    }
}

function renderQuestionnaire(module) {
    var questions = module.questions;
    var myHtml = `<div class="columns">
                    <div class="column col-xl-3 hide-xs"></div>
                    <div class="column col-xl-6 col-xs-12">
                        <form style="text-align:left;" id="myForm">`;
    questions.forEach(function(q) {
        if (q[1][0] === '') {
            myHtml += `<div class="form-group">
                        <label class="form-label" for="${q[2]}">${q[0]}</label>
                        <input class="form-input" type="text" id="${q[2]}" name="${q[2]}" required/>
                     </div>`;
        }
        else {
            myHtml += `<div class="form-group">
                        <label class="form-label">${q[0]}</label>`;
            q[1].forEach(function(c) {
                myHtml += `<label class="form-radio">
                            <input type="radio" name="${q[2]}" value="${c}" required/>
                            <i class="form-icon"></i> ${c}
                        </label>`;
            });
            myHtml += `</div>`;
        }
    }, this);
    myHtml += `<button type="submit" class="btn btn-primary" style="text-align:center;">Next</button></form></div></div>`;
    $(".content").html(myHtml);
    $("#myForm").submit(function(event) {
        event.preventDefault();
        var qs = [];
        questions.forEach(function(q) {
            var answer;
            if (q[1][0] === '') {
                answer = $(`#${q[2]}`).val();
            }
            else {
                answer = $(`input[name=${q[2]}]:checked`).val();
            }
            qs.push({'id':q[2], 'answer':answer})
        });
        results['questionnaires'].push({'id':module.obj[0].pk, 'questions':qs});
        moduleNum++;
        renderModule(moduleNum);
        return false;
    });
}

function renderText(module) {
    var text = module[0].fields.text;
    $(".content").html(`<div class="columns intro-text">
                            <div class="column col-xl-3 hide-xs"></div>
                            <div class="column col-xl-6 col-xs-12">
                                <p style="text-align:justify;">${text}</p>
                            </div>
                        </div>
                        <button type="button" class="button-next btn btn-primary">Next</button>`);
    $(".button-next").click(function() {
        moduleNum++;
        renderModule(moduleNum);
    });
}

function renderBlock(module) {
    obj = module.obj[0].fields;
    signals = module.signals;
    alerts = module.alerts;
    stimuli = module.stimuli;
    trialNum = 0;
    score = 0;
    responses = [];
    outcomes = [];
    alertTimeout;
    stimulusTimeout;
    trialTimeout;
    $(".content").html(`<div class="columns">
                            <div class="column col-xl-4 hide-xs"></div>
                            <div class="column col-xl-1 col-xs-3">
                                ${obj.display_trial_num ? '<div class="trial-num">Trial#: <span></span></div>' : ''}
                            </div>
                            <div class="column col-xl-2 col-xs-6">
                                <div class="stimulus-alert centered"></div>
                            </div>
                            <div class="column col-xl-1 col-xs-3">
                                ${obj.display_total_points ? '<div class="score">Score: <span></span></div>' : ''}
                            </div>
                        </div>
                        <div class="columns">
                            <div class="column col-xl-4 hide-xs"></div>
                            <div class="column col-xl-4 col-xs-12">
                                ${obj.stimulus === "num" ? '<div class="stimulus-number"><div class="number"></div></div>' : '<div class="stimulus-rectangle"><div class="rectangle"></div></div>'}
                            </div>
                        </div>
                        ${obj.display_last_points ? '<div class="outcome invisible">Hidden</div>' : ''}
                        <div class="columns">
                            <div class="column col-xl-5 col-xs-1"></div>
                            <div class="column col-xl-1 col-xs-5"><button type="button" class="button-accept btn btn-primary">Accept</button></div>
                            <div class="column col-xl-1 col-xs-5"><button type="button" class="button-reject btn btn-primary">Reject</button></div>
                        </div>`);
    $(".trial-num span").text(trialNum + 1);
    $(".score span").text(score);
    changeAlertColor(alerts[trialNum]);
    $(".number").text(stimuli[trialNum]);
    $(".rectangle").height(stimuli[trialNum] + "%");
    randomizeRectPosition();
    hideStimulus();
    hideAlert();
    setTimeout(showStimulus, obj.stimulus_delay * 1000);
    stimulusTimeout = setTimeout(hideStimulus, (obj.stimulus_delay + obj.stimulus_duration) * 1000);
    setTimeout(showAlert, obj.alert_delay * 1000);
    alertTimeout = setTimeout(hideAlert, (obj.alert_delay + obj.alert_duration) * 1000);
    trialTimeout = setTimeout(completeTrial, obj.trial_duration * 1000, "N/A");
    trialBeginTime = Date.now();
    results['blocks'].push({'id':module.obj[0].pk, 'score':0, 'trials':[]});
    $(".button-accept").click(function() {
        clearTimeout(stimulusTimeout);
        hideStimulus();
        clearTimeout(alertTimeout);
        hideAlert();
        clearTimeout(trialTimeout);
        completeTrial(false);
    });
    $(".button-reject").click(function() {
        clearTimeout(stimulusTimeout);
        hideStimulus();
        clearTimeout(alertTimeout);
        hideAlert();
        clearTimeout(trialTimeout);
        completeTrial(true);
    });
}

function changeAlertColor(b) {
    if (b) {
        $(".stimulus-alert").css("background-color", obj.alert_signal_color);
    }
    else {
        $(".stimulus-alert").css("background-color", obj.alert_noise_color);
    }
}

function changeOutcomeText(o) {
    if ($(".outcome").hasClass("invisible")) {
        $(".outcome").removeClass("invisible");
    }
    switch (o.slice(0, -2)) {
        case "hit":
            $(".outcome").text("Correct!");
            break;
        case "fa":
            $(".outcome").text("Incorrect...");
            break;
        case "miss":
            $(".outcome").text("Incorrect...");
            break;
        case "cr":
            $(".outcome").text("Correct!");
            break;
        default:
            $(".outcome").text("Did not complete in time...");
    }
}

function completeTrial(b) {
    trialEndTime = Date.now();
    $("button").prop("disabled", true);
    if (trialNum < obj.num_trials) {
        if (b !== "N/A") {
            responses.push(b);
            var outcome = outcomeMap[b][signals[trialNum]][alerts[trialNum]];
            outcomes.push(outcome);
            changeOutcomeText(outcome);
            var points = obj["v_" + outcome];
            score += points;
            $(".score span").text(score);
            results['blocks'][results['blocks'].length-1]['trials'].push({
                'trial_num': trialNum, 
                'time': trialEndTime, 
                'response_time': (trialEndTime-trialBeginTime), 
                'signal': signals[trialNum], 
                'alert': alerts[trialNum], 
                'response': b, 
                'outcome': outcome,
                'points': points,
            });
        }
        else {
            responses.push(b);
            outcomes.push(b);
            changeOutcomeText(b);
            results['blocks'][results['blocks'].length-1]['trials'].push({
                'trial_num': trialNum, 
                'time': trialEndTime, 
                'response_time': (trialEndTime-trialBeginTime), 
                'signal': signals[trialNum], 
                'alert': alerts[trialNum], 
                'response': b, 
                'outcome': b,
                'points': 0,
            });
        }
        if (trialNum < obj.num_trials - 1) {
            trialNum++;
            $(".trial-num span").text(trialNum + 1);
            changeAlertColor(alerts[trialNum]);
            $(".number").text(stimuli[trialNum]);
            $(".rectangle").height(stimuli[trialNum] + "%");
            randomizeRectPosition();
            setTimeout(function() {
                $("button").prop("disabled", false);
                trialBeginTime = Date.now();
                setTimeout(showStimulus, obj.stimulus_delay * 1000);
                stimulusTimeout = setTimeout(hideStimulus, (obj.stimulus_delay + obj.stimulus_duration) * 1000);
                setTimeout(showAlert, obj.alert_delay * 1000);
                alertTimeout = setTimeout(hideAlert, (obj.alert_delay + obj.alert_duration) * 1000);
                trialTimeout = setTimeout(completeTrial, obj.trial_duration * 1000, "N/A");
            }, obj.trial_delay * 1000);
        }
        else {
            results['blocks'][results['blocks'].length-1]['score'] = score;
            trialNum++;
            moduleNum++;
            renderModule(moduleNum);
        }
    }
}

function hideStimulus() {
    $(".number").addClass("invisible");
    $(".rectangle").addClass("invisible");
}

function showStimulus() {
    $(".number").removeClass("invisible");
    $(".rectangle").removeClass("invisible");
}

function hideAlert() {
    $(".stimulus-alert").addClass("invisible");
}

function showAlert() {
    $(".stimulus-alert").removeClass("invisible");
}

function randomizeRectPosition() {
    var availableHeight = $(".stimulus-rectangle").width() - $(".rectangle").height();
    var availableWidth = $(".stimulus-rectangle").width() - $(".rectangle").width();
    $(".rectangle").css("top", (Math.random() * availableHeight).toString());
    $(".rectangle").css("left", (Math.random() * availableWidth).toString());
}

outcomeMap = {
    //user signal
    true: {
        //system signal
        true: {
            true: "hit_s", //alert signal
            false: "hit_n", //alert noise
        },
        //system noise
        false: {
            true: "fa_s", //alert signal
            false: "fa_n", //alert noise
        },
    },
    //user noise
    false: {
        //system signal
        true: {
            true: "miss_s", //alert signal
            false: "miss_n", //alert noise
        },
        //system noise
        false: {
            true: "cr_s", //alert signal
            false: "cr_n", //alert noise
        },
    },
};