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