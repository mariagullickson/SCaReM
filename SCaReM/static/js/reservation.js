// date & time pickers
$('.datepicker').datepicker();
$('.timepicker').timepicker({
    showPeriod: true,
    showLeadingZero: true
});

// filtering resources by tag
$('#id_tag').change(function() {
    if ($('#id_tag').val()) {
	$("#id_resources option").hide();
	var resources = tagResources[$('#id_tag').val()];
	for (i = 0; i < resources.length; i++)
	{
	    var resource_id = resources[i];
	    $('#id_resources option[value=' + resource_id + ']').show();
	}
    } else {
	$("#id_resources option").show();
    }
});
