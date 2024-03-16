var dummyeditor = document.getElementById("editor-dummy")

var editor = ace.edit("editor", {
    theme: 'ace/theme/cobalt',
    mode: 'ace/mode/python'
});

editor.getSession().on("change", function () {
    dummyeditor.value = editor.getValue();
});