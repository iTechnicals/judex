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
            scorearr.forEach(([username, problems, score]) => {
                htmldata += `
                    <div class="grid-item">
                `;
                if (admin) {
                    htmldata += `
                        <form method="POST" style="display: inline;">
                            <input type="submit" name="${username}" value="x">
                        </form>
                    `;
                }
                htmldata += `${username}
                    </div>
                    <div class="grid-item right-grid-item">
                        ${problems}
                    </div>
                    <div class="grid-item right-grid-item">
                        ${score}
                    </div>
                `;
            });

            $("#leaderboard").html(htmldata);
        }
    });
}

updateLeaderboard();
setInterval(updateLeaderboard, 10000);