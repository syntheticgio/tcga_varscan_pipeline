/*
 * AJAX Polling
 */


const URL = "http://34.67.6.46:8081"
// const URL = "http://127.0.0.1:8081"

let counts = {}

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
        let self = this;

        let poll = setTimeout(function () {
            $.ajax({
                url: URL + "/progress/",
                success: function (response) {
                    document.getElementById("queued").innerHTML = response["queued"];
                    document.getElementById("processing").innerHTML = response["processing"];
                    document.getElementById("finished").innerHTML = response["finished"];
                    let count_html = "<p>Counts<br/>Verified: " + response["counts"]["phase1-finished"] + "<br/>";
                    count_html += "Finished: " + response["counts"]["finished"] + "<br/>";
                    count_html += "Running: " + response["counts"]["running"] + "<br/>";
                    count_html += "Waiting: " + response["counts"]["waiting_count"] + "<br/>";
                    document.getElementById("metrics").innerHTML = count_html;
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
function NodeStatus(node_ids="all") {
    this.poll = false;
    this.activatePoll = function () {
        this.poll = true;
        this.runPoll();
    };
    this.disablePoll = function () {
        this.poll = false;
    };
    this.runPoll = function () {
        let self = this;

        let poll = setTimeout(function () {
            $.ajax({
                url: URL + "/node_status/",
                success: function (response) {
                    let html_element = "";
                    for (let node_name in response) {
                        html_element += "<div id=\"" + node_name + "\">";
                        html_element += response[node_name]["name"];
                        html_element += response[node_name]["status"];
                        html_element += response[node_name]["jobs_requested"];
                        html_element += response[node_name]["free_mem"];
                        html_element += response[node_name]["cpu_load"];
                        html_element += response[node_name]["real_mem"];
                        html_element += response[node_name]["cores"];
                        html_element += "</div>";
                    }
                    document.getElementById("nodes").innerHTML = html_element;
                },
                dataType: "json",
                data: JSON.stringify({"node_ids": node_ids}),
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
            // TODO: Should have response here where we can update something dynamically
            console.log(response)
        },
        dataType: "json",
        data: JSON.stringify({"tcga_id": tcga_id}),
        type: "post",
        contentType: "application/json; charset=utf-8",
        traditional: true
    })
}


$(document).ready(function () {
    let request = new RequestStatus();
    request.activatePoll();
    let nodes = new NodeStatus();
    nodes.activatePoll();
});
