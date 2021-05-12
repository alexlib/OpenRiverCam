$(document).ready(function () {

    // fill the epsg dropdown with info
    $.ajax({
        type: 'GET',
        url: `/api/get_epsg_codes`,
        contentType: "application/json",
        dataType: 'json',
        success: function(data) {
                // clear any inputs
                $("#crs").empty();
                $("#crs").append($("<option></option>").val("none").html(`Same as selected site`));
                $.each(data, function () {
                    $("#crs").append($("<option></option>").val(this['epsg']).html(`EPSG:${this['epsg']} ${this['name']}`));
            });
        }
    });
});
