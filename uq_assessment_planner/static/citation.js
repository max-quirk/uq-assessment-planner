function copyCitation() {
  console.log(123)
  var citation = document.getElementById("citation");
  citation.select();
  document.execCommand("Copy");
  alert("Copied!");
}