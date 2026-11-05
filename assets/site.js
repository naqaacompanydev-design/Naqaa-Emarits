/* Quick quote: builds a WhatsApp message from the form. No data is stored or sent anywhere else. */
document.querySelectorAll("form.quote").forEach(function (form) {
  form.addEventListener("submit", function (e) {
    e.preventDefault();
    var ar = document.documentElement.lang === "ar";
    var pick = function (name) {
      var el = form.querySelector('[name="' + name + '"]:checked') || form.querySelector('[name="' + name + '"]');
      if (!el) return "";
      return el.tagName === "SELECT" ? el.options[el.selectedIndex].text : (el.dataset.label || el.value);
    };
    var parts = [pick("service"), pick("size"), pick("emirate")].filter(Boolean);
    var area = form.querySelector('[name="area"]');
    if (area && area.value.trim()) parts.push(area.value.trim());
    var msg = (ar ? "مرحبا نقاء، أريد عرض سعر: " : "Hi Naqaa, I'd like a price for: ") + parts.join(ar ? "، " : ", ");
    window.open("https://wa.me/" + form.dataset.wa + "?text=" + encodeURIComponent(msg), "_blank", "noopener");
  });
});
