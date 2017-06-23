(function($) {
    $(document).ready(function() {
        $(".matrix").find("label").remove();
        $(".matrix").find("input").unwrap();
        $(".matrix").find("input").wrap("<td></td>");
        $(".matrix").find("td").slice(0,4).wrapAll("<tr></tr>").first().before("<th>User: Signal</th>");
        $(".matrix").find("td").slice(4,8).wrapAll("<tr></tr>").first().before("<th>User: Noise</th>");
        $(".matrix").find(".form-row").wrap("<table></table>");
        $(".matrix").find("tr").first().unwrap().before('<tr><th></th><th colspan="2">Signal</th><th colspan="2">Noise</th></tr><tr><th>Alert:</th><th>Signal</th><th>Noise</th><th>Signal</th><th>Noise</th></tr>');
        $("table").css("display", "inline-block").clone().addClass("help-table").css("margin-left", "50px").appendTo(".matrix");
        $(".help-table tr:nth-child(3) td:nth-child(2)").attr("colspan", "2").children().replaceWith("<p>HIT</p>");
        $(".help-table tr:nth-child(3) td:nth-child(3)").remove();
        $(".help-table tr:nth-child(3) td:nth-child(3)").attr("colspan", "2").children().replaceWith("<p>FA</p>");
        $(".help-table tr:nth-child(3) td:nth-child(4)").remove();
        $(".help-table tr:nth-child(4) td:nth-child(2)").attr("colspan", "2").children().replaceWith("<p>MISS</p>");
        $(".help-table tr:nth-child(4) td:nth-child(3)").remove();
        $(".help-table tr:nth-child(4) td:nth-child(3)").attr("colspan", "2").children().replaceWith("<p>CR</p>");
        $(".help-table tr:nth-child(4) td:nth-child(4)").remove();
        $(".help-table p").css("text-align", "center").css("font-size", "24px").css("margin", "auto");
});
}(django.jQuery));