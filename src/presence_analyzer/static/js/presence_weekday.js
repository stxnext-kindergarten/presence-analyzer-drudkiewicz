google.load("visualization", "1", {packages:["corechart"], 'language': 'en'});

(function($) {
    $(document).ready(function(){
        var loading = $('#loading');
        $('#user_id').change(function(){
            var selected_user = $("#user_id").val();
            var chart_div = $('#chart_div');
            if(selected_user) {
                loading.show();
                chart_div.hide();
                $.getJSON("/api/v1/presence_weekday/"+selected_user, function(result) {
                    var data = google.visualization.arrayToDataTable(result);
                    var options = {};
                    chart_div.show();
                    loading.hide();
                    var chart = new google.visualization.PieChart(chart_div[0]);
                    chart.draw(data, options);
                });
            }
        });
    });
})(jQuery);