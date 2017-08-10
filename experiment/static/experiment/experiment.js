var moduleNum = 0;
var obj;
var signals;
var alerts;
var stimuli;
var trialNum;
var score;
var points;
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
            else {
                renderExample(module);
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
            $(".content").html('<h6>Your results have been successfully uploaded. Thank you for your participation.</h6>');
        });
    }
}

function renderQuestionnaire(module) {
    var questions = module.questions;
    var myHtml = `<div class="columns">
                    <div class="column col-2 hide-xs"></div>
                    <div class="column col-8 col-xs-12">
                        <form style="text-align:left;" id="myForm">`;
    questions.forEach(function(q) {
        if (q[1][0] === '') {
            myHtml += `<div class="form-group" dir="auto">
                        <label class="form-label" for="${q[2]}">${q[0]}</label>
                        <input class="form-input" type="text" id="${q[2]}" name="${q[2]}" required/>
                      </div>`;
        }
        else {
            myHtml += `<div class="form-group" dir="auto">
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
    myHtml += `<div style="text-align:center;"><button type="submit" class="btn btn-primary">Next</button></div></form></div></div>`;
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
    var text = module[0].fields.text.replace(/\n/g, "<br />");
    $(".content").html(`<div class="columns intro-text">
                            <div class="column col-2 hide-xs"></div>
                            <div class="column col-8 col-xs-12">
                                <p style="text-align:justify;" dir="auto">${text}</p>
                            </div>
                        </div>
                        <button type="button" class="button-next btn btn-primary">Next</button>`);
    $(".button-next").click(function() {
        moduleNum++;
        renderModule(moduleNum);
    });
}

function renderExample(module) {
    var object = module[0].fields;
    $(".content").html(`<div class="columns">
                            <div class="column col-3 hide-xs"></div>
                            <div class="column col-2 col-xs-4">
                                <div class="trial-num">Trial#: <span></span></div>
                            </div>
                            <div class="column col-half"></div>
                            <div class="column col-1 col-xs-4">
                                <div class="stimulus-alert centered"></div>
                            </div>
                            <div class="column col-5">
                                <div class="columns">
                                    <div class="column col-4">
                                        <div class="points">Last Trial: <span></span></div>
                                    </div>
                                    <div class="column col-4">
                                        <div class="outcome"></div>
                                    </div>
                                    <div class="column col-4">
                                        <div class="score">Total Score: <span></span></div>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div class="columns">
                            <div class="column col-4 hide-xs"></div>
                            <div class="column col-4 col-xs-12">
                                ${object.stimulus === "num" ? '<div class="stimulus-number"><div class="number"></div></div>' : '<div class="stimulus-rectangle"><div class="rectangle"></div></div>'}
                            </div>
                        </div>
                        <button type="button" class="button-next btn btn-primary">Next</button>`);
    $(".trial-num span").text(object.num_trial);
    $(".score span").text(object.score);
    $(".points span").text(object.points);
    $(".outcome").text(object.outcome);
    $(".stimulus-alert").css("background-color", object.alert_color);
    $(".number").text(object.val);
    $(".rectangle").height(object.val + "%");
    randomizeRectPosition();
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
    points = 0;
    responses = [];
    outcomes = [];
    alertTimeout;
    stimulusTimeout;
    trialTimeout;
    $(".content").html(`<div class="columns">
                            <div class="column col-3 hide-xs"></div>
                            <div class="column col-2 col-xs-4">
                                ${obj.display_trial_num ? '<div class="trial-num">Trial#: <span></span></div>' : ''}
                            </div>
                            <div class="column col-half"></div>
                            <div class="column col-1 col-xs-4">
                                <div class="stimulus-alert centered"></div>
                            </div>
                            <div class="column col-5">
                                <div class="columns">
                                    <div class="column col-4">
                                        ${obj.display_last_points ? '<div class="points">Last Trial: <span></span></div>' : ''}
                                    </div>
                                    <div class="column col-4">
                                        ${obj.display_outcome ? '<div class="outcome invisible">Hidden</div>' : ''}
                                    </div>
                                    <div class="column col-4">
                                        ${obj.display_total_points ? '<div class="score">Total Score: <span></span></div>' : ''}
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div class="columns">
                            <div class="column col-4 hide-xs"></div>
                            <div class="column col-4 col-xs-12">
                                ${obj.stimulus === "num" ? '<div class="stimulus-number"><div class="number"></div></div>' : '<div class="stimulus-rectangle"><div class="rectangle"></div></div>'}
                            </div>
                        </div>
                        <div class="columns">
                            <div class="column col-5 col-xs-1"></div>
                            <div class="column col-1 col-xs-5"><button type="button" class="button-accept btn btn-primary">Accept</button></div>
                            <div class="column col-1 col-xs-5"><button type="button" class="button-reject btn btn-primary">Reject</button></div>
                        </div>`);
    $(".trial-num span").text(trialNum + 1);
    $(".score span").text(score);
    $(".points span").text(points);
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
            $(".outcome").text("Out of time...");
    }
}

function completeTrial(b) {
    trialEndTime = Date.now();
    $("button").prop("disabled", true);
    if (trialNum < obj.num_trials) {
        responses.push(b);
        var outcome = b !== "N/A" ? outcomeMap[b][signals[trialNum]][alerts[trialNum]] : "N/A";
        outcomes.push(outcome);
        changeOutcomeText(outcome);
        points = b !== "N/A" ? obj["v_" + outcome] : obj["v_na"];
        score += points;
        $(".score span").text(score);
        $(".points span").text(points);
        results['blocks'][results['blocks'].length-1]['trials'].push({
            'trial_num': trialNum+1, 
            'time': trialEndTime, 
            'response_time': (trialEndTime-trialBeginTime), 
            'signal': signals[trialNum], 
            'alert': alerts[trialNum], 
            'response': b, 
            'outcome': outcome,
            'points': points,
        });
        if (trialNum < obj.num_trials - 1) {
            trialNum++;
            $(".trial-num span").text(trialNum + 1);
            changeAlertColor(alerts[trialNum]);
            $(".number").text(stimuli[trialNum]);
            $(".rectangle").height(stimuli[trialNum] + "%");
            randomizeRectPosition();
            setTimeout(function() {
                $("button").prop("disabled", false);
                hideOutcome();
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

function hideOutcome() {
    $(".outcome").addClass("invisible");
}

function showOutcome() {
    $(".outcome").removeClass("invisible");
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