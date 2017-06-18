(function($) {
    $(document).ready(function() {
        $(".matrix").find("label").remove();
        $(".matrix").find("input").unwrap();
        $(".matrix").find("input").wrap("<td></td>");
        $(".matrix").find("td").slice(0,4).wrapAll("<tr></tr>").first().before("<th>User: Signal</th>");
        $(".matrix").find("td").slice(4,8).wrapAll("<tr></tr>").first().before("<th>User: Noise</th>");
        $(".matrix").find(".form-row").wrap("<table></table>");
        $(".matrix").find("tr").first().unwrap().before('<tr><th></th><th colspan="2">Signal</th><th colspan="2">Noise</th></tr><tr><th>Alert:</th><th>Signal</th><th>Noise</th><th>Signal</th><th>Noise</th></tr>');
    });
}(django.jQuery));