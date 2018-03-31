var sunset;

function refreshWeatherData(force, callback) {

  $.ajax({
        type: "GET",
        url: "api/v2/weather",
        dataType: "json",
        error: function (error) {
          showAlert("An error occurred: " + error.status + " " + error.statusText, color=alerts.red);
        },
        success: function (result) {
          sunset = Date.parse(result["conditions"]["astrology"]["sun"]["sunset"]);

          var conditions = $("#conditions-container");
          var forecast = $("#forecast-container");

          if (conditions.length) {
            conditions.loadTemplate($("#conditions-template"), result["conditions"], {append: true});
          }

          if (forecast.length) {
            forecast.loadTemplate($("#forecast-template"), result["forecast"], {append: true});

            $("#forecast-container .precip-indicator").each(function(index) {
                value = parseFloat(this.innerText);
                if (value % 1 === 0) {
                    $(this).prop("hidden", true);
                }
              });
          }

          if (callback) {
            callback();
          }
        }
  });

}

$(function () {

    $.addTemplateFormatter({
        MoonPhaseFormatter : function(value, template) {
                return "age" + Math.floor(parseFloat(value) * 31);
            },
        TempFormatter : function(value, round) {
                temp = parseFloat(value);

                if (round)
                    return Math.round(temp) + "&deg;";
                else
                    return temp + "&deg;";
            },
        SimpleTimeFormatter : function(value, template) {
                return moment(value).format("LT");
            },
        IconFormatter : function(value, showNight) {
                var condition = "wu-" + value;

                if (showNight && Date.now() >= sunset)
                    condition += " wu-night";

                return condition;
            }
    });
});