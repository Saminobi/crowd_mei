function sendMEI(app) {
  const http = new XMLHttpRequest();
  const url = 'http://127.0.0.1:5000/';
  const xhr = new XMLHttpRequest();
  // var text = $("app").html();
  const text = app.mei
  console.log(text)
  xhr.open("POST", url, true);
  xhr.setRequestHeader('Content-Type', 'application/xhtml+xml');
  xhr.send(text);
}