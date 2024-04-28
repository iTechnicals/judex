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

var editor = ace.edit("editor", {
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

var dummyeditor = document.getElementById("editor-dummy");

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

checkValidity();
setInterval(checkValidity, 10000);

