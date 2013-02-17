$(function() {
    $("textarea").val('');
    $("#csr").hide().bind('click focus', function() { this.select(); } );
    $("#csrform").submit(function(event) {
        event.preventDefault();
        $("#postgenerate").slideDown("slow");
        $.post("/generate", $(this).serialize(), function(data) {
            $("#csr").val(data).fadeIn("slow");
            $('html, body').animate({
                scrollTop: $("#postgenerate").offset().top
            }, 1500);
        }, "text");
   });
});
