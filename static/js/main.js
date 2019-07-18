

$(function() {

    $(".close").on("click", function() {
        $(this).closest(".modal").removeClass("active");
    });


    $("#csr-form").submit(function(e) {
        e.preventDefault();
        $.post("/generate", $(this).serialize(), function(data) {
            $("#csr").val(data);
        }, "text");
        $("#csr-modal").addClass("active");
    });

    $("#csr").on("click focus", function() { this.select() } );

    let endpoint = "https://rdap.afrinic.net/rdap/entity/";
    let orgId = $("#org-id");
    let nicIds;

    orgId.on("change", function () {
         $.getJSON(endpoint + orgId.val(),function(data) {
            console.log(endpoint+orgId.val());
            console.info(data.entities[0]["vcardArray"][1][5][3]);
             nicIds = data.entities;
            let select = document.querySelector("select");


            for (let nicId in nicIds) {
                let option = document.createElement("option");
                console.log(nicIds[nicId]);
                let textValue = nicIds[nicId].handle;
                option.value = textValue;
                option.innerText = textValue;
                select.append(option);
            }

        }).fail(function () {
            alert("Enter a valid Org Handle");
        })

    });

    let nicHandle = $("#nic-id");

    nicHandle.on("change",showForm);



    function showForm() {

            fillForm(nicIds);
            let csrForm = $("#csr-form");

            if (csrForm.css("display") === "none") {
                csrForm.css("display", "block");
            }


    }

    function fillForm(nicIds) {
        let nicId = $("#nic-id").val();
        let address = [];
        let roles =[];
        let orgUnit = "";


        for (let counter in nicIds){
            if(nicIds[counter].handle === nicId){
                let selectedNic = nicIds[counter];
                roles = selectedNic.roles;
                address = selectedNic["vcardArray"][1][5][3];
                //console.log(address);
            }
        }

        if(roles.length > 1){

            for(let i in roles){

                if(i < roles.length -1){
                    orgUnit += roles[i] + ",";
                }
                else {
                    orgUnit += roles[i];
                }
            }

        }

        else {
            orgUnit = roles[0];
        }

        //$("#country").val(address[2]);
        //$("#locality").val(address[1]);
        $("#org-unit").val(orgUnit);
        $("#common-name").val(nicId);
        $("#org").val($("#org-id").val());
    }


});






