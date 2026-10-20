/*
 * helpers.js — أدوات مشتركة بين كل صفحات لوحة الإدارة. يُحمَّل من base.html قبل أي ملف آخر.
 *
 * كل صفحة لها مكوّن Alpine واحد (مثال: dashboardPage) مبني من أجزاء قابلة لإعادة الاستخدام:
 *   pageHelpers()      هذا الملف            — دوال مساعدة عامة
 *   grantCards()       grant_cards.js       — كروت المنحة (تفاصيل / أصناف / مستفيدون / تقرير الأثر)
 *   grantsTable()      grant_cards.js       — ترتيب جدول المنح وإجمالياته (صفحتا المانح والمستفيد)
 *   dateRangePicker()  date_range_picker.js — فلتر نطاق التاريخ
 *   logoCropper()      logo_cropper.js      — قص شعار الجهة المانحة
 * وملف الصفحة نفسه في مجلد pages/ يضيف ما يخصها فقط.
 */

// يدمج عدة أجزاء في مكوّن واحد. الجزء الأخير يغلب عند تكرار الاسم.
// (نستخدم الواصفات بدل {...spread} حتى تبقى الـ getters تعمل كـ getters ولا تُحسب مرة واحدة فقط)
function composeComponent(...parts) {
  const component = {};
  for (const part of parts) {
    Object.defineProperties(component, Object.getOwnPropertyDescriptors(part));
  }
  return component;
}

// يقرأ بيانات أرسلها Django للصفحة عبر {{ value|json_script:"id" }}
function readJsonScript(id) {
  return JSON.parse(document.getElementById(id).textContent);
}

function pageHelpers() {
  return {
    // رمز الحماية CSRF — كل صفحة فيها نموذج مخفي واحد يحمله
    csrfToken() {
      return document.querySelector('[name=csrfmiddlewaretoken]').value;
    },
    // 2025-09-30 → 30/09/2025
    isoToDisplay(iso) {
      if (!iso) return '';
      const [y, m, d] = iso.split('-');
      return `${d}/${m}/${y}`;
    },
    // "200,000" → 200000
    parseAmount(s) {
      const n = parseInt(String(s).replace(/[^0-9]/g, ''), 10);
      return isNaN(n) ? 0 : n;
    },
  };
}
