$('.datepicker').datepicker();

$(document).ready(function() {
    var showTooltip = function(event) {
        $('.event_detail', this).show();
        $('.event_glance', this).hide();
    };

    var hideTooltip = function() {
        $('.event_glance', this).show();
        $('.event_detail', this).hide();
    };

    $(".one_event").bind({
        mouseenter: showTooltip,
        mouseleave: hideTooltip,
    });
});
