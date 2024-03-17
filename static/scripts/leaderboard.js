let latestData = {};

function updateLeaderboard() {
    $.getJSON({
        url: "/get_scores",
        success: function(data, textStatus, xhr){
            let htmldata = "";
            for (const key in data) {
                htmldata += `
                    <div class="grid-item">
                        ${key}
                    </div>
                    <div class="grid-item right-grid-item">
                        ${data[key][0]}
                    </div>
                    <div class="grid-item right-grid-item">
                        ${data[key][1]}
                    </div>
                `
            }
            $("#leaderboard").html(htmldata);
        }
    });
}

updateLeaderboard();
setInterval(updateLeaderboard, 10000);