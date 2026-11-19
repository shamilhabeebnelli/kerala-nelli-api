/* denelli-api docs page: loads the manifest and shows live samples. */
(function () {
  "use strict";
  var BASE = "api/v1/";

  function trimSample(obj) {
    var copy = JSON.parse(JSON.stringify(obj));
    if (copy.data) {
      if (Array.isArray(copy.data)) {
        copy.data = copy.data.slice(0, 2).concat(["..."]);
      } else if (copy.data.rates) {
        var keys = Object.keys(copy.data.rates).slice(0, 5);
        var r = {};
        keys.forEach(function (k) { r[k] = copy.data.rates[k]; });
        r["..."] = "..." ;
        copy.data.rates = r;
      }
    }
    return JSON.stringify(copy, null, 1);
  }

  function loadEndpoint(path) {
    return fetch(BASE + path + ".json", { cache: "no-store" }).then(function (r) {
      if (!r.ok) throw new Error("http " + r.status);
      return r.json();
    });
  }

  function fillPills(manifest) {
    var pills = document.querySelectorAll("[data-pill]");
    pills.forEach(function (p) {
      var path = p.getAttribute("data-pill");
      var info = manifest && manifest.endpoints ? manifest.endpoints[path] : null;
      if (!info) { p.textContent = "building"; p.classList.add("stale"); return; }
      p.textContent = info.status === "ok" ? "live · " + info.count + " items" : "stale data";
      if (info.status !== "ok") p.classList.add("stale");
    });
    var live = document.getElementById("dnl-live");
    if (manifest && manifest.generated_at) {
      live.classList.add("on");
      live.innerHTML = '<span class="hbn-dot"></span>updated ' + manifest.generated_at;
    }
    var built = document.getElementById("dnl-built");
    if (manifest && manifest.generated_at) {
      built.textContent = "Last build: " + manifest.generated_at +
        " · rebuilds every 6 hours via GitHub Actions · manifest: /api/v1/index.json";
    }
  }

  function fillSamples() {
    var blocks = document.querySelectorAll("[data-sample]");
    blocks.forEach(function (b) {
      var path = b.getAttribute("data-sample");
      loadEndpoint(path).then(function (json) {
        b.textContent = trimSample(json);
      }).catch(function () {
        b.textContent = "first build still running — check back in a minute";
      });
    });
  }

  function wireCopy() {
    document.querySelectorAll("[data-copy]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        var txt = btn.getAttribute("data-copy");
        function done() {
          btn.textContent = "copied";
          btn.classList.add("copied");
          setTimeout(function () { btn.textContent = "copy"; btn.classList.remove("copied"); }, 1400);
        }
        if (navigator.clipboard && navigator.clipboard.writeText) {
          navigator.clipboard.writeText(txt).then(done, done);
        } else {
          var ta = document.createElement("textarea");
          ta.value = txt; document.body.appendChild(ta); ta.select();
          try { document.execCommand("copy"); } catch (e) {}
          document.body.removeChild(ta); done();
        }
      });
    });
  }

  fetch(BASE + "index.json", { cache: "no-store" })
    .then(function (r) { return r.ok ? r.json() : null; })
    .then(fillPills)
    .catch(function () { fillPills(null); });
  fillSamples();
  wireCopy();
})();
