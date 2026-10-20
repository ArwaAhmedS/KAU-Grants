/*
 * date_picker.js — منتقي تاريخ واحد (يوم محدد). قالبه: templates/admin_panel/partials/_date_picker.html
 * initialValue: التاريخ الحالي (YYYY-MM-DD أو نص فارغ) — onChange: تُستدعى بالتاريخ الجديد عند الاختيار.
 */
function datePicker(initialValue, onChange) {
  const today = new Date();
  return {
    value: initialValue,
    open: false,
    viewYear: initialValue ? parseInt(initialValue.slice(0, 4)) : today.getFullYear(),
    viewMonth: initialValue ? parseInt(initialValue.slice(5, 7)) - 1 : today.getMonth(),
    monthsAr: ["يناير","فبراير","مارس","أبريل","مايو","يونيو","يوليو","أغسطس","سبتمبر","أكتوبر","نوفمبر","ديسمبر"],
    daysAr: ["ح","ن","ث","ر","خ","ج","س"],

    toggle() { this.open = !this.open; },
    prevMonth() { if (this.viewMonth === 0) { this.viewMonth = 11; this.viewYear -= 1; } else this.viewMonth -= 1; },
    nextMonth() { if (this.viewMonth === 11) { this.viewMonth = 0; this.viewYear += 1; } else this.viewMonth += 1; },
    isoToDisplay(iso) {
      if (!iso) return '';
      const [y, m, d] = iso.split('-');
      return `${d}/${m}/${y}`;
    },
    selectDay(day) {
      const mm = String(this.viewMonth + 1).padStart(2, '0');
      const dd = String(day).padStart(2, '0');
      const iso = `${this.viewYear}-${mm}-${dd}`;
      this.value = iso;
      onChange(iso);
      this.open = false;
    },
    selectToday() {
      const now = new Date();
      const mm = String(now.getMonth() + 1).padStart(2, '0');
      const dd = String(now.getDate()).padStart(2, '0');
      const iso = `${now.getFullYear()}-${mm}-${dd}`;
      this.value = iso;
      onChange(iso);
      this.open = false;
    },
    get cells() {
      const first = new Date(this.viewYear, this.viewMonth, 1).getDay();
      const total = new Date(this.viewYear, this.viewMonth + 1, 0).getDate();
      const arr = [];
      for (let i = 0; i < first; i++) arr.push(null);
      for (let d = 1; d <= total; d++) arr.push(d);
      return arr;
    },
    isSelected(day) {
      const mm = String(this.viewMonth + 1).padStart(2, '0');
      const dd = String(day).padStart(2, '0');
      return `${this.viewYear}-${mm}-${dd}` === this.value;
    },
    isToday(day) {
      const t = new Date();
      return day === t.getDate() && this.viewMonth === t.getMonth() && this.viewYear === t.getFullYear();
    },
  };
}
