function updateStatus(status) {
    var statusText = $("#config_status");
    var red = $("#indicator-red");
    var yellow = $("#indicator-yellow");
    var green = $("#indicator-green");

    switch (status) {
        case "MODIFIED":
            yellow.show();
            red.hide();
            green.hide();
            statusText.text("Pending camera");
            break;
        case "UPDATED":
            yellow.hide();
            red.hide();
            green.show();
            statusText.text("Camera updated");
            break;
        default:
            yellow.hide();
            red.show();
            green.hide();
            statusText.text("Camera config status unavailable. Current server config version: " + result["version"]);
            break;
    }
}

function getConfig() {
    $.ajax({
        type: "GET",
        url: "/api/v2/config/" + name,
        dataType: "json",
        error: function (error) {
            $("#status").text("An error occured: " + error.status + " " + error.statusText);
        },
        success: function (result) {
            $.each(result, function (key, value) {
                if (!isNumber(value) && (value == true || value == false)) {
                    $("#" + key).prop("checked", value);
                } else {
                    $("#" + key).prop("value", value);
                }
            });

            updateStatus(result["status"])
            toggleMotionSettings(result["motion_enabled"]);
        }
    });
};

function saveConfig(config) {
    if (!config) {
        //throw error
        return;
    }

    $("#config input[type=submit]").prop("disabled", true);

    var version = parseInt(config["version"]);
    config["version"] = version + 1;

    $.ajax({
        type: "PUT",
        url: "/api/v2/config/" + name,
        contentType: "application/json",
        data: JSON.stringify(config),
        error: function (error) {
            $("#error-message").text("An error occured: " + error.status + " " + error.statusText + " " + error.responseText);
            $("#error-message").show().fadeOut(5000);
        },
        success: function (result) {
            $("#success-message").text("Config queued for delivery");
            $("#success-message").show().fadeOut(5000);
        },
        complete: function() {
            getConfig();
            $("#config input[type=submit]").prop("disabled", false);

            socket.emit("config_update", {"name": name, "version":config["version"]})
        }
    });
};

function toggleMotionSettings(enabled) {
    var motion_settings = $("#motion_settings input, #motion_settings select");
    if (enabled) {
        motion_settings.removeClass("disabled");
        motion_settings.prop("disabled", false);
    } else {
        motion_settings.addClass("disabled");
        motion_settings.prop("disabled", true);
    }
}

function isNumber(n) {
    return !isNaN(parseFloat(n)) && isFinite(n);
};

$(function () {
    socket.on('connect', function () {
        console.log('Socket connected...');
    });

    socket.on('config_updated', function(data) {
        updateStatus(data.status);
    });

    getConfig();

    $("#config").submit(function (e) {

        var values = {};

        $.each($(this).serializeArray(), function (i, field) {
            if (isNumber(field.value))
                values[field.name] = parseInt(field.value);
            else
                values[field.name] = field.value;
        });

        $.each($('#config input[type=checkbox]'), function (i, field) {
            values[field.name] = field.checked;
        });

        e.preventDefault();
        saveConfig(values);
    });

    $("#motion_enabled[type=checkbox]").change(function() {
        toggleMotionSettings(this.checked);
    });
});