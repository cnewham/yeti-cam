function refresh() {
    updateImage();
    updateStatus();
}

function updateImage() {
	current = Flask.url_for("upload_folder", {"name":"primary","filename": "current.jpg"});

	newImage = $("#current");
	newImage.attr("src", current + "?" + new Date().getTime());
}

function toggleOnlineStatus(isOnline) {
    if (isOnline) {
        $("#online-indicator").prop("hidden", false);
        $("#offline-indicator").prop("hidden", true);
    } else {
        $("#online-indicator").prop("hidden", true);
        $("#offline-indicator").prop("hidden", false);
    }
}


function toggleManualCapture(isEnabled) {
    button = $("#manual-capture");
    if (isEnabled) {
        button.removeClass('camera-disabled').addClass('camera-enabled');

        button.unbind('click');
        button.click(function() {
            socket.emit('manual_capture', {});
            toggleManualCapture(false);
        });
    }
    else {
        button.removeClass('camera-enabled').addClass('camera-disabled');
        button.unbind('click');
    }
}

var alerts = {
    red: "alert-red",
    green: "alert-green",
    amber: "alert-amber"
}

function showAlert(message, expire, color) {
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

function updateStatus() {
	$.ajax({
        type: "GET",
        url: "api/status",
        dataType: "json",
        error: function (error) {
        	$("#status").text("An error occured: " + error.status + " " + error.statusText);
        },
        success: function (result) {
    		status = "<table style='width:100%'>";
    		$.each(result, function (key, value) {
                status += "<tr><td>" + key + "</td><td>" + value + "</td></tr>";
    		});
    		status += "</table>";

    		$("#status").html(status);
		}
	});
}

$(function () {
    refresh();

    $(".cam-slider").unslider({arrows:false})

    socket.on('status_update', function (data) {
        updateStatus();
    });

    socket.on('camera_capture', function (data) {
        updateImage();
        toggleManualCapture(true);
    });

    socket.on('manual_capture_result', function (data){
        if (data.result)
            showAlert("Manual capture request successful", 5000, alerts.green);
        else
            showAlert("Manual capture request failed. Camera busy", 5000, alerts.amber);
    });

    socket.on('camera_status', function (data) {
        toggleOnlineStatus(data.connected);
        toggleManualCapture(data.connected);
    });

    socket.on('connect', function () {
        console.log('Socket connected...');
    });
});