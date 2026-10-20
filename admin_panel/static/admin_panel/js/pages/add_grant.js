/*
 * add_grant.js — نموذج إضافة منحة جديدة (بيانات المنحة، المستفيدون، الزيارات، الأخبار، الإعلانات).
 * القالب: templates/admin_panel/add_grant.html — منتقي التاريخ في date_picker.js
 */
function addGrantPage() {
  return composeComponent(pageHelpers(), {
    donorsList: [],
    beneficiariesList: [],
    beneficiaryCategories: [],
    form: {
      title: '', date: '', type: 'مالي',
      decisionNumber: '', decisionDate: '', decisionQtyCount: '', decisionQtyType: '',
      donor: '', donorOther: '', beneficiary: '', amount: '', status: 'جارية',
    },
    beneficiaryCounts: [],
    visits: [],
    newVisit: { date: '', purpose: '' },
    news: [],
    newNews: { title: '', url: '' },
    announcements: [],
    newAnnouncement: { text: '', url: '' },
    saving: false,
    saveError: '',

    init() {
      this.donorsList = readJsonScript('donors-list-data');
      this.beneficiariesList = readJsonScript('beneficiaries-list-data');
      this.beneficiaryCategories = readJsonScript('beneficiary-categories-data');
      if (this.beneficiaryCategories.length) {
        const first = this.beneficiaryCategories[0];
        this.beneficiaryCounts = [{ category: first[0], categoryLabel: first[1], count: 0, other_label: '' }];
      }
    },

    availableCategoriesFor(currentCategory) {
      const used = new Set(this.beneficiaryCounts.map((b) => b.category));
      return this.beneficiaryCategories.filter((c) => c[0] === currentCategory || !used.has(c[0]));
    },
    addBeneficiaryCategory() {
      const used = new Set(this.beneficiaryCounts.map((b) => b.category));
      const next = this.beneficiaryCategories.find((c) => !used.has(c[0]));
      if (!next) return;
      this.beneficiaryCounts.push({ category: next[0], categoryLabel: next[1], count: 0, other_label: '' });
    },
    addVisit() {
      if (!this.newVisit.date || !this.newVisit.purpose.trim()) return;
      this.visits.push({ ...this.newVisit });
      this.newVisit = { date: '', purpose: '' };
    },
    addNews() {
      if (!this.newNews.title.trim() || !this.newNews.url.trim()) return;
      this.news.push({ title: this.newNews.title.trim(), url: this.newNews.url.trim() });
      this.newNews = { title: '', url: '' };
    },
    addAnnouncement() {
      if (!this.newAnnouncement.text.trim() || !this.newAnnouncement.url.trim()) return;
      this.announcements.push({ text: this.newAnnouncement.text.trim(), url: this.newAnnouncement.url.trim() });
      this.newAnnouncement = { text: '', url: '' };
    },
    async saveGrant() {
      this.saveError = '';
      if (!this.form.title.trim()) { this.saveError = 'اكتب عنوان المنحة'; return; }
      if (!this.form.donor) { this.saveError = 'اختر الجهة المانحة'; return; }
      if (this.form.donor === '__other__' && !this.form.donorOther.trim()) { this.saveError = 'اكتب اسم الجهة المانحة'; return; }
      if (!this.form.beneficiary) { this.saveError = 'اختر الجهة المستفيدة'; return; }

      // إضافة تلقائية لأي بيانات مكتوبة في حقول الزيارات/الأخبار/الإعلانات ولم يُضغط لها زر "إضافة" بعد،
      // حتى لا تُفقد عند الحفظ.
      this.addVisit();
      this.addNews();
      this.addAnnouncement();

      const body = new FormData();
      body.append('csrfmiddlewaretoken', this.csrfToken());
      body.append('title', this.form.title);
      body.append('date', this.form.date);
      body.append('type', this.form.type === 'عيني' ? 'عيني' : 'مالي');
      body.append('decisionNumber', this.form.decisionNumber || '');
      body.append('decisionDate', this.form.decisionDate || '');
      body.append('decisionQuantityCount', this.form.decisionQtyCount || '');
      body.append('decisionQuantityType', (this.form.decisionQtyType || '').trim());
      body.append('donor_id', this.form.donor);
      body.append('donor_other', this.form.donorOther || '');
      body.append('beneficiary_id', this.form.beneficiary);
      body.append('amount', this.form.amount || '0');
      body.append('status', this.form.status);
      body.append('counts_json', JSON.stringify(this.beneficiaryCounts.map((b) => ({ category: b.category, count: b.count, other_label: b.other_label || '' }))));
      body.append('visits_json', JSON.stringify(this.visits));
      body.append('news_json', JSON.stringify(this.news));
      body.append('announcements_json', JSON.stringify(this.announcements));

      this.saving = true;
      try {
        const res = await fetch(window.location.pathname, { method: 'POST', body });
        if (!res.ok) throw new Error('save failed');
        window.location.href = res.url;
      } catch (e) {
        this.saving = false;
        this.saveError = 'تعذّر حفظ المنحة، يُرجى المحاولة مرة أخرى';
      }
    },
  });
}
