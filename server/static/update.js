/*
 * AJAX Polling
 */

function RequestStatus() {
    this.poll = false;
    this.activatePoll = function () {
        this.poll = true;
        this.runPoll();
    };
    this.disablePoll = function () {
        this.poll = false;
    };
    this.runPoll = function () {
        var self = this;

        var poll = setTimeout(function () {
            $.ajax({
                url: 'http://127.0.0.1/progress/',
                success: function (response) {
                    document.getElementById("information").innerHTML = response["results"];
                    //console.log(response)
                    //console.log(response["results"])
                },
                dataType: "json",
                data: JSON.stringify({"0": "0"}),
                complete: function () {
                    if (self.poll == false) {
                        clearTimeout(poll);
                    } else {
                        self.runPoll();
                    }
                },
                type: "post",
                contentType: "application/json; charset=utf-8",
                traditional: true
            })
        }, 1000);

    };
}


$(document).ready(function () {
    var request = new RequestStatus();
    request.activatePoll();
});
