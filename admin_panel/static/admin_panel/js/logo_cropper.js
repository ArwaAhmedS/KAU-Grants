/*
 * logo_cropper.js — نافذة قص شعار الجهة المانحة داخل دائرة (سحب + تكبير).
 * قالبها: templates/admin_panel/partials/_logo_cropper.html
 *
 * الاستخدام: الصفحة تستدعي openCropper(dataUrl) بعد اختيار صورة، وتعرّف
 *   onLogoCropped(file, previewDataUrl)
 * لتستلم الشعار المقصوص (ملف PNG مربع 320×320 + صورة معاينة) عند الضغط على "استخدام الشعار".
 */
function logoCropper() {
  return {
    cropperOpen: false,
    cropperImgUrl: null,
    cropperZoom: 1,
    cropperOffsetX: 0,
    cropperOffsetY: 0,
    cropperBaseScale: 1,
    cropperNaturalW: 0,
    cropperNaturalH: 0,
    cropperDragging: false,
    cropperDragStartX: 0,
    cropperDragStartY: 0,
    cropperStartOffsetX: 0,
    cropperStartOffsetY: 0,

    openCropper(dataUrl) {
      this.cropperImgUrl = dataUrl;
      this.cropperZoom = 1;
      this.cropperOffsetX = 0;
      this.cropperOffsetY = 0;
      const img = new Image();
      img.onload = () => {
        this.cropperNaturalW = img.naturalWidth;
        this.cropperNaturalH = img.naturalHeight;
        this.cropperBaseScale = 280 / Math.min(img.naturalWidth, img.naturalHeight);
        this.cropperOpen = true;
      };
      img.src = dataUrl;
    },
    closeCropper() {
      this.cropperOpen = false;
      this.cropperImgUrl = null;
    },
    cropperClamp() {
      const scale = this.cropperBaseScale * this.cropperZoom;
      const dispW = this.cropperNaturalW * scale;
      const dispH = this.cropperNaturalH * scale;
      const maxX = Math.max(0, (dispW - 280) / 2);
      const maxY = Math.max(0, (dispH - 280) / 2);
      this.cropperOffsetX = Math.min(maxX, Math.max(-maxX, this.cropperOffsetX));
      this.cropperOffsetY = Math.min(maxY, Math.max(-maxY, this.cropperOffsetY));
    },
    cropperStartDrag(e) {
      this.cropperDragging = true;
      const point = e.touches ? e.touches[0] : e;
      this.cropperDragStartX = point.clientX;
      this.cropperDragStartY = point.clientY;
      this.cropperStartOffsetX = this.cropperOffsetX;
      this.cropperStartOffsetY = this.cropperOffsetY;
    },
    cropperDrag(e) {
      if (!this.cropperDragging) return;
      const point = e.touches ? e.touches[0] : e;
      this.cropperOffsetX = this.cropperStartOffsetX + (point.clientX - this.cropperDragStartX);
      this.cropperOffsetY = this.cropperStartOffsetY + (point.clientY - this.cropperDragStartY);
      this.cropperClamp();
    },
    cropperEndDrag() {
      this.cropperDragging = false;
    },
    async confirmCrop() {
      this.cropperClamp();
      const size = 320;
      const canvas = document.createElement('canvas');
      canvas.width = size;
      canvas.height = size;
      const ctx = canvas.getContext('2d');
      const img = new Image();
      img.src = this.cropperImgUrl;
      await new Promise((resolve) => { img.onload = resolve; });

      const scale = this.cropperBaseScale * this.cropperZoom * (size / 280);
      const dispW = this.cropperNaturalW * scale;
      const dispH = this.cropperNaturalH * scale;
      const dx = (size - dispW) / 2 + this.cropperOffsetX * (size / 280);
      const dy = (size - dispH) / 2 + this.cropperOffsetY * (size / 280);

      ctx.fillStyle = '#ffffff';
      ctx.fillRect(0, 0, size, size);
      ctx.drawImage(img, dx, dy, dispW, dispH);

      const blob = await new Promise((resolve) => canvas.toBlob(resolve, 'image/png'));
      const uniqueName = `logo_${Date.now()}_${Math.random().toString(36).slice(2, 8)}.png`;
      this.onLogoCropped(new File([blob], uniqueName, { type: 'image/png' }), canvas.toDataURL('image/png'));
      this.closeCropper();
    },
  };
}
