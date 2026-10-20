/*
 * donor_detail.js — صفحة الجهة المانحة الواحدة: بياناتها وجهات تواصلها وشعارها + جدول منحها وكروت المنحة.
 * القالب: templates/admin_panel/donor_detail.html
 */
function donorDetailPage() {
  return composeComponent(pageHelpers(), grantCards(), grantsTable(), logoCropper(), {
    donor: null,
    categoryStyles: {},
    categoryHistory: [],
    showCategoryHistory: false,
    // تعديل بيانات الجهة
    donorEditMode: false,
    savingDonor: false,
    editDonorName: '',
    editDonorLogo: null,
    editDonorLogoFile: null,
    editContacts: [],

    init() {
      this.donor = readJsonScript('donor-info-data');
      this.categoryStyles = readJsonScript('category-styles-data');
      this.categoryHistory = readJsonScript('category-history-data');
      this.totalBeneficiariesCount = readJsonScript('total-beneficiaries-data');
      this.initGrantCards();
    },

    get displayName() { return this.donor.name; },
    get displayLogo() { return this.donor.logoUrl; },
    get displayContacts() { return this.donor.contacts || []; },
    get catStyle() {
      return this.categoryStyles[this.donor.category] || { bg: 'bg-[#fdf3e7]', text: 'text-[#8B4513]', border: 'border-[#CD7F32]/40', dot: 'bg-[#CD7F32]' };
    },
    get stats() {
      return [
        { label: 'إجمالي منح الجهة', value: String(this.grants.length),
          icon: '<svg class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" viewBox="0 0 24 24"><path d="m15.477 12.89 1.515 8.526a.5.5 0 0 1-.81.47l-3.58-2.687a1 1 0 0 0-1.197 0l-3.586 2.686a.5.5 0 0 1-.81-.469l1.514-8.526"/><circle cx="12" cy="8" r="6"/></svg>' },
        { label: 'إجمالي المستفيدين', value: String(this.totalBeneficiaries),
          icon: '<svg class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" viewBox="0 0 24 24"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>' },
        { label: 'إجمالي مبلغ التبرع', value: this.totalAmount.toLocaleString('en-US') + ' ﷼',
          icon: '<svg class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" viewBox="0 0 24 24"><line x1="18" x2="18" y1="20" y2="10"/><line x1="12" x2="12" y1="20" y2="4"/><line x1="6" x2="6" y1="20" y2="14"/></svg>' },
      ];
    },

    // ── تعديل بيانات الجهة وجهات التواصل ──
    enterDonorEdit() {
      this.editDonorName = this.displayName;
      this.editDonorLogo = this.displayLogo;
      this.editDonorLogoFile = null;
      const dc = this.displayContacts;
      this.editContacts = dc.length ? dc.map((c) => ({ ...c })) : [{ name: '', title: '', email: '', phone: '' }];
      this.donorEditMode = true;
    },
    cancelDonorEdit() { this.donorEditMode = false; },
    async saveDonorEdit() {
      if (this.savingDonor) return;
      this.savingDonor = true;

      const body = new FormData();
      body.append('csrfmiddlewaretoken', this.csrfToken());
      body.append('form_type', 'save_donor');
      body.append('name', this.editDonorName.trim() || this.donor.name);
      body.append('contacts_json', JSON.stringify(this.editContacts.map((c) => ({
        name: c.name.trim(), title: c.title.trim(), email: c.email.trim(), phone: c.phone.trim(),
      }))));
      if (this.editDonorLogoFile) body.append('logo', this.editDonorLogoFile);

      try {
        const res = await fetch(window.location.pathname, { method: 'POST', body });
        if (!res.ok) throw new Error('save failed');
        window.location.reload();
      } catch (e) {
        this.savingDonor = false;
        alert('تعذّر حفظ التعديلات، يُرجى المحاولة مرة أخرى');
      }
    },
    addEditContact() { this.editContacts.push({ name: '', title: '', email: '', phone: '' }); },
    removeEditContact(i) { this.editContacts.splice(i, 1); },
    handleDonorLogoChange(e) {
      const file = e.target.files[0];
      if (!file) return;
      const reader = new FileReader();
      reader.onload = () => { this.openCropper(reader.result); };
      reader.readAsDataURL(file);
      e.target.value = '';
    },
    // يستلم الشعار المقصوص من logoCropper()
    onLogoCropped(file, previewDataUrl) {
      this.editDonorLogoFile = file;
      this.editDonorLogo = previewDataUrl;
    },
  });
}
