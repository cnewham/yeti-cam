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
          sunset = Date.parse(result["current"]["astrology"]["sun"]["sunset"]);

          var conditions = $("#conditions-container");
          var forecast = $("#forecast-container");
          var alerts = $("#alerts-container");

          if (conditions.length) {
            conditions.loadTemplate($("#conditions-template"), result["current"], {append: true});
          }

          if (forecast.length) {
            forecast.loadTemplate($("#forecast-template"), result["forecast"], {append: true});
          }

          if (alerts.length) {
            alerts.loadTemplate($("#alerts-template"), result["alerts"], {append: true});
          }

          if (callback) {
            callback();
          }
        }
  });

}

$(function () {

    $.addTemplateFormatter({
        MoonPhaseFormatter : function(value) {
            return "age" + Math.floor(parseFloat(value) * 31);
        },
        TempFormatter : function(value, round) {
            temp = parseFloat(value);

            if (round)
                return Math.round(temp) + "&deg;";
            else
                return temp + "&deg;";
        },
        PercentageFormatter : function(value) {
            return Math.round(parseFloat(value) * 100) + "%";
        },
        SimpleTimeFormatter : function(value) {
            return moment(value).format("LT");
        },
        WeekdayFormatter : function(value) {
            return moment(value).format("dddd")
        },
        PrecipitationIconFormatter: function(value) {
            if (value === "snow") {
                return "wu-icon snow";
            } else if (value === "rain") {
                return "wu-icon wet";
            } else {
                return "";
            }
        },
        PrecipitationFormatter: function(value) {
            var val = parseFloat(value);

            if (val > 0) {
                return val.toFixed(2);
            } else {
                return ""
            }
        },
        IconFormatter : function(value, showNight) {
            var condition = value;

            if (showNight && Date.now() >= sunset)
                condition += " wu-night";

            return condition;
        },
        AlertFormatter: function(value) {

            if (value === "advisory") {
                return "alert-default"
            }
            else if (value === "watch") {
                return "alert-amber";
            } else if (value === "warning") {
                return "alert-red";
            } else {
                return "";
            }
        }
    });
});