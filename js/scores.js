function addScore() {
  var img = document.createElement("score")
  var source = '/Users/saminobi/Documents/PhD_Work/Projects/Collaborate_MEI/Codebase/collaborate_mei/scores/IMSLP109835-PMLP30951-sibley.1802.1525.beethoven.andante.fmajor.jpg'
  document.body.appendChild(img)
}

function sendMEI(app) {
  var http = new XMLHttpRequest();
  var url = 'http://127.0.0.1:5000/';
  var xhr = new XMLHttpRequest();
  // var text = $("app").html();
  var text = app.mei
  console.log(text)
  xhr.open("POST", url, true);
  xhr.setRequestHeader('Content-Type', 'application/xhtml+xml');
  xhr.send(text);
}