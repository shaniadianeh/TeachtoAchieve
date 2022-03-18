// Teacher/Student dropdown on register page
function select() {
  var x = document.getElementById("select-drop").value;
  var y = document.getElementById("hide-student");
  console.log(x);
  if (x == "student") {
    y.style.display = "block";
  } else {
    y.style.display = "none";
  }
}
