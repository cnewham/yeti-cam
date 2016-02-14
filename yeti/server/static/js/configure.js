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
                    $("#" + key).attr("checked", value);
                } else {
                    $("#" + key).attr("value", value);
                }
            });
        }
    });
};

function saveConfig(config) {
    if (!config) {
        //throw error
        return;
    }

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
            $("#success-message").show().fadeOut(5000);
            getConfig();
        }
    });
};

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
});