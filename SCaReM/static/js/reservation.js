// date & time pickers
$('.datepicker').datepicker();
$('.timepicker').timepicker({
    showPeriod: true,
    showLeadingZero: true
});

// all day button
function allDay() {
    $('#id_start_time').val('12:00 AM');
    $('#id_end_time').val('11:59 PM');
}

// resource multiselect
$('#id_resources').multiSelect();

// filtering resources by tag
$('#id_tag').change(function() {
    if ($('#id_tag').val()) {
	$("#ms-id_resources .ms-elem-selectable").hide();
	var resources = tagResources[$('#id_tag').val()];
	for (i = 0; i < resources.length; i++)
	{
	    var resource_id = resources[i];
	    $(".ms-selectable #" + resource_id + "-selectable").show();
	    $(".ms-selectable #" + resource_id + "-selectable.ms-selected").hide();
	}
    } else {
	$("#ms-id_resources .ms-elem-selectable").show();
    }
});
