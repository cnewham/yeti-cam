
function updateImage() {
	current = Flask.url_for("upload_folder", {"filename": "current.jpg"});

	newImage = $("#current");
	newImage.attr("src", current + "?" + new Date().getTime());

	$("#currentTime").text('success!');
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
    		status = "<table>";
    		$.each(result, function(key, value) {
    			status += "<tr><td>" + key + "</td><td>" + value + "</td></tr>";
    		});
    		status += "</table>";

    		$("#status").html(status);
		}
	});
}

$(function(){
	updateStatus();

	setInterval(function(){
		updateImage();
		updateStatus();
	}, 10000);

});