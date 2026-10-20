/*
 * add_donor.js — نموذج إضافة جهة مانحة جديدة (الاسم، جهات التواصل، الشعار).
 * القالب: templates/admin_panel/add_donor.html
 */
function addDonorForm() {
  return composeComponent(pageHelpers(), logoCropper(), {
    name: '',
    contacts: [{ name: '', title: '', email: '', phone: '' }],
    logoPreview: null,
    logoFile: null,
    saved: false,
    saving: false,
    errors: {},

    updateContact(index, field, value) {
      this.contacts[index][field] = value;
    },
    addContact() {
      this.contacts.push({ name: '', title: '', email: '', phone: '' });
    },
    removeContact(index) {
      this.contacts.splice(index, 1);
    },
    handleLogoChange(e) {
      const file = e.target.files[0];
      if (!file) return;
      const reader = new FileReader();
      reader.onload = () => { this.openCropper(reader.result); };
      reader.readAsDataURL(file);
      e.target.value = '';
    },
    // يستلم الشعار المقصوص من logoCropper()
    onLogoCropped(file, previewDataUrl) {
      this.logoFile = file;
      this.logoPreview = previewDataUrl;
    },
    validate() {
      const errs = {};
      if (!this.name.trim()) errs.name = 'اسم الجهة مطلوب';
      this.contacts.forEach((c, i) => {
        if (c.email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(c.email)) {
          errs['contactEmail-' + i] = 'البريد الإلكتروني غير صحيح';
        }
      });
      return errs;
    },
    async handleSave() {
      const errs = this.validate();
      if (Object.keys(errs).length) { this.errors = errs; return; }
      this.errors = {};
      if (this.saving) return;
      this.saving = true;

      const body = new FormData();
      body.append('csrfmiddlewaretoken', this.csrfToken());
      body.append('name', this.name.trim());
      body.append('contacts_json', JSON.stringify(this.contacts.map(c => ({
        name: c.name.trim(), title: c.title.trim(), email: c.email.trim(), phone: c.phone.trim(),
      }))));
      if (this.logoFile) body.append('logo', this.logoFile);

      try {
        const res = await fetch(window.location.pathname, { method: 'POST', body });
        if (!res.ok) throw new Error('save failed');
        this.saved = true;
        window.location.href = res.url;
      } catch (e) {
        this.saving = false;
        alert('تعذّر حفظ الجهة، يُرجى المحاولة مرة أخرى');
      }
    },
  });
}
