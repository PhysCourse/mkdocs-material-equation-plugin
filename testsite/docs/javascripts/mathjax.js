window.MathJax = {
  loader: {load: ['[tex]/cancel','[tex]/physics']},
  tex: {
    inlineMath: [['$','$'],["\\(", "\\)"]],
    displayMath: [['$$','$$'],["\\[", "\\]"]],
    packages: {'[+]': ['cancel','physics']},
    
    tags: 'ams',
    tagSide: 'right',
    useLabelIds: true,
    processEscapes: true,
    processEnvironments: true,
    macros: {
      slashed: ["{#1 \\!\\!\\!/}",1],
      cslashed: ["{#1 \\!\\!\\!\\!/}",1],
      lslashed: ["{#1 \\!\\!/}",1],
    }

  },
  options: {
    ignoreHtmlClass: ".*|",
    processHtmlClass: "arithmatex|md-ellipsis|formula-slide|slide-content"
  }
};

document$.subscribe(() => { 
  MathJax.startup.output.clearCache()
  MathJax.typesetClear()
  MathJax.texReset()
  MathJax.typesetPromise()
  console.log("render event")
})

/* kludge (костыль) to work mathjax with data-preview */
let rendering = false;
new MutationObserver((mutations) => {
  if (rendering || !window.MathJax?.typesetPromise) return;
  
  for (let mutation of mutations) {
    for (let node of mutation.addedNodes) {
      if (node.nodeType === 1 /*&& node.querySelector?.('.arithmatex')*/) {
        rendering = true;
        MathJax.typesetPromise().finally(() => rendering = false);
        return;
      }
    }
  }
}).observe(document.body, {childList: true, subtree: true});