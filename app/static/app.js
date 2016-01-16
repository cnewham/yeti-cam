
function updateCurrent() {
	current = Flask.url_for("static", {"filename": "current.jpg"});

	newImage = $("#current");
	newImage.attr("src", current + "?" + new Date().getTime());

	$("#currentTime").text('success!');
}


$("#current").click(function(){

	updateCurrent();

});

$(function(){

	setInterval(function(){
		updateCurrent();
	}, 10000);

});

