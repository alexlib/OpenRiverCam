// TEMPORARY DOCUMENT READY FUNCTION
$(function() {
    // Add extra rows for bathymetry coordinates.
    $('#add').on('click', () => {
        // Check amount of current rows for next index.
        const count = $('table#coordinates tr>td:first-child').length;
        // Get the last row.
        const lastRow = $('table#coordinates tr:last');
        // Clone row and set input names and values.
        const newRow = lastRow.clone();
        newRow.find('input').each(function() {
            $(this).attr('name', `${$(this).attr('name').substring(0, $(this).attr('name').lastIndexOf("_"))}_${count}`);
            $(this).val('');
        });
        // Insert the row at the end of the table.
        lastRow.after(newRow);
    });
    $('input#_store_csv').on('click', () => {
        $('input#_store_csv').prop('disabled',true);
        const text_area = $('textarea#csv_area');
        const id = $('input#bathymetry_id').val();
        const url_redirect = `/portal/bathymetry`; //details/?id=${id}`
        $.ajax({
            type: 'POST',
            url: `/api/bathymetry_txt/${id}`,
            data: JSON.stringify(text_area.val()),
            contentType: "application/json",
            dataType: 'json',
            success: function() { window.location.href = url_redirect },
            error: function() { $('input#_store_csv').prop('disabled',false);}
        });
    });

    $('#bathymetry-form').submit(function( event ) {
        // Prevent submit.
        event.preventDefault();
        // Prevent double actions.
        $('button[type=submit], input[type=submit]').prop('disabled',true);

        const id = $('input#bathymetry_id').val();
        const form = this;
        const count = $('table#coordinates tr>td:first-child').length;

        // Retrieve coordinates from HTML table.
        const coordinates = [];
        for (let i = 0; i <= count; i++) {
            if ($(`input[name="coordinate_x_${i}"]`) && $(`input[name="coordinate_x_${i}"]`).val()) {
                coordinates.push({
                    "x": $(`input[name="coordinate_x_${i}"]`).val(),
                    "y": $(`input[name="coordinate_y_${i}"]`).val(),
                    "z": $(`input[name="coordinate_z_${i}"]`).val()
                })
            }
        }

        $.ajax({
            type: 'POST',
            url: `/api/bathymetry/${id}`,
            data: JSON.stringify({ "coordinates": coordinates }),
            contentType: "application/json",
            dataType: 'json',
            // Submit parent form on success.
            success: function() { form.submit(); },
            // Enable save button again.
            error: function() { $('button[type=submit], input[type=submit]').prop('disabled',false); }
        });
    });
});