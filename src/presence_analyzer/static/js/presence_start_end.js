(function($) {
    $(document).ready(function(){
        var loading = $('#loading');
        $.getJSON("/api/v1/users", function(result) {
            var dropdown = $("#user_id");
            $.each(result, function(item) {
                dropdown.append($("<option />").val(this.user_id).text(this.name));
            });
            dropdown.show();
            loading.hide();
        });
        $('#user_id').change(function(){
            var selected_user = $("#user_id").val();
            var chart_div = $('#chart_div');
            if(selected_user) {
                loading.show();
                chart_div.hide();
                
                $.getJSON("/api/v1/presence_start_end/"+selected_user, function(result) {
                        for (var i = 0; i < result.length; i++) {
                            var start_date = new Date(1, 1, 1),
                                end_date = new Date(1, 1, 1);

                            start_date.setSeconds(result[i][1]);
                            end_date.setSeconds(result[i][2]);
                            result[i][1] = start_date;
                            result[i][2] = end_date;
                        }

                        var data = new google.visualization.DataTable();
                        data.addColumn('string', 'Weekday');
                        data.addColumn({ type: 'datetime', id: 'Start' });
                        data.addColumn({ type: 'datetime', id: 'End' });
                        data.addRows(result);
                        var options = {
                            hAxis: {title: 'Weekday'}
                        };
                        var formatter = new google.visualization.DateFormat({pattern: 'HH:mm:ss'});
                        formatter.format(data, 1);
                        formatter.format(data, 2);

                        chart_div.show();
                        loading.hide();
                        var chart = new google.visualization.Timeline(chart_div[0]);
                        chart.draw(data, options);
                });
            }
        });
    });
})(jQuery);