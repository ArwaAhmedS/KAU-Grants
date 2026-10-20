/*
 * donor_list.js — قائمة الجهات المانحة: بحث + فلتر الفئة + فلتر تاريخ آخر منحة.
 * القالب: templates/admin_panel/donor_list.html
 */
function donorListPage() {
  return composeComponent(dateRangePicker(), {
    donors: [],
    categoryStyles: {},
    query: '',
    categoryFilter: 'الكل',

    init() {
      this.donors = readJsonScript('static-donors-data');
      this.categoryStyles = readJsonScript('category-styles-data');
      this.initDateRangePicker();
    },

    get allDonors() {
      return this.donors;
    },
    get allCategories() {
      return [...new Set(this.allDonors.map(d => d.category).filter(Boolean))];
    },
    get filteredDonors() {
      const q = this.query.trim().toLowerCase();
      return this.allDonors.filter(d => {
        const matchText = !q || d.name.toLowerCase().includes(q);
        const matchCat = this.categoryFilter === 'الكل' || d.category === this.categoryFilter;
        const matchFrom = !this.dateRange.from || (d.lastGrantDate && d.lastGrantDate >= this.dateRange.from);
        const matchTo = !this.dateRange.to || (d.lastGrantDate && d.lastGrantDate <= this.dateRange.to);
        return matchText && matchCat && matchFrom && matchTo;
      });
    },
    formatAmount(n) {
      if (!n) return null;
      return n.toLocaleString('en-US') + ' ﷼';
    },
    formatDate(iso) {
      if (!iso) return null;
      const d = new Date(iso);
      return d.toLocaleDateString('ar-SA-u-ca-gregory', { year: 'numeric', month: 'short', day: 'numeric' });
    },
  });
}
