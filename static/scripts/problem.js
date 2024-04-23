function checkValidity() {
    $.getJSON({
        url: "/get_valid_username",
        success: function(data){
            console.log(data);
            switch (data) {
                case 1:
                    window.location.replace(homepageURL);
                    break;
                case 2:
                    window.location.replace(leaderboardURL);
            }
        }
    });
}

checkValidity();
setInterval(checkValidity, 10000);

var dummyeditor = document.getElementById("editor-dummy")

var editor = ace.edit("editor", {
    theme: 'ace/theme/cobalt',
    mode: 'ace/mode/python',
    minLines: 20,
    maxLines: 30
});

dummyeditor.value = editor.getValue();

editor.getSession().on("change", function () {
    dummyeditor.value = editor.getValue();
});