listOfFiles = [];
function addFile(filePath) {
    if (listOfFiles.indexOf(filePath) >= 0) {
        return;
    }

    listOfFiles.push(filePath);
    document.getElementById("emittedScript").innerHTML = listOfFiles.reduce((accum, file) => accum + `del "${file}"<br />`, "");
}
