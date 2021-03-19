$(document).ready(function () {
    pos_y = document.getElementById('position_y');
    pos_x = document.getElementById('position_x');
    crs = document.getElementById('position_crs');
    pos_y.value = -6.8;
    pos_x.value = 39.25;

    var maxAutoZoom = 15;
    var map = L.map('map').setView({lon: 0, lat: 0}, 2);
    var osmLayer = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 18,
        attribution: '&copy; <a href="https://openstreetmap.org/copyright" target="_blank">OpenStreetMap contributors' +
            '</a> ',
        tileSize: 256,
    });
    var googleSat = L.tileLayer('http://{s}.google.com/vt/lyrs=s&x={x}&y={y}&z={z}', {
        maxZoom: 18,
        subdomains:['mt0','mt1','mt2','mt3']
    });
    var googleTer = L.tileLayer('http://{s}.google.com/vt/lyrs=p&x={x}&y={y}&z={z}', {
        maxZoom: 18,
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
    marker = new L.marker([0, 0], {draggable: "true"});
    // update the marker so that it sets everything in the same way
    changeMarker(pos_y.value, pos_x.value);
    marker.addTo(map);

    // add markers (separate function)
    map.on("click", function (e) {
        changeMarker(e.latlng.lat, e.latlng.lng);
    });

    marker.on('dragend', function(e){
        var drag = e.target;
        var position = drag.getLatLng();
        changeMarker(position.lat, position.lng);
    });
    pos_y.onchange = function(){
        position = marker.getLatLng();
        changeMarker(pos_y.value, position.lng);
    };
    pos_x.onchange = function(){
        position = marker.getLatLng();
        changeMarker(position.lat, pos_x.value);
    };
    function changeMarker(lat, lng){
        var newLatLng = new L.LatLng(lat, lng);
        marker.setLatLng(newLatLng, {draggable: "true"}).bindPopup(newLatLng).update();
        pos_y.value = lat;
        pos_x.value = lng;
        setUtm(lat, lng)

    }
    function setUtm(lat, lng){
        // compute the EPSG code based on north-south and longitudinal position
        if (lat < 0){
            utm_zone_1 = 32700
        }
        else{
            utm_zone_1 = 32600
        }
        utm_zone_2 = parseInt(Math.ceil((parseFloat(lng) + 180) / 6));
        utm_zone = utm_zone_1 + utm_zone_2;
        // set value of field
        crs.value = utm_zone;
    }

});
