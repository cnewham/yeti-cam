function refreshWeatherData(force) {

  $.ajax({
        type: "GET",
        url: "api/v2/weather",
        data: {"force":force},
        dataType: "json",
        error: function (error) {
          showAlert("An error occurred: " + error.status + " " + error.statusText, color=alerts.red);
        },
        success: function (result) {
          $("#conditions-container").loadTemplate($("#conditions-template"), result["conditions"], {append: true});
          $("#forecast-container").loadTemplate($("#forecast-template"), result["forecast"], {append: true});

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

$.addTemplateFormatter({
    MoonPhaseFormatter : function(value, template) {
            return "age" + Math.floor(parseFloat(value) * 31)
        },
    TempFormatter : function(value, template) {
            return value + "&deg;"
        },
});

  refreshWeatherData(false)
});