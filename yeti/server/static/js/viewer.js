function refresh() {
    updateImage();
    updateStatus();
};

function updateImage() {
	current = Flask.url_for("upload_folder", {"filename": "current.jpg"});

	newImage = $("#current");
	newImage.attr("src", current + "?" + new Date().getTime());
};

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
    		$.each(result, function(key, value) {
    			status += "<tr><td>" + key + "</td><td>" + value + "</td></tr>";
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
});