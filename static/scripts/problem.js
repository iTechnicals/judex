function checkValidity() {
    $.getJSON({
        url: "/get_valid_username",
        success: function(data){
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

var dummyeditor = document.getElementById("editor-dummy");

var editor = ace.edit("editor", {
    theme: "ace/theme/cobalt",
    mode: "ace/mode/python",
    minLines: 20,
    maxLines: 30
});

dummyeditor.value = editor.getValue();

editor.getSession().on("change", function () {
    dummyeditor.value = editor.getValue();
});

selector.addEventListener("change", (e) => {
    let mode = (e.target.value === "cpp" || e.target.value === "c") ? "c_cpp" : e.target.value;
    editor.session.setMode("ace/mode/" + mode);
});

checkValidity();
setInterval(checkValidity, 10000);

