import 'https://www.verovio.org/javascript/app/verovio-app.js';
import 'https://ajax.googleapis.com/ajax/libs/jquery/3.3.1/jquery.min.js'

const options = {
    defaultView: 'editor', // default is 'responsive', alternative is 'document'
    defaultZoom: 3, // 0-7, default is 4
    enableResponsive: false, // default is true
    enableDocument: false, // default is true
    enableEditor: true
};
// Create the app - here with an empty option object
const app = new Verovio.App(document.getElementById("app"), options);

// Load a file (MEI or MusicXML)
fetch("data/mei/measure_annotations.mei")
.then(function(response) {
    return response.text();
})
.then(function(text) {
    app.loadData(text);
    $("#saveButton").click(sendMEI.bind({},app))
})

