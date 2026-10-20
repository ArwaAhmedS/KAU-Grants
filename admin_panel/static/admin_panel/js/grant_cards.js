/*
 * grant_cards.js — منطق كروت المنحة المشتركة بين لوحة التحكم وصفحة المانح وصفحة المستفيد.
 *
 * الكروت (قوالبها في templates/admin_panel/partials/):
 *   _grant_detail_modal.html  تفاصيل المنحة + تعديلها + عدد ونوع المستفيدين
 *   _grant_items_modal.html   أصناف المنحة العينية
 *   _report_card_modal.html   تقرير الأثر (عرض / رفع / تراجع)
 *
 * على الصفحة أن تضع بيانات المنح في json_script باسم "grants-data" وتستدعي initGrantCards() داخل init().
 */
function grantCards() {
  return {
    // ── الحالة ──
    grants: [],
    beneficiariesList: [],
    beneficiaryCategories: [],
    selected: null,
    editMode: false,
    snapshot: null,
    saveFlash: false,
    savingEdit: false,
    newVisit: { date: '', purpose: '' },
    newNews: { title: '', url: '' },
    newAnn: { text: '', url: '' },
    showAddVisit: false,
    showAddNews: false,
    showAddAnn: false,
    deletedItemIds: [],
    itemsModalOpen: false,
    savingItems: false,
    itemsSavedFlash: false,
    itemsSaveError: '',
    savingCounts: false,
    countsSavedFlash: false,
    reportSelected: null,
    selectedReportIdx: 0,
    reportFileName: '',
    confirmingReportUpload: false,
    uploadedReportId: null,
    reportUploadError: false,

    // يحمّل البيانات، ثم يعيد فتح الكارد الذي كان مفتوحاً قبل إعادة تحميل الصفحة (حسب باراميترات الرابط)
    initGrantCards() {
      this.grants = readJsonScript('grants-data');
      this.beneficiariesList = readJsonScript('beneficiaries-list-data');
      this.beneficiaryCategories = readJsonScript('beneficiary-categories-data');

      const params = new URLSearchParams(window.location.search);
      const openGrantFlag = document.getElementById('open-grant-flag');
      if (openGrantFlag) {
        const gid = parseInt(openGrantFlag.dataset.id, 10);
        if (!isNaN(gid) && this.grants.some((g) => g.id === gid)) {
          this.openGrant(gid);
          if (params.get('saved') === '1') {
            this.saveFlash = true;
            setTimeout(() => { this.saveFlash = false; }, 2500);
          }
          if (document.getElementById('open-items-flag')) {
            this.itemsModalOpen = true;
            if (params.get('saved') === 'items') {
              this.itemsSavedFlash = true;
              setTimeout(() => { this.itemsSavedFlash = false; }, 2500);
            }
          }
        }
      }
      const openReportFlag = document.getElementById('open-report-flag');
      if (openReportFlag) {
        const rid = parseInt(openReportFlag.dataset.id, 10);
        if (!isNaN(rid) && this.grants.some((g) => g.id === rid)) {
          this.openReportCard(rid);
        }
      }
      // رفع تقرير رُفض لأن الملف غير مقبول (يرجع الخادم ?upload_error=1)
      this.reportUploadError = params.get('upload_error') === '1';
      // بعد رفع تقرير: مهلة 30 ثانية للتراجع
      const uploadedParam = params.get('uploaded');
      if (uploadedParam) {
        this.uploadedReportId = parseInt(uploadedParam, 10);
        setTimeout(() => { this.uploadedReportId = null; }, 30000);
      }
    },

    // ── كارد تفاصيل المنحة ──
    get grant() {
      if (this.selected === null) return null;
      return this.grants.find((g) => g.id === this.selected) || null;
    },
    decisionCombined(g) {
      const parts = [];
      if (g.decisionNumber) parts.push(`رقم ${g.decisionNumber}`);
      if (g.decisionDate) parts.push(this.isoToDisplay(g.decisionDate));
      if (g.type === 'عيني' && g.decisionQuantityCount) parts.push(`العدد ${g.decisionQuantityCount}`);
      return parts.join('، ') || '—';
    },
    resetAddForms() {
      this.newVisit = { date: '', purpose: '' };
      this.newNews = { title: '', url: '' };
      this.newAnn = { text: '', url: '' };
      this.showAddVisit = false;
      this.showAddNews = false;
      this.showAddAnn = false;
    },
    openGrant(id) {
      this.selected = id;
      this.editMode = false;
      this.snapshot = null;
      this.saveFlash = false;
      this.resetAddForms();
    },
    closeModal() {
      this.selected = null;
      this.editMode = false;
      this.snapshot = null;
      this.deletedItemIds = [];
      this.itemsModalOpen = false;
      this.itemsSavedFlash = false;
      this.itemsSaveError = '';
      this.countsSavedFlash = false;
      this.resetAddForms();
    },
    enterEdit() {
      if (!this.grant) return;
      this.snapshot = JSON.parse(JSON.stringify(this.grant));
      this.editMode = true;
      this.saveFlash = false;
      this.deletedItemIds = [];
      this.resetAddForms();
    },
    cancelEdit() {
      if (this.snapshot) {
        const idx = this.grants.findIndex((g) => g.id === this.snapshot.id);
        if (idx !== -1) this.grants[idx] = JSON.parse(JSON.stringify(this.snapshot));
      }
      this.editMode = false;
      this.snapshot = null;
      this.deletedItemIds = [];
      this.resetAddForms();
    },
    async saveEdit() {
      if (!this.grant) return;
      const g = this.grant;
      const body = new FormData();
      body.append('csrfmiddlewaretoken', this.csrfToken());
      body.append('form_type', 'save_grant');
      body.append('grant_id', g.id);
      body.append('type', g.type);
      body.append('date', g.date);
      body.append('beneficiary_id', g.beneficiaryId);
      body.append('decisionNumber', g.decisionNumber || '');
      body.append('decisionDate', g.decisionDate || '');
      body.append('decisionQuantityCount', g.decisionQuantityCount || '');
      body.append('decisionQuantityType', g.decisionQuantityType || '');
      body.append('amount', g.amount);
      body.append('status', g.status);
      body.append('visits_json', JSON.stringify(g.visits));
      body.append('news_json', JSON.stringify(g.news));
      body.append('announcements_json', JSON.stringify(g.announcements));

      this.savingEdit = true;
      try {
        const res = await fetch(window.location.pathname, { method: 'POST', body });
        if (!res.ok) throw new Error('save failed');
        window.location.href = window.location.pathname + '?open=' + g.id + '&saved=1';
      } catch (e) {
        this.savingEdit = false;
        alert('تعذّر حفظ التعديلات، يُرجى المحاولة مرة أخرى');
      }
    },
    addVisit() {
      if (!this.newVisit.date || !this.newVisit.purpose.trim()) return;
      this.grant.visits.push({ ...this.newVisit });
      this.newVisit = { date: '', purpose: '' };
      this.showAddVisit = false;
    },
    addNews() {
      if (!this.newNews.title.trim() || !this.newNews.url.trim()) return;
      this.grant.news.push({ title: this.newNews.title.trim(), url: this.newNews.url.trim() });
      this.newNews = { title: '', url: '' };
      this.showAddNews = false;
    },
    addAnnouncement() {
      if (!this.newAnn.text.trim() || !this.newAnn.url.trim()) return;
      this.grant.announcements.push({ text: this.newAnn.text.trim(), url: this.newAnn.url.trim() });
      this.newAnn = { text: '', url: '' };
      this.showAddAnn = false;
    },

    // ── عدد ونوع المستفيدين (حفظ مستقل داخل كارد التفاصيل) ──
    availableCategoriesForGrant() {
      if (!this.grant) return [];
      const used = new Set(this.grant.beneficiaries.map((b) => b.category));
      return this.beneficiaryCategories.filter((c) => !used.has(c[0]));
    },
    categoryOptionsFor(idx) {
      const current = this.grant.beneficiaries[idx].category;
      return this.beneficiaryCategories.filter((c) => c[0] === current || !this.grant.beneficiaries.some((b, i) => i !== idx && b.category === c[0]));
    },
    addBeneficiaryCategory() {
      if (!this.grant || this.availableCategoriesForGrant().length === 0) return;
      this.grant.beneficiaries.push({ category: '', categoryLabel: '', count: 0, other_label: '' });
    },
    removeBeneficiaryCategory(idx) {
      this.grant.beneficiaries.splice(idx, 1);
    },
    changeBeneficiaryCategory(idx, newValue) {
      const opt = this.beneficiaryCategories.find((c) => c[0] === newValue);
      const b = this.grant.beneficiaries[idx];
      if (opt) { b.category = opt[0]; b.categoryLabel = opt[1]; }
      if (newValue !== 'other') { b.other_label = ''; }
    },
    async saveCountsCard() {
      if (!this.grant) return;
      const g = this.grant;
      const body = new FormData();
      body.append('csrfmiddlewaretoken', this.csrfToken());
      body.append('form_type', 'save_counts');
      body.append('grant_id', g.id);
      (g.beneficiaries || []).forEach((b) => {
        body.append('category', b.category);
        body.append('count_value', b.count);
        body.append('other_label', b.other_label || '');
      });

      this.savingCounts = true;
      try {
        const res = await fetch(window.location.pathname, {
          method: 'POST', body,
          headers: { 'X-Requested-With': 'XMLHttpRequest' },
        });
        if (!res.ok) throw new Error('save failed');
        const data = await res.json();
        const idx = this.grants.findIndex((x) => x.id === g.id);
        if (idx !== -1) this.grants[idx].beneficiaries = data.beneficiaries;
        this.savingCounts = false;
        this.countsSavedFlash = true;
        setTimeout(() => { this.countsSavedFlash = false; }, 2500);
      } catch (e) {
        this.savingCounts = false;
        alert('تعذّر حفظ التعديلات، يُرجى المحاولة مرة أخرى');
      }
    },

    // ── كارد الأصناف (للمنح العينية) ──
    addItemToGrant() {
      if (!this.grant) return;
      if (this.grant.itemsLimit !== null && this.grant.items.length >= this.grant.itemsLimit) return;
      this.grant.items.push({
        uid: 'new_' + Date.now() + '_' + Math.random().toString(36).slice(2, 6),
        id: null, item_type: 'صنف جديد', condition: 'new',
        building: '', floor: '', room: '', model: '', serial_number: '',
        attachment_name: '', attachment_url: '', _file: null, clear_attachment: false,
      });
    },
    removeItemFromGrant(idx) {
      const it = this.grant.items[idx];
      if (it.id) this.deletedItemIds.push(it.id);
      this.grant.items.splice(idx, 1);
    },
    handleItemFileChange(e, it) {
      const file = e.target.files[0];
      if (!file) return;
      it._file = file;
      it.attachment_name = file.name;
      it.clear_attachment = false;
    },
    async saveItemsCard() {
      if (!this.grant) return;
      const g = this.grant;
      const body = new FormData();
      body.append('csrfmiddlewaretoken', this.csrfToken());
      body.append('form_type', 'save_items');
      body.append('grant_id', g.id);
      body.append('items_json', JSON.stringify((g.items || []).map((it) => ({
        id: it.id, uid: it.uid, item_type: it.item_type, condition: it.condition,
        building: it.building, floor: it.floor, room: it.room, model: it.model,
        serial_number: it.serial_number, clear_attachment: !!it.clear_attachment,
      }))));
      body.append('deleted_ids_json', JSON.stringify(this.deletedItemIds));
      (g.items || []).forEach((it) => {
        if (it._file instanceof File) body.append('file_' + it.uid, it._file);
      });

      this.savingItems = true;
      this.itemsSaveError = '';
      this.itemsSavedFlash = false;
      try {
        const res = await fetch(window.location.pathname, {
          method: 'POST', body,
          headers: { 'X-Requested-With': 'XMLHttpRequest' },
        });
        if (!res.ok) throw new Error('save failed');
        const data = await res.json();
        this.savingItems = false;
        if (data.invalidFile) {
          // لم يُحفظ أي شيء: نُبقي ما كتبه المستخدم كما هو ليغيّر المرفق ويعيد الحفظ
          this.itemsSaveError = 'الملف المرفق غير مقبول: تأكد من نوعه (PDF أو Word أو Excel أو صورة) وأن حجمه لا يتجاوز 10 ميغابايت. لم يتم حفظ التعديلات';
          return;
        }
        if (data.duplicateSerial) {
          // لم يُحفظ أي شيء: نُبقي ما كتبه المستخدم كما هو ليصحّح الرقم المكرر ويعيد الحفظ
          this.itemsSaveError = 'هذا الرقم التسلسلي مسجّل من قبل لصنف آخر. لم يتم حفظ التعديلات';
          return;
        }
        const idx = this.grants.findIndex((x) => x.id === g.id);
        if (idx !== -1) {
          this.grants[idx].items = data.items;
          this.grants[idx].itemsLimit = data.itemsLimit;
        }
        this.deletedItemIds = [];
        if (data.limitExceeded) {
          this.itemsSaveError = 'تم تجاوز العدد المسموح به من الأصناف. تم حفظ الأصناف ضمن الحد المسموح فقط';
          return;
        }
        this.itemsSavedFlash = true;
        setTimeout(() => { this.itemsSavedFlash = false; }, 2500);
      } catch (e) {
        this.savingItems = false;
        alert('تعذّر حفظ الأصناف، يُرجى المحاولة مرة أخرى');
      }
    },

    // ── كارد تقرير الأثر ──
    get reportGrant() {
      if (this.reportSelected === null) return null;
      return this.grants.find((g) => g.id === this.reportSelected) || null;
    },
    get reportPreviewUrl() {
      const r = this.reportGrant && this.reportGrant.reports[this.selectedReportIdx];
      return r && r.url ? r.url + '#toolbar=0&navpanes=0&scrollbar=0' : '';
    },
    openReportCard(id) {
      this.reportSelected = id;
      const g = this.grants.find((x) => x.id === id);
      this.selectedReportIdx = g && g.reports.length > 0 ? g.reports.length - 1 : 0;
    },
    closeReportCard() {
      this.reportSelected = null;
      this.reportUploadError = false;
      this.reportFileName = '';
      this.confirmingReportUpload = false;
    },
    cancelReportUpload() {
      this.reportFileName = '';
      this.confirmingReportUpload = false;
      if (this.$refs.reportCardInput) this.$refs.reportCardInput.value = '';
    },
    // رابط الرفع يأتي من القالب (data-upload-report-url بكارد التقرير) وفيه 0 مكان رقم المنحة
    uploadReportUrl(grantId) {
      const template = document.querySelector('[data-upload-report-url]').dataset.uploadReportUrl;
      return template.replace('/0/', '/' + grantId + '/');
    },
    async confirmReportUpload() {
      const file = this.$refs.reportCardInput.files[0];
      if (!file || !this.reportGrant) return;
      const grantId = this.reportGrant.id;
      const body = new FormData();
      body.append('csrfmiddlewaretoken', this.csrfToken());
      body.append('file', file);
      body.append('next', window.location.pathname);
      try {
        const res = await fetch(this.uploadReportUrl(grantId), { method: 'POST', body });
        if (!res.ok) throw new Error('upload failed');
        window.location.href = res.url;
      } catch (err) {
        this.confirmingReportUpload = false;
        alert('تعذّر رفع التقرير، يُرجى المحاولة مرة أخرى');
      }
    },
    async undoReportUpload() {
      if (!this.uploadedReportId || !this.reportGrant) return;
      const grantId = this.reportGrant.id;
      const body = new FormData();
      body.append('csrfmiddlewaretoken', this.csrfToken());
      body.append('action', 'delete');
      body.append('report_id', this.uploadedReportId);
      body.append('next', window.location.pathname);
      try {
        const res = await fetch(this.uploadReportUrl(grantId), { method: 'POST', body });
        if (!res.ok) throw new Error('delete failed');
        window.location.href = res.url;
      } catch (err) {
        alert('تعذّر التراجع عن الرفع، يُرجى المحاولة مرة أخرى');
      }
    },
  };
}

/*
 * grantsTable() — ترتيب جدول "منح الجهة" وإجمالياته، لصفحتي المانح والمستفيد.
 */
function grantsTable() {
  return {
    grantSort: '',
    totalBeneficiariesCount: 0,
    get totalBeneficiaries() { return this.totalBeneficiariesCount; },
    get totalAmount() {
      return this.grants.reduce((sum, g) => sum + this.parseAmount(g.amount), 0);
    },
    get sortedGrants() {
      const list = this.grants.slice();
      if (!this.grantSort) return list;
      return list.sort((a, b) => {
        const pa = this.parseAmount(a.amount);
        const pb = this.parseAmount(b.amount);
        if (this.grantSort === 'amount-desc') return pb - pa;
        if (this.grantSort === 'amount-asc') return pa - pb;
        if (this.grantSort === 'date-asc') return (a.date || '').localeCompare(b.date || '');
        if (this.grantSort === 'date-desc') return (b.date || '').localeCompare(a.date || '');
        return 0;
      });
    },
  };
}
