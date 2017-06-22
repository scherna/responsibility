data = JSON.parse(data);
var signals = data.signals;
var alerts = data.alerts;
var stimuli = data.stimuli;
var obj = JSON.parse(data.obj)[0].fields;
var trial_num = -1;
var score = 0;
var responses = [];
var outcomes = [];

$(document).ready(function() {
    $(".button-begin").click(function() {
        trial_num = 0;
        $(".trial-num").show();
        $(".trial-num span").text(trial_num + 1);
        $(".score").show();
        $(".score span").text(score);
        $(".outcome").show();
        $(".stimulus-alert").show();
        changeAlertColor(alerts[trial_num]);
        $(".stimulus-number").show().text(stimuli[trial_num]);
        $(".stimulus-rectangle").show()
        $(".button-accept").show();
        $(".button-reject").show();
        $(".intro-text").hide();
        $(".button-begin").hide();
    });
    $(".button-accept").click(function() {
        buttonHandler(false);
    });
    $(".button-reject").click(function() {
        buttonHandler(true);
    });
});

function changeAlertColor(b) {
    if (b === true) {
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
    }
}

function buttonHandler(b) {
    if (trial_num < obj.num_trials) {
        responses.push(b);
        var outcome = outcomeMap[b][signals[trial_num]][alerts[trial_num]];
        outcomes.push(outcome);
        changeOutcomeText(outcome);
        score += obj["v_" + outcome];
        $(".score span").text(score);
        if (trial_num < obj.num_trials - 1) {
            trial_num++;
            $(".trial-num span").text(trial_num + 1);
            changeAlertColor(alerts[trial_num]);
            $(".stimulus-number").text(stimuli[trial_num]);
        }
        else {
            trial_num++;
            alert("Congratulations! You finished the experiment.");
        }
    }
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