/*
 * beneficiary_list.js — قائمة الجهات المستفيدة: بحث + ترتيب + فلتر تاريخ آخر منحة.
 * القالب: templates/admin_panel/beneficiary_list.html
 */
function beneficiaryListPage() {
  return composeComponent(dateRangePicker(), {
    beneficiaries: [],
    query: '',
    sortKey: 'الأحدث',

    init() {
      const raw = readJsonScript('beneficiaries-data');
      this.beneficiaries = raw.map(b => {
        const lastDateTs = b.lastGrantDate ? new Date(b.lastGrantDate + 'T12:00:00').getTime() : null;
        return {
          ...b, lastDateTs,
          lastDateFormatted: lastDateTs ? this.formatDate(new Date(lastDateTs)) : null,
        };
      });
      this.initDateRangePicker();
    },

    formatDate(d) {
      return d.toLocaleDateString('ar-SA-u-ca-gregory', { year: 'numeric', month: 'short', day: 'numeric' });
    },
    get filtered() {
      const q = this.query.trim().toLowerCase();
      const fromTs = this.dateRange.from ? new Date(this.dateRange.from).getTime() : 0;
      const toTs = this.dateRange.to ? new Date(this.dateRange.to).getTime() + 86399999 : Infinity;
      const list = this.beneficiaries.filter(b => {
        const matchText = !q || b.name.toLowerCase().includes(q);
        const ts = b.lastDateTs ?? 0;
        const matchFrom = !this.dateRange.from || ts >= fromTs;
        const matchTo = !this.dateRange.to || ts <= toTs;
        return matchText && matchFrom && matchTo;
      });
      if (this.sortKey === 'الأحدث') list.sort((a, b) => (b.lastDateTs ?? 0) - (a.lastDateTs ?? 0));
      else if (this.sortKey === 'الأكثر منحاً') list.sort((a, b) => b.grantsCount - a.grantsCount);
      else if (this.sortKey === 'الأعلى قيمة') list.sort((a, b) => b.totalAmount - a.totalAmount);
      else if (this.sortKey === 'الأكثر مستفيدين') list.sort((a, b) => b.totalBeneficiaries - a.totalBeneficiaries);
      return list;
    },
  });
}
