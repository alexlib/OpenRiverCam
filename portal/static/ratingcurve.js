$(document).ready(function () {
    field_a = document.getElementById('a');
    field_b = document.getElementById('b');
    field_h0 = document.getElementById('h0');

    // prepare phony data, this needs to be replaced by h and Q estimates from filtered points
    var h = [
            0.3, 0.2, 0.3, 0.45, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0
        ];
    var Q = [
            0.201558520554371, 1.26239032474249, 2.96265491948767, 5.19654734918048, 7.90653417985158,
            11.0541905393208, 14.6112227039883, 18.5555385881248, 22.8691941066439, 27.5371934516811
        ];
    var ids = [
            10, 9, 8, 7, 6, 5, 4, 3, 2, 1
        ];
    var pars = {
            'h0': 0.05, 'a': 30, 'b': 1.67
        }
    var siteId = 1;
    var name = "Chuo Kikuu";
    function getChart(){
        Chart = Highcharts.chart('rating-curve', {
            chart: {
            },
            title: {
                text: 'Rating Curve for ' + name
            },
            xAxis: {
                title: {
                    enabled: true,
                    text: 'Level [m]'
                },
                min: 0,
                gridLineWidth: 0,
                visible: true,
                startOnTick: true,
                endOnTick: true,
                showLastLabel: true
            },
            yAxis: {
                title: {
                    enabled: true,
                    text: 'Discharge [m3/s]'
                },

                min: 0,
                gridLineWidth: 0,
                visible: true,
                startOnTick: true,
                endOnTick: true,
                showLastLabel: true
            },
            legend: {
                layout: 'vertical',
                align: 'left',
                verticalAlign: 'top',
                x: 100,
                y: 70,
                floating: true,
                backgroundColor: Highcharts.defaultOptions.chart.backgroundColor,
                borderWidth: 0
            },

            plotOptions: {
                scatter: {
                    cursor: 'pointer',
                    marker: {
                        symbol: 'circle',
                        radius: 5,
                        states: {
                            hover: {
                                enabled: true,
                                lineColor: 'rgb(100,100,100)'
                            }
                        }
                    },
                    states: {
                        hover: {
                            marker: {
                                enabled: true
                            }
                        }
                    },
                    point: {
                        events: {
                            click: function () {
                                if (this.include == true) {
                                    this.include = false;
                                    this.color = 'rgba(0, 0, 0, 0.35)';
                                }
                                else {
                                    this.include = true;
                                    this.color = 'rgba(210, 70, 90, 0.9)';
                                }
                                // refit on the data
                                fitData();
                                this.series.redraw();


                            }
                        }
                    }
                }
            },
            tooltip: {
              useHTML: true,
              style: {
                pointerEvents: 'auto'
              }
            },

            series: [
                {
                    tooltip: {
                        useHTML: true,
                        headerFormat: '<b>{series.name}</b><br>',
                        pointFormatter: function() {
                            var string = 'id: ' + this.name + ', ' + this.x.toFixed(4) + ' m, ' + this.y.toFixed(4) +
                                ' m3/s<br>';
                            string += 'Click <a href="/portal/movies/details/?id=' + this.name +
                                '&url=%2Fportal%2Fmovies%2F" target="_blank">here</a> to inspect';
//                            string += '<a href="http://www.google.com">check!</a><br>';
                            return string;
                        }
                    },
                    type: 'scatter',
                    zoomType: 'xy',
                    name: 'Rating points',
                    color: 'rgba(210, 70, 90, 0.9)',
    //                data: h.map(function(e, i) {
    //                          return [e, Q[i]];

                    data: h.map(function(e, i) {
                              return {x: e, y: Q[i], name: ids[i], include: true};
                          }), //[[0.5, 0.5], [1, 1]],
                    turboThreshold: 0, // Required for datasets covering more than 1k points.
                }
//                {
//                    type: 'line',
//                    hover: false,
//                    zoomType: 'xy',
//                    name: 'Rating curve fit',
//                    color: 'rgba(200, 200, 200, 1)',
//                    marker: {
//                        enabled: false
//                    },
//                    data: data.h.map(function(e, i) {
//                              return [e, data.Q[i]];
//                          }), //[[0.5, 0.5], [1, 1]],
//
//                    turboThreshold: 0, // Required for datasets covering more than 1k points.
//                    enableMouseTracking: false
//                },

            ],

            exporting: {
                buttons: {
                    contextButton: {
                        menuItems: ['downloadPNG']
                    }
                }
            }
        });
        return Chart;
    }
    function fitChart (pars) {
        // make a set of samples for h to plot the fit in
        var hmin = Math.min(...h);
        var hmax = Math.max(...h);
        var hint = (hmax - hmin) / 1000;
        var hrange = [];
        var hcur = hmin;
        for (var i = 0; i < 1000; i++) {
            hrange.push(hcur)
            hcur += hint;
            }

        // retrieves data from existing chart, sends to server to retrieve a fit and plots that fit
//        samples = readSamples()
        data = hrange.map(function(e, i) {
                      return [e, pars.a*Math.pow(Math.max(e-pars.h0, 0), pars.b)];
                  })
        if ( Chart.series.length > 1 ) {
            // replace data of existing graph
            Chart.series[1].setData(data);
        }
        else {
            Chart.addSeries({
                type: 'line',
                hover: false,
                zoomType: 'xy',
                name: 'Rating curve fit',
                color: 'rgba(200, 200, 200, 1)',
                marker: {
                    enabled: false
                },
                data: data,
                turboThreshold: 0, // Required for datasets covering more than 1k points.
                enableMouseTracking: false
            });
        }
        Chart.setSubtitle ({
            text: 'Q = ' + pars.a.toFixed(2) + ' * (h - ' + pars.h0.toFixed(2) + ' )^' +
                pars.b.toFixed(2)
        });
        // change field values
        field_a.value = pars.a;
        field_b.value = pars.b;
        field_h0.value = pars.h0;
    }
    function fitData() {
        // read samples and their current state from the graph
        scatter = Chart.series[0].data;
        var samples = {water_level: [], discharge: [], include: []};
        for (var i = 0; i < scatter.length; i++) {
            if (scatter[i].include == true) {
                samples.water_level.push(parseFloat(scatter[i].x))
                samples.discharge.push(parseFloat(scatter[i].y))

            }
        }
        // fit new rating curve parameters
        $.getJSON(
        '/api/visualize/get_rating_curve/${siteId}',
        {

            water_level: JSON.stringify(samples.water_level),
            discharge: JSON.stringify(samples.discharge)
        },
        function(data){
            console.log(data);
            fitChart(data);
        }
    );

//            samples.include.push(scatter[i].include)
        return samples;
    }

    Chart = getChart();

    fitData();
//    console.log(readSamples());
//    console.log(Chart.series);
    // get the scatter series
//    scatter = Chart.series[1].data;

});

