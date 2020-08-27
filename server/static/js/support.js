
// (function() {
//   var status = $('.status'),
//     poll = function() {
//       $.ajax({
//         url: '/video/',
//         dataType: 'json',
//         type: 'POST',
//         // data: JSON.stringify({"val":"test"}),
//         success: function(return_data) { // check if available
//             if(return_data['new_frame']) {
//                 let frame = "static/img/" + return_data['frame']
//                 $("#annotations").attr("src", frame)
//             }
//         },
//         error: function() { // error logging
//           console.log('Error!');
//         }
//       });
//     },
//     pollInterval = setInterval(function() { // run function every 2000 ms
//       poll();
//       }, 2000);
//     poll(); // also run function on init
// })();


function videoPoll(){
    poll = function() {
      $.ajax({
        url: '/video/',
        dataType: 'json',
        type: 'POST',
        // data: JSON.stringify({"val":"test"}),
        success: function(return_data) { // check if available
            if(return_data['new_frame']) {
                let frame = "static/img/" + return_data['frame']
                $("#annotations").attr("src", frame)
            }
        },
        error: function() { // error logging
          console.log('Error!');
        }
      });
    };
    pollInterval = setInterval(function() { // run function every 2000 ms
      poll();
      }, 10000);
    poll(); // also run function on init
}

function statsPoll(){
    poll = function() {
      $.ajax({
        url: '/stats/',
        dataType: 'json',
        type: 'POST',
        // data: JSON.stringify({"val":"test"}),
        success: function(return_data) { // check if available
            if(return_data['status'] === 'ok') {
                $("#fps_value").attr("value", return_data["fps"]);
                $("#det_time_value").attr("value", return_data["det_time"]);
                $("#track_time_value").attr("value", return_data["track_time"]);
                $("#proc_frames_value").attr("value", return_data["processed_frames"]);
                $("#skipped_frames_value").attr("value", return_data["skipped_frames"]);
                 $("#false_pos_detector").attr("value", return_data["det_fpr"]);
                $("#false_neg_detector").attr("value", return_data["det_fnr"]);
                 $("#false_positives_tracker").attr("value", return_data["track_fpr"]);
                $("#false_negatives_tracker").attr("value", return_data["track_fnr"]);

            }
        },
        error: function() { // error logging
          console.log('Error!');
        }
      });
    };
    pollInterval = setInterval(function() { // run function every 2000 ms
      poll();
      }, 1000);
    poll(); // also run function on init
}

statsPoll();
