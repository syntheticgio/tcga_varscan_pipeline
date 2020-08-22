/*
 * AJAX Polling
 */

// let URL = "http://34.67.6.46:8081"
let URL = "http://127.0.0.1:8081"
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
                url: URL + "/progress/",
                success: function (response) {
                    document.getElementById("queued").innerHTML = response["queued"];
                    document.getElementById("processing").innerHTML = response["processing"];
                    document.getElementById("finished").innerHTML = response["finished"];
                    //console.log(response)
                    //console.log(response["results"])
                },
                dataType: "json",
                data: JSON.stringify({"0": "0"}),
                complete: function () {
                    if (self.poll === false) {
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
function SubmitJob(tcga_id) {
    $.ajax({
        url: URL + "/submit_job/",
        success: function (response) {
            // document.getElementById("queued").innerHTML = response["queued"];
            // document.getElementById("information").innerHTML = response["results"];
            console.log(response)
            //console.log(response["results"])
        },
        dataType: "json",
        data: JSON.stringify({"tcga_id": tcga_id}),
        type: "post",
        contentType: "application/json; charset=utf-8",
        traditional: true
    })
}


$(document).ready(function () {
    var request = new RequestStatus();
    request.activatePoll();
});
