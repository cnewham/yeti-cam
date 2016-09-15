var socket = io.connect('http://' + document.domain + ':5001');

function refresh() {
    updateImage();
    updateStatus();
};

function updateImage() {
	current = Flask.url_for("upload_folder", {"filename": "current.jpg"});

	newImage = $("#current");
	newImage.attr("src", current + "?" + new Date().getTime());
};

function toggleOnlineStatus(isOnline) {
    if (isOnline) {
        $("#online-indicator").prop("hidden", false);
        $("#offline-indicator").prop("hidden", true);
    } else {
        $("#online-indicator").prop("hidden", true);
        $("#offline-indicator").prop("hidden", false);
    }
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
    		    if (key == "online") {
		            toggleOnlineStatus(value);
		        } else {
    		        status += "<tr><td>" + key + "</td><td>" + value + "</td></tr>";
		        }
    		});
    		status += "</table>";

    		$("#status").html(status);
		}
	});
};

$(function () {
    refresh();

    setInterval(function () {
        refresh();
    }, 10000);

    socket.on('connect', function () {
        socket.emit('test', { data: 'I\'m connected!' });
    });
});