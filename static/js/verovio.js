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

fetch('')   // The directory here should be passed through a variable
            // Example directory -> ../data/composers/beethoven/adante_f/piano/mei/page1.mei
.then(function(response) {
    return response.text();
})
.then(function(a) {
    app.loadData(a);
    $("#saveButton").click(sendMEI.bind({},app))
})

//var text = readTextFile('/data/composers/pls/ama/ya/mei/page1.mei');
//alert(text);
//app.loadData(text);
//$("#saveButton").click(sendMEI.bind({},app))

//function readTextFile(file)
//{
//    var rawFile = new XMLHttpRequest();
//    rawFile.open("GET", file, false);
//    rawFile.onreadystatechange = function ()
//    {
//        if(rawFile.readyState === 4)
//        {
//            if(rawFile.status === 200 || rawFile.status == 0)
//            {
//                var allText = rawFile.responseText;
//                return allText;
////                  alert(allText);
//            }
//        }
//    }
//    rawFile.send(null);
//}




