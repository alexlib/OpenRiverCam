$(document).ready(function () {
    var maxAutoZoom = 18;
    pos_y = -15.42985331;
    pos_x = 28.31623077;
    id = 2;
    name = "check";
    crs = document.getElementById('position_crs');
//    pos_y.value = -6.8;
//    pos_x.value = 39.25;
    var maxAutoZoom = 15;
    var map = L.map('map').setView({lon: 0, lat: 0}, 2);
    var osmLayer = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 18,
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
//    L.control.layers(baseMaps).addTo(map);

    osmLayer.addTo(map);
    // add a scale at at your map.
    var scale = L.control.scale().addTo(map);
    marker = new L.marker([pos_y, pos_x]);
    toolTip = "<dl>" +
        "<dt>ID: " + id + "</dt>" +
        "<dt>Name: " + name + "</dt>" +
        "</dl>"
    marker.bindTooltip(toolTip);
    // update the marker so that it sets everything in the same way
    marker.addTo(map);
    // zoom to marker
    pos = marker.getLatLng();
    map.setView([pos.lat, pos.lng], maxAutoZoom);

});
