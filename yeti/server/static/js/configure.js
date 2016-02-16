function getConfig() {
    $.ajax({
        type: "GET",
        url: "api/config",
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

            $("#version_display").text("Current Config Version: " + result["version"]);
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
        url: "api/config",
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
        }
    });
};

function toggleMotionSettings(enabled) {
    var motion_settings = $("#motion_settings input");
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