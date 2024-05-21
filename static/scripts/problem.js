let curr_time;

let code = {
    "python": `# Code goes here!`,
    "cpp": `// Include standard library
#include <bits/stdc++.h>

using namespace std;

int main() {
    // Code goes here!

    return 0;
}`
};

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

function pad(n) {
    return (n < 10) ? ("0" + n) : n;
}

function updateTimer() {
    // var hours = Math.floor(curr_time / 3600); all events expected to be less than 1 hour
    let minutes = Math.floor((curr_time % 3600) / 60);
    let seconds = curr_time % 60;
    document.getElementById('timer').textContent = pad(minutes) + ":" + pad(seconds);
    curr_time--;
}

let editor = ace.edit("editor", {
    theme: "ace/theme/cobalt",
    mode: "ace/mode/python",
    minLines: 20,
    maxLines: 30
});

// NOTE: we don't save other language solutions if the code is actually submitted
function updateLanguage(id, oldId) {
    let mode = (id === "c" || id === "cpp") ? "c_cpp" : id;
    editor.session.setMode("ace/mode/" + mode);

    if (editor.getValue() !== "") code[oldId] = editor.getValue();
    editor.setValue(code[id], -1);
}

let dummyeditor = document.getElementById("editor-dummy");

$.getJSON({
    url: "/get_time",
    async: false,
    success: function(data){
        curr_time = data;
    }
});

dummyeditor.value = editor.getValue();
editor.getSession().on("change", function () {
    dummyeditor.value = editor.getValue();
});

selector.oldValue = selector.value;
updateLanguage(selector.value, selector.oldValue);
selector.addEventListener("change", (e) => {
    updateLanguage(selector.value, selector.oldValue);
    selector.oldValue = selector.value;
});

document.addEventListener('keydown', function (event) {
    if (event.ctrlKey && event.key === 'Enter') {
        document.getElementById('submit').click();
    }
});

checkValidity();
updateTimer();
setInterval(checkValidity, 10000);
setInterval(updateTimer, 1000);


const submitButton = document.getElementById("submit");
document.addEventListener("keydown", (event) => {
    if (event.ctrlKey && event.key.toLowerCase() === "enter") {
        event.preventDefault();
        submitButton.click();
    }
});

