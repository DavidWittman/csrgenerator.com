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

    let endpoint = "https://rdap.afrinic.net/rdap/entity/"
//var orgId = document.querySelector("#org-id")
    let orgId = $("#org-id")

    orgId.on("change", function () {
        let data =  $.getJSON(endpoint + orgId.val(),function(data) {
            console.log(endpoint+orgId.val())
            let nicIds = data.entities;
            let select = document.querySelector("select");
            for (let nicId in nicIds) {
                let option = document.createElement("option");
                let textValue = nicIds[nicId].handle
                option.value = textValue;
                option.innerText = textValue;
                select.append(option);
            }

        }).fail(function () {
            alert("Enter a valid Org Handle")
        })

    })

    let nicHandle = $("#nic-id")

    nicHandle.on("change",function () {
        let csrForm = $("#csr-form");

        if(csrForm.css("display") === "none"){
            csrForm.css("display", "block");
        }

    })



});





