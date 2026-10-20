/*
 * beneficiary_dashboard.js — مكوّنات Alpine لبوابة المستفيد. القالب: templates/portal/beneficiary_dashboard.html
 *
 *   categoryManager()  كارد "عدد ونوع المستفيدين" لكل منحة (يُحفظ بإرسال النموذج العادي)
 *   itemsManager()     كارد "تفاصيل الأصناف المستلمة" للمنحة العينية (يُحفظ بـ AJAX دون إعادة تحميل)
 */
function categoryManager(scriptId, allCatsId) {
  return {
    categories: JSON.parse(document.getElementById(scriptId).textContent).map((c, i) => ({ ...c, id: 'existing_' + i })),
    allCategories: JSON.parse(document.getElementById(allCatsId).textContent),
    get availableCategories() {
      return this.allCategories.filter(c => !this.categories.some(x => x.value === c.value));
    },
    categoryOptions(idx) {
      const current = this.categories[idx].value;
      return this.allCategories.filter(c => c.value === current || !this.categories.some((x, i) => i !== idx && x.value === c.value));
    },
    addCategory() {
      if (this.availableCategories.length === 0) return;
      this.categories.push({ id: 'new_' + Date.now() + '_' + Math.random(), value: '', label: '', count: 0, other_label: '' });
    },
    changeCategory(idx, newValue) {
      const opt = this.allCategories.find(c => c.value === newValue);
      if (opt) { this.categories[idx].value = opt.value; this.categories[idx].label = opt.label; }
      if (newValue !== 'other') { this.categories[idx].other_label = ''; }
    },

    removeCategory(idx) { this.categories.splice(idx, 1); },
  };
}

function itemsManager(scriptId, maxItems) {
  return {
    items: JSON.parse(document.getElementById(scriptId).textContent),
    deletedIds: [],
    uidCounter: 1,
    maxItems: maxItems,
    saving: false,
    savedFlash: false,
    saveError: '',
    get limitReached() {
      return this.maxItems !== null && this.items.length >= this.maxItems;
    },
    addItem() {
      if (this.limitReached) return;
      this.items.push({
        uid: 'new_' + (this.uidCounter++) + '_' + Date.now(),
        id: null,
        item_type: 'صنف جديد',
        condition: 'new',
        building: '', floor: '', room: '', model: '', serial_number: '',
        attachment_name: '', attachment_url: '',
      });
    },
    removeItem(idx) {
      const it = this.items[idx];
      if (it.id) { this.deletedIds.push(it.id); }
      this.items.splice(idx, 1);
    },
    async saveItems(formEl) {
      if (this.saving) return;
      this.saving = true;
      this.saveError = '';
      this.savedFlash = false;
      const formData = new FormData(formEl);
      this.items.forEach((it) => {
        if (it._file instanceof File) {
          formData.set('file_' + it.uid, it._file);
        }
      });
      try {
        const res = await fetch(window.location.pathname, {
          method: 'POST', body: formData,
          headers: { 'X-Requested-With': 'XMLHttpRequest' },
        });
        if (!res.ok) throw new Error('HTTP ' + res.status);
        const data = await res.json();
        if (data.invalidFile) {
          // لم يُحفظ أي شيء: نُبقي ما كتبه المستخدم كما هو ليغيّر المرفق ويعيد الحفظ
          this.saveError = 'الملف المرفق غير مقبول: تأكد من نوعه (PDF أو Word أو Excel أو صورة) وأن حجمه لا يتجاوز 10 ميغابايت';
          this.saving = false;
          return;
        }
        this.items = data.items;
        this.deletedIds = [];
        if (data.duplicateSerial) {
          this.saveError = 'هذا الرقم التسلسلي مسجّل من قبل لصنف آخر';
        } else if (data.limitExceeded) {
          this.saveError = 'تم تجاوز العدد المسموح به من الأصناف. تم حفظ الأصناف ضمن الحد المسموح فقط';
        } else {
          this.savedFlash = true;
          setTimeout(() => { this.savedFlash = false; }, 3000);
        }
        this.saving = false;
      } catch (e) {
        console.error('saveItems: AJAX save failed, falling back to normal submit —', e);
        formEl.submit();
      }
    },
  };
}
