/* ============================================================
   LMS App — Theme persistence
   - Respects the OS/browser color scheme by default.
   - Remembers the user's manual choice (localStorage), so it
     stays the same across every page and future visits.
   - Injects a floating toggle button automatically — no HTML
     needed on any page.
   Note: the tiny inline snippet in <head> (see instructions)
   already sets the theme before the page paints, so there's
   no flash of the wrong theme. This file just wires up the
   toggle button.
   ============================================================ */

(function () {
  var STORAGE_KEY = "lms-theme";

  function getStoredTheme() {
    try { return localStorage.getItem(STORAGE_KEY); } catch (e) { return null; }
  }

  function storeTheme(theme) {
    try { localStorage.setItem(STORAGE_KEY, theme); } catch (e) {}
  }

  function systemPrefersDark() {
    return window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches;
  }

  function applyTheme(theme) {
    document.documentElement.setAttribute("data-theme", theme);
    var btn = document.getElementById("theme-toggle");
    if (btn) btn.textContent = theme === "dark" ? "☀️" : "🌙";
  }

  function currentTheme() {
    return document.documentElement.getAttribute("data-theme") ||
      (systemPrefersDark() ? "dark" : "light");
  }

  function toggleTheme() {
    var next = currentTheme() === "dark" ? "light" : "dark";
    storeTheme(next);
    applyTheme(next);
  }

  function injectToggleButton() {
    if (document.getElementById("theme-toggle")) return;
    var btn = document.createElement("button");
    btn.id = "theme-toggle";
    btn.type = "button";
    btn.title = "Toggle light / dark theme";
    btn.setAttribute("aria-label", "Toggle color theme");
    btn.textContent = currentTheme() === "dark" ? "☀️" : "🌙";
    btn.addEventListener("click", toggleTheme);
    document.body.appendChild(btn);
  }

  // Keep in sync if the OS theme changes AND the user hasn't manually chosen one.
  if (window.matchMedia) {
    window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", function (e) {
      if (!getStoredTheme()) applyTheme(e.matches ? "dark" : "light");
    });
  }

  document.addEventListener("DOMContentLoaded", function () {
    applyTheme(currentTheme());
    injectToggleButton();
  });
})();
