(function($) {
    $.fn.plotPIV = function(movieId, serieTitle) {
        const container = this;
        $.getJSON(
            `/api/visualize/get_velocity_vectors/${movieId}`,
            function( response ) {
                Chart = Highcharts.chart(container.attr('id'), {
                    chart: {
                        plotBackgroundImage: `/api/visualize/get_projected_snapshot/${movieId}`,
                        height: 1110 * ((response["ymax"] - response["ymin"]) / (response["xmax"] - response["xmin"])),
                        width: 1110,
                        margin: 0
                    },
                    legend: {
                        enabled: false
                    },
                    title: {
                        text: null
                    },
                    xAxis: {
                        min: response["xmin"],
                        max: response["xmax"],
                        gridLineWidth: 0,
                        visible: false
                    },
                    yAxis: {
                        min: response["ymin"],
                        max: response["ymax"],
                        gridLineWidth: 0,
                        visible: false
                    },
                    series: [{
                        type: 'vector',
                        name: serieTitle,
                        color: Highcharts.getOptions().colors[6],
                        vectorLength: 10,
                        data: response["data"],
                        turboThreshold:0 // Required for datasets covering more than 1k points.
                    }],
                    exporting: {
                        buttons: {
                            contextButton: {
                                menuItems: ['downloadPNG']
                            }
                        }
                    }
                });
            }
        );

        return this;
    }
})(jQuery);