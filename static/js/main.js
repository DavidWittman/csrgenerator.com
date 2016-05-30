$(function() {
    $(".close").on("click", function() {
        $(this).closest(".modal").removeClass("active");
    });
    $("form").submit(function(e) {
        e.preventDefault();
        $.post("/generate", $(this).serialize(), function(data) {
            $("#csr").val(data);
        }, "text");
        $("#csr-modal").addClass("active");
    });
    $("#csr").on("click focus", function() { this.select() } );
});
