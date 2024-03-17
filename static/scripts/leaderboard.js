let admin = false;

$.getJSON({
    url: "/auth",
    success: function(data) {
        if (data == 1) {
            admin = true;
        }
    }
});

function updateLeaderboard() {
    $.getJSON({
        url: "/get_scores",
        success: function(data){
            let scorearr = [];
            for (const key in data) {
                scorearr.push([key, data[key][0], data[key][1]]);
            }

            scorearr.sort(function(x, y) {
                return y[2] - x[2];
            });

            let htmldata = "";
            scorearr.forEach(function(item) {
                htmldata += `
                    <div class="grid-item">
                `
                if (admin) {
                    htmldata += `
                        <form method="POST" style="display: inline;">
                            <input type="submit" name="${item[0]}" value="x">
                        </form>
                    `
                }
                htmldata += `${item[0]}
                    </div>
                    <div class="grid-item right-grid-item">
                        ${item[1]}
                    </div>
                    <div class="grid-item right-grid-item">
                        ${item[2]}
                    </div>
                `
            });

            $("#leaderboard").html(htmldata);
        }
    });
}

updateLeaderboard();
setInterval(updateLeaderboard, 10000);