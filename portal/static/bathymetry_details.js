$(document).ready(function () {
    const id = $('input#bathymetry_id').val();
    $.ajax({
        type: 'GET',
        url: `/api/bathymetry_details/${id}`,
        contentType: "application/json",
        dataType: 'json',
        success: function(data) {
            console.log(data);
            map_bathymetry(data);
            cross_section(data);
        },

        error: function() {console.log("Something went wrong")}
    });
});

cross_section = function(data) {
    // add a highchart of the bathymetry profile
    Highcharts.chart('cross_section', {
        chart: {
        },
        title: {
            text: `Bathymetry at site ${data.site_id} - ${data.site_name}`
        },
        subtitle: {
            text: 'YZ profile (left bank is zero)'
        },
        xAxis: {
            reversed: false,
            title: {
                enabled: true,
                text: 'Distance from left-bank'
            },
            labels: {
                format: '{value} m'
            },
//            accessibility: {
//                rangeDescription: 'Range: 0 to 80 m.'
//            },
            maxPadding: 0.05,
            showLastLabel: true
        },
        yAxis: {
            title: {
                text: 'Elevation above reference level'
            },
            labels: {
                format: '{value} m'
            },
//            accessibility: {
//                rangeDescription: 'Range: -90°C to 20°C.'
//            },
            lineWidth: 2
        },
        legend: {
            enabled: false
        },
        tooltip: {
            headerFormat: '<b>{series.name}</b><br/>',
            pointFormat: 'Distance: {point.x} m, Elevation: {point.y} m'
        },
        plotOptions: {
            spline: {
                marker: {
                    enable: false
                }
            }
        },
        series: [{
            name: 'Bathymetry',
            data: data.bathym_yz,
        }]
    });
}
map_bathymetry = function(data) {
   // make a nice geospatial map
    var maxAutoZoom = 19;
    var map = L.map('map').setView({lon: 0, lat: 0}, 2);
    var osmLayer = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 20,
        attribution: '&copy; <a href="https://openstreetmap.org/copyright" target="_blank">OpenStreetMap contributors' +
            '</a> ',
        tileSize: 256,
    });
    var googleSat = L.tileLayer('http://{s}.google.com/vt/lyrs=s&x={x}&y={y}&z={z}', {
        maxZoom: 20,
        subdomains:['mt0','mt1','mt2','mt3']
    });
    var googleTer = L.tileLayer('http://{s}.google.com/vt/lyrs=p&x={x}&y={y}&z={z}', {
        maxZoom: 20,
        subdomains:['mt0','mt1','mt2','mt3']
    });
    var baseMaps = {
        "OpenStreetMap": osmLayer,
        "Google Satellite": googleSat,
        "Google Terrain": googleTer

    }
    L.control.layers(baseMaps).addTo(map);
    osmLayer.addTo(map);
    // add a scale at at your map.
    var scale = L.control.scale().addTo(map);
    // add site position to map
    marker = new L.marker(data.site_position);
    toolTip = "<dl>" +
        "<dt>ID: " + data.site_id + "</dt>" +
        "<dt>Name: " + data.site_name + "</dt>" +
        "</dl>"
    marker.bindTooltip(toolTip);
    // update the marker so that it sets everything in the same way
    marker.addTo(map);
    // zoom to marker
    pos = marker.getLatLng();
    map.setView([pos.lat, pos.lng], maxAutoZoom);

    // add bathymetry to map
    L.geoJson(data.bathym_geojson, {
        style: function(feature) {
            return {
            stroke: true,
            color: "red",
            weight: 5
            }
        }
    }).addTo(map);
}
