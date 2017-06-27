data = JSON.parse(data);
var signals = data.signals;
var alerts = data.alerts;
var stimuli = data.stimuli;
var obj = JSON.parse(data.obj)[0].fields;
var trial_num = -1;
var score = 0;
var responses = [];
var outcomes = [];
var alertTimeout;
var stimulusTimeout;
var trialTimeout;

$(document).ready(function() {
    $(".button-begin").click(function() {
        trial_num = 0;
        $(".trial-num").show();
        $(".trial-num span").text(trial_num + 1);
        $(".score").show();
        $(".score span").text(score);
        $(".outcome").show();
        changeAlertColor(alerts[trial_num]);
        $(".number").text(stimuli[trial_num]);
        $(".stimulus-rectangle").show();
        $(".stimulus-number").show();
        $(".stimulus-alert").show();
        $(".rectangle").height(stimuli[trial_num] + "%");
        randomizeRectPosition();
        hideStimulus();
        hideAlert();
        $(".button-accept").show();
        $(".button-reject").show();
        $(".intro-text").hide();
        $(".button-begin").hide();
        setTimeout(showStimulus, obj.stimulus_delay * 1000);
        stimulusTimeout = setTimeout(hideStimulus, (obj.stimulus_delay + obj.stimulus_duration) * 1000);
        setTimeout(showAlert, obj.alert_delay * 1000);
        alertTimeout = setTimeout(hideAlert, (obj.alert_delay + obj.alert_duration) * 1000);
        trialTimeout = setTimeout(completeTrial, obj.trial_duration * 1000, "N/A");
    });
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
});

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
            $(".outcome").text("Hit!");
            break;
        case "fa":
            $(".outcome").text("False alarm...");
            break;
        case "miss":
            $(".outcome").text("Miss...");
            break;
        case "cr":
            $(".outcome").text("Correct rejection!");
            break;
        default:
            $(".outcome").text("Did not complete in time...");
    }
}

function completeTrial(b) {
    if (trial_num < obj.num_trials) {
        if (b !== "N/A") {
            responses.push(b);
            var outcome = outcomeMap[b][signals[trial_num]][alerts[trial_num]];
            outcomes.push(outcome);
            changeOutcomeText(outcome);
            score += obj["v_" + outcome];
            $(".score span").text(score);
        }
        else {
            responses.push(b);
            outcomes.push(b);
            changeOutcomeText(b);
        }
        if (trial_num < obj.num_trials - 1) {
            trial_num++;
            $(".trial-num span").text(trial_num + 1);
            changeAlertColor(alerts[trial_num]);
            $(".number").text(stimuli[trial_num]);
            $(".rectangle").height(stimuli[trial_num] + "%");
            randomizeRectPosition();
            setTimeout(function() {
                setTimeout(showStimulus, obj.stimulus_delay * 1000);
                stimulusTimeout = setTimeout(hideStimulus, (obj.stimulus_delay + obj.stimulus_duration) * 1000);
                setTimeout(showAlert, obj.alert_delay * 1000);
                alertTimeout = setTimeout(hideAlert, (obj.alert_delay + obj.alert_duration) * 1000);
                trialTimeout = setTimeout(completeTrial, obj.trial_duration * 1000, "N/A");
            }, obj.trial_delay * 1000);
        }
        else {
            trial_num++;
            alert("Congratulations! You finished the experiment.");
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