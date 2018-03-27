function updateStatus(name) {
  $.ajax({
    type: "GET",
    url: "api/v2/status/" + name,
    dataType: "json",
    error: function (error) {
      showAlert("An error occurred: " + error.status + " " + error.statusText, color=alerts.red);
    },
    success: function (result) {
      status = "<table style='width:100%'>";
      $.each(result, function (key, value) {
        status += "<tr><td>" + key + "</td><td>" + value + "</td></tr>";
      });
      status += "</table>";

      elem = $("#" + name + " .status")
      elem.html(status);
    }
  });
}

function updateImage(name) {
  current = Flask.url_for("upload_folder", {"name":name,"filename": "current.jpg"});

  newImage = $("#" + name + " .capture");
  newImage.attr("src", current + "?" + new Date().getTime());
}

function toggleOnlineStatus(cam) {
  if (cam.connected) {
    $("#" + cam.name + " .online").prop("hidden", false);
    $("#" + cam.name + " .offline").prop("hidden", true);
  } else {
    $("#" + cam.name + " .online").prop("hidden", true);
    $("#" + cam.name + " .offline").prop("hidden", false);
  }
}

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
          })

          $("#capture-container").dragend({});
        }
  });

   refreshWeatherData(false)
}

$(function () {

  socket.on('status_update', function (cam) {
    updateStatus(cam.name);
  });

  socket.on('camera_capture', function (cam) {
    updateImage(cam.name);
  });

  socket.on('camera_status', function (cams) {
    console.log(cams);

    $.each(cams, function(idx, cam) {
        toggleOnlineStatus(cam);
    });
  });

  socket.on('connect', function () {
    console.log('Socket connected...');
  });

  $.addTemplateFormatter({
    ConfigUrlFormatter : function(value, template) {
            return Flask.url_for("configure", { "name":value });
        }
  });

    init();
});

$(window).on("load", function() {
    $("#loading").hide();
});