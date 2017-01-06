function init() {

  $.ajax({
        type: "GET",
        url: "api/v2/capture",
        dataType: "json",
        error: function (error) {
          showAlert("An error occurred: " + error.status + " " + error.statusText, color=alerts.red);
        },
        success: function (result) {
          $("#capture-container").loadTemplate($("#capture-template"), result)

          $.each(result, function(idx, data) {
            updateImage(data["name"])
            updateStatus(data["name"])
          });

          $(".cam-slider").unslider({arrows:false,swipe:true})
        }
  });

}

var alerts = {
  red: "alert-red",
  green: "alert-green",
  amber: "alert-amber"
}

function showAlert(message, color, expire) {
  if (message === undefined)
    return;

  if (color === undefined)
    color = "alert-default";

  alert = $("#alert-message");

  alert.text(message);
  alert.removeClass().addClass("alert").addClass(color);

  if (expire === undefined)
    alert.fadeIn(200);
  else
    alert.fadeIn(200).delay(expire).fadeOut(400);

}

$(function () {
  //init();
});