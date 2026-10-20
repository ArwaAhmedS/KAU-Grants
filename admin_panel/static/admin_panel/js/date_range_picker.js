/*
 * date_range_picker.js — فلتر نطاق التاريخ (من – إلى) المستخدم في لوحة التحكم وقائمتي المانحين والمستفيدين.
 *
 * النطاق المختار في dateRange = { from, to } بصيغة YYYY-MM-DD (نص فارغ = غير محدد)،
 * والصفحة تقرؤه لتفلتر قائمتها. الاختيار على مرحلتين: dpStage = 'from' ثم 'to'.
 * على الصفحة أن تستدعي initDateRangePicker() داخل init().
 */
function dateRangePicker() {
  return {
    dateRange: { from: '', to: '' },
    dpOpen: false,
    dpViewYear: new Date().getFullYear(),
    dpViewMonth: new Date().getMonth(),
    dpStage: 'from',
    dpHover: null,
    dpMonthsAr: ["يناير","فبراير","مارس","أبريل","مايو","يونيو","يوليو","أغسطس","سبتمبر","أكتوبر","نوفمبر","ديسمبر"],
    dpDaysAr: ["أح","إث","ث","أر","خ","ج","س"],
    dpTodayISO: '',

    initDateRangePicker() {
      const n = new Date();
      this.dpTodayISO = this.dpToISO(n.getFullYear(), n.getMonth(), n.getDate());
    },

    dpToISO(y, m, d) {
      return `${y}-${String(m + 1).padStart(2, '0')}-${String(d).padStart(2, '0')}`;
    },
    dpFmt(iso) {
      return new Date(iso + 'T12:00:00').toLocaleDateString('ar-SA-u-ca-gregory', { day: 'numeric', month: 'short' });
    },
    dpLabel() {
      if (!this.dateRange.from) return null;
      if (!this.dateRange.to) return this.dpFmt(this.dateRange.from);
      return `${this.dpFmt(this.dateRange.from)} – ${this.dpFmt(this.dateRange.to)}`;
    },
    dpToggleOpen() {
      if (!this.dpOpen) {
        if (this.dateRange.from) {
          const d = new Date(this.dateRange.from + 'T12:00:00');
          this.dpViewYear = d.getFullYear();
          this.dpViewMonth = d.getMonth();
        } else {
          const n = new Date();
          this.dpViewYear = n.getFullYear();
          this.dpViewMonth = n.getMonth();
        }
        this.dpStage = (this.dateRange.from && !this.dateRange.to) ? 'to' : 'from';
      }
      this.dpOpen = !this.dpOpen;
      this.dpHover = null;
    },
    dpPrevMonth() {
      if (this.dpViewMonth === 0) { this.dpViewMonth = 11; this.dpViewYear -= 1; }
      else this.dpViewMonth -= 1;
    },
    dpNextMonth() {
      if (this.dpViewMonth === 11) { this.dpViewMonth = 0; this.dpViewYear += 1; }
      else this.dpViewMonth += 1;
    },
    dpPickDay(iso) {
      if (this.dpStage === 'from') {
        this.dateRange = { from: iso, to: '' };
        this.dpStage = 'to';
        this.dpHover = null;
      } else {
        if (iso < this.dateRange.from) {
          this.dateRange = { from: iso, to: '' };
          this.dpStage = 'to';
        } else if (iso === this.dateRange.from) {
          this.dateRange = { from: '', to: '' };
          this.dpStage = 'from';
        } else {
          this.dateRange = { from: this.dateRange.from, to: iso };
          this.dpOpen = false;
          this.dpStage = 'from';
          this.dpHover = null;
        }
      }
    },
    dpClear() {
      this.dateRange = { from: '', to: '' };
      this.dpStage = 'from';
    },
    dpPickYear(e) {
      const year = e.target.value;
      if (!year) return;
      this.dateRange = { from: `${year}-01-01`, to: `${year}-12-31` };
      this.dpStage = 'from';
      this.dpOpen = false;
    },
    get dpYearOptions() {
      const currentYear = new Date().getFullYear();
      return Array.from({ length: 11 }, (_, i) => currentYear + 1 - i);
    },
    dpEffectiveTo() {
      return (this.dpStage === 'to' && this.dpHover && this.dateRange.from && this.dpHover > this.dateRange.from) ? this.dpHover : this.dateRange.to;
    },
    dpIsFrom(iso) { return iso === this.dateRange.from; },
    dpIsTo(iso) { return iso === this.dateRange.to; },
    dpIsEndpoint(iso) { return this.dpIsFrom(iso) || this.dpIsTo(iso); },
    dpInRange(iso) {
      const effectiveTo = this.dpEffectiveTo();
      return !!(this.dateRange.from && effectiveTo && iso > this.dateRange.from && iso < effectiveTo);
    },
    dpCells() {
      const firstDow = new Date(this.dpViewYear, this.dpViewMonth, 1).getDay();
      const daysInMo = new Date(this.dpViewYear, this.dpViewMonth + 1, 0).getDate();
      const cells = [];
      for (let i = 0; i < firstDow; i++) cells.push({ iso: null, day: null });
      for (let d = 1; d <= daysInMo; d++) cells.push({ iso: this.dpToISO(this.dpViewYear, this.dpViewMonth, d), day: d });
      while (cells.length % 7 !== 0) cells.push({ iso: null, day: null });
      return cells;
    },
  };
}
