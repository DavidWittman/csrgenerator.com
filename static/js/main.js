
$(function() {

    $(".close").on("click", function() {
        $(this).closest(".modal").removeClass("active");
    });

   $("#csr-form").submit(function (e) {
       e.preventDefault();
       $("#csr-modal").addClass("active");

       $.post("/generate", $(this).serialize())
           .done(function (data) {
               console.log(data);
               $("html").html(data);
           })
           .fail(function (data) {
               console.log(data.responseText);
               $("html").html(data.responseText);
           })

   });

    let endpoint = "https://rdap.afrinic.net/rdap/entity/";
    let orgId = $("#org-id");
    let nicIds;

    orgId.on("change", function () {
           $.getJSON(endpoint + orgId.val(),function(data) {
              // console.log(endpoint+orgId.val());
              // console.info(data.entities[0]["vcardArray"][1][5][3]);
               nicIds = data.entities;
              let select = document.querySelector("datalist");


        //nicIds = ["IS001-AFRINIC","ATU1-AFRINIC"];
        // console.log(nicIds);
        for (let nicId in nicIds) {
            console.log(nicId);
            // let option = document.createElement("option");
            // let textValue = nicIds[nic_id];
            // option.value = textValue;
            // option.innerText = textValue;
            // select.append(option);

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
            //let address = [];
            let roles = [];
            let orgUnit = "";


            for (let counter in nicIds) {
                if (nicIds[counter].handle === nicId) {
                    let selectedNic = nicIds[counter];
                    roles = selectedNic.roles;
                    //address = selectedNic["vcardArray"][1][5][3];
                    //console.log(address);
                }
            }


            if (roles.length > 1) {

                for (let i in roles) {

                    if (i < roles.length - 1) {
                        orgUnit += roles[i] + ",";
                    } else {
                        orgUnit += roles[i];
                    }
                }

            } else {
                orgUnit = roles[0];
            }

            //$("#country").val(address[2]);
            //$("#locality").val(address[1]);
            $("#org-unit").val(orgUnit);
            $("#common-name").val(nicId);
            $("#org").val($("#org-id").val());
        }

});