/*
 * dashboard.js — لوحة التحكم: إحصاءات + بحث/فلترة/ترتيب المنح + كروت المنحة.
 * القالب: templates/admin_panel/dashboard.html
 */
function dashboardPage() {
  return composeComponent(pageHelpers(), grantCards(), dateRangePicker(), {
    totalDonorsCount: 0,
    totalBeneficiariesCount: 0,
    query: '',
    typeFilter: 'الكل',
    grantSort: 'date-desc',

    init() {
      this.totalDonorsCount = readJsonScript('total-donors-data');
      this.totalBeneficiariesCount = readJsonScript('total-beneficiaries-data');
      this.initDateRangePicker();
      this.initGrantCards();
    },

    // بطاقات الإحصاءات تُحسب من نتائج البحث الحالية
    get stats() {
      const list = this.filteredGrants;
      const donorCount = new Set(list.map((g) => g.donorId)).size;
      const beneficiaryCount = new Set(list.map((g) => g.beneficiaryId)).size;
      const grantsAmount = list.reduce((sum, g) => sum + this.parseAmount(g.amount), 0);
      return [
        { label: 'إجمالي الجهات المانحة', value: String(donorCount),
          icon: '<svg class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" viewBox="0 0 24 24"><path d="M6 22V4a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v18Z"/><path d="M6 12H4a2 2 0 0 0-2 2v6a2 2 0 0 0 2 2h2"/><path d="M18 9h2a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2h-2"/><path d="M10 6h4"/><path d="M10 10h4"/><path d="M10 14h4"/><path d="M10 18h4"/></svg>' },
        { label: 'إجمالي الجهات المستفيدة', value: String(beneficiaryCount),
          icon: '<svg class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" viewBox="0 0 24 24"><line x1="3" x2="21" y1="22" y2="22"/><line x1="6" x2="6" y1="18" y2="11"/><line x1="10" x2="10" y1="18" y2="11"/><line x1="14" x2="14" y1="18" y2="11"/><line x1="18" x2="18" y1="18" y2="11"/><polygon points="12 2 20 7 4 7"/></svg>' },
        { label: 'إجمالي المنح', value: String(list.length),
          icon: '<svg class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" viewBox="0 0 24 24"><path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"/><path d="M14 2v4a2 2 0 0 0 2 2h4"/><path d="M10 9H8"/><path d="M16 13H8"/><path d="M16 17H8"/></svg>' },
        { label: 'إجمالي قيمة المنح', value: grantsAmount.toLocaleString('en-US') + ' ﷼',
          icon: '<svg class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" viewBox="0 0 24 24"><line x1="18" x2="18" y1="20" y2="10"/><line x1="12" x2="12" y1="20" y2="4"/><line x1="6" x2="6" y1="20" y2="14"/></svg>' },
      ];
    },
    get filteredGrants() {
      const q = this.query.trim().toLowerCase();
      let list = this.grants.filter((g) => {
        const matchText = !q || g.title.toLowerCase().includes(q) || g.donor.toLowerCase().includes(q) || g.beneficiary.toLowerCase().includes(q);
        const matchType = this.typeFilter === 'الكل' || g.type === this.typeFilter;
        const matchFrom = !this.dateRange.from || (g.date && g.date >= this.dateRange.from);
        const matchTo = !this.dateRange.to || (g.date && g.date <= this.dateRange.to);
        return matchText && matchType && matchFrom && matchTo;
      });
      list = list.slice().sort((a, b) => {
        const pa = this.parseAmount(a.amount);
        const pb = this.parseAmount(b.amount);
        if (this.grantSort === 'amount-desc') return pb - pa;
        if (this.grantSort === 'amount-asc') return pa - pb;
        if (this.grantSort === 'date-asc') return (a.date || '').localeCompare(b.date || '');
        return (b.date || '').localeCompare(a.date || '');
      });
      return list;
    },
  });
}
