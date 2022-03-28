requirejs([
    'jquery',
    'base/js/utils',
], function($, utils) {
    utils.change_favicon("custom/favicon.ico")

    $.getJSON("{base_url}/api/2.0/rents/service/status/{uuid}", function(data) {
        var countDownDate = new Date().getTime() + data.result.timeToEnd * 1000;
        var tariff = data.result.tariffName;

        if (tariff == "dynamic") {
            $('<span class="save_widget">Tariff: dynamic</span>').insertAfter(jQuery("#ipython_notebook"));
        } else {
            $('<span class="save_widget">Time left:&nbsp;<span id="timer" class="checkpoint_status"></span></span>').insertAfter(jQuery("#ipython_notebook"));
            var x = setInterval(function() {
                var now = new Date().getTime();
                var diff = countDownDate - now;
                var days = Math.floor(diff / (1000 * 60 * 60 * 24));
                var hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
                var minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
                var seconds = Math.floor((diff % (1000 * 60)) / 1000);
                if (days) {
                    document.getElementById("timer").innerHTML = days + "d " + hours + "h " + minutes + "m " + seconds + "s ";
                } else if (hours) {
                    document.getElementById("timer").innerHTML = hours + "h " + minutes + "m " + seconds + "s ";
                } else {
                    document.getElementById("timer").innerHTML = minutes + "m " + seconds + "s ";
                }

                if (diff <= 0) {
                    clearInterval(x);
                    document.getElementById("timer").innerHTML = "EXPIRED";
                }
        }, 1000);
        }
    });
});