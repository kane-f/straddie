(function () {
  var initialized = false;

  function update() {
    var hero = document.querySelector("[data-hero-parallax]");
    if (!hero) return;
    var rect = hero.getBoundingClientRect();
    var progress = Math.min(Math.max(-rect.top, 0), rect.height);
    var layers = hero.querySelectorAll(".hero-parallax__layer");
    for (var i = 0; i < layers.length; i++) {
      var depth = parseFloat(layers[i].getAttribute("data-depth")) || 0;
      layers[i].style.transform = "translate3d(0," + progress * depth + "px,0)";
    }
  }

  function bindOnce() {
    if (initialized) return;
    initialized = true;

    var reduceMotion =
      window.matchMedia &&
      window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (reduceMotion) return;

    var ticking = false;
    function onScroll() {
      if (ticking) return;
      ticking = true;
      window.requestAnimationFrame(function () {
        update();
        ticking = false;
      });
    }

    window.addEventListener("scroll", onScroll, { passive: true });
    window.addEventListener("resize", onScroll, { passive: true });
  }

  function init() {
    bindOnce();
    update();
  }

  // Material's instant navigation swaps page content without a full reload,
  // so re-run init on every navigation via its document$ observable.
  // Falls back to a normal DOMContentLoaded if instant navigation is off.
  if (typeof document$ !== "undefined" && document$.subscribe) {
    document$.subscribe(init);
  } else {
    document.addEventListener("DOMContentLoaded", init);
  }
})();
