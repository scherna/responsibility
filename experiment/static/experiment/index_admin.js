$(document).ready(function() {
    $(".app-experiment").clone().removeClass("app-experiment").addClass("second-table").appendTo("#content-main");
    $(".app-experiment table caption").text("Modules");
    $(".app-experiment .model-experiment").remove();
    $(".app-experiment .model-outputfile").remove();
    $(".second-table table caption").text("Others");
    $(".second-table .model-block").remove();
    $(".second-table .model-example").remove();
    $(".second-table .model-text").remove();
    $(".second-table .model-question").remove();
    $(".second-table .model-questionnaire").remove();
});