(function () {
  var button = document.getElementById("copy-bibtex");
  var block = document.getElementById("bibtex-content");
  if (!button || !block) return;
  button.addEventListener("click", function () {
    navigator.clipboard.writeText(block.textContent).then(function () {
      button.textContent = "Copied";
      setTimeout(function () {
        button.textContent = "Copy BibTeX";
      }, 1800);
    });
  });
})();
