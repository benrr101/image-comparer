listOfFiles = [];

function drawScript() {
    document.getElementById("emittedScript").innerHTML = listOfFiles.reduce(
        (accum, file) => accum + `del "${file}"<br />`,
        "");
}

function drawButton(original, label, action, filePath) {
    let newButton = document.createElement("button");
    newButton.innerText = label;
    newButton.onclick = () => action(filePath, newButton);

    original.parentNode.insertBefore(newButton, original);
    original.parentNode.removeChild(original);
}

function addFile(filePath, node) {
    if (listOfFiles.indexOf(filePath) >= 0) {
        return;
    }

    listOfFiles.push(filePath);
    drawScript();
    drawButton(node, "Don't Delete", removeFile, filePath);
}

function removeFile(filePath, node) {
    let index = listOfFiles.indexOf(filePath);
    if (index < 0) {
        return;
    }

    listOfFiles.splice(index, 1);
    drawScript();
    drawButton(node, "Delete", addFile, filePath);
}
