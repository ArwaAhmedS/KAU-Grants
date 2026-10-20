/*
 * beneficiary_detail.js — صفحة الجهة المستفيدة الواحدة: اسمها وإحصاءاتها + جدول منحها وكروت المنحة.
 * القالب: templates/admin_panel/beneficiary_detail.html
 */
function beneficiaryDetailPage() {
  return composeComponent(pageHelpers(), grantCards(), grantsTable(), {
    bData: null,
    beneficiaryEditMode: false,
    savingBeneficiary: false,
    editBeneficiaryName: '',

    init() {
      this.bData = readJsonScript('beneficiary-data');
      this.totalBeneficiariesCount = readJsonScript('total-beneficiaries-data');
      this.initGrantCards();
    },

    get stats() {
      return [
        { label: 'إجمالي المنح المستلمة', value: String(this.grants.length),
          icon: '<svg class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="m15.477 12.89 1.515 8.526a.5.5 0 0 1-.81.47l-3.58-2.687a1 1 0 0 0-1.197 0l-3.586 2.686a.5.5 0 0 1-.81-.469l1.514-8.526"/><circle cx="12" cy="8" r="6"/></svg>' },
        { label: 'إجمالي المستفيدين', value: String(this.totalBeneficiaries),
          icon: '<svg class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path stroke-linecap="round" stroke-linejoin="round" d="M22 21v-2a4 4 0 0 0-3-3.87"/><path stroke-linecap="round" stroke-linejoin="round" d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>' },
        { label: 'إجمالي مبلغ المنح المستلمة', value: this.totalAmount.toLocaleString('en-US') + ' ﷼',
          icon: '<svg class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><line stroke-linecap="round" x1="18" x2="18" y1="20" y2="10"/><line stroke-linecap="round" x1="12" x2="12" y1="20" y2="4"/><line stroke-linecap="round" x1="6" x2="6" y1="20" y2="14"/></svg>' },
      ];
    },

    // ── تعديل اسم الجهة ──
    enterBeneficiaryEdit() {
      this.editBeneficiaryName = this.bData.name;
      this.beneficiaryEditMode = true;
    },
    cancelBeneficiaryEdit() { this.beneficiaryEditMode = false; },
    async saveBeneficiaryEdit() {
      if (this.savingBeneficiary) return;
      this.savingBeneficiary = true;
      const body = new FormData();
      body.append('csrfmiddlewaretoken', this.csrfToken());
      body.append('form_type', 'save_beneficiary');
      body.append('name', this.editBeneficiaryName.trim() || this.bData.name);
      try {
        const res = await fetch(window.location.pathname, { method: 'POST', body, headers: { 'X-Requested-With': 'XMLHttpRequest' } });
        const data = await res.json();
        if (data.success) {
          this.bData.name = data.name;
          this.beneficiaryEditMode = false;
        } else {
          alert(data.error || 'تعذّر حفظ التعديل، يُرجى المحاولة مرة أخرى');
        }
      } catch (e) {
        alert('تعذّر حفظ التعديل، يُرجى المحاولة مرة أخرى');
      } finally {
        this.savingBeneficiary = false;
      }
    },
  });
}
