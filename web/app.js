"use strict";

const elements = {
  input: document.querySelector("#pdf-input"),
  dropZone: document.querySelector("#drop-zone"),
  fileCard: document.querySelector("#file-card"),
  fileName: document.querySelector("#file-name"),
  fileSize: document.querySelector("#file-size"),
  removeFile: document.querySelector("#remove-file"),
  ratioInputs: [...document.querySelectorAll('input[name="ratio"]')],
  customRatio: document.querySelector("#custom-ratio"),
  ruled: document.querySelector("#ruled"),
  convertButton: document.querySelector("#convert-button"),
  status: document.querySelector("#status"),
  statusText: document.querySelector("#status-text"),
  statusPercent: document.querySelector("#status-percent"),
  progressBar: document.querySelector("#progress-bar"),
  resultCard: document.querySelector("#result-card"),
  resultSummary: document.querySelector("#result-summary"),
  downloadButton: document.querySelector("#download-button"),
  previewSource: document.querySelector(".preview-source"),
  previewNotes: document.querySelector("#preview-notes"),
  ratioBadge: document.querySelector("#ratio-badge"),
};

const state = {
  file: null,
  resultUrl: null,
  processing: false,
};

const MAX_FILE_SIZE = 500 * 1024 * 1024;

function formatBytes(bytes) {
  if (bytes === 0) return "0 B";
  const units = ["B", "KB", "MB", "GB"];
  const index = Math.min(Math.floor(Math.log(bytes) / Math.log(1024)), units.length - 1);
  const value = bytes / 1024 ** index;
  return `${value.toFixed(index === 0 || value >= 10 ? 0 : 1)} ${units[index]}`;
}

function outputFileName(name) {
  const base = name.replace(/\.pdf$/i, "") || "document";
  return `${base}_with_notes.pdf`;
}

function clearResult() {
  if (state.resultUrl) {
    URL.revokeObjectURL(state.resultUrl);
    state.resultUrl = null;
  }
  elements.resultCard.hidden = true;
  elements.downloadButton.removeAttribute("href");
}

async function isPdfFile(file) {
  if (!file || (!file.name.toLowerCase().endsWith(".pdf") && file.type !== "application/pdf")) {
    return false;
  }

  const signature = new Uint8Array(await file.slice(0, 5).arrayBuffer());
  return String.fromCharCode(...signature) === "%PDF-";
}

async function selectFile(file) {
  if (!file) return;

  if (file.size > MAX_FILE_SIZE) {
    showError("500MBを超えるPDFは選択できません。ファイルを分割してお試しください。");
    return;
  }

  if (!(await isPdfFile(file))) {
    showError("PDFファイルを選択してください。");
    return;
  }

  clearResult();
  state.file = file;
  elements.fileName.textContent = file.name;
  elements.fileSize.textContent = `${formatBytes(file.size)} ・ 端末内で処理されます`;
  elements.dropZone.hidden = true;
  elements.fileCard.hidden = false;
  elements.convertButton.disabled = false;
  elements.status.hidden = true;
}

function removeSelectedFile() {
  if (state.processing) return;
  clearResult();
  state.file = null;
  elements.input.value = "";
  elements.fileCard.hidden = true;
  elements.dropZone.hidden = false;
  elements.convertButton.disabled = true;
  elements.status.hidden = true;
}

function selectedRatio() {
  const selected = elements.ratioInputs.find((input) => input.checked);
  if (!selected) return 1;
  if (selected.value !== "custom") return Number(selected.value);
  return Number(elements.customRatio.value) / 100;
}

function validateRatio() {
  const ratio = selectedRatio();
  if (!Number.isFinite(ratio) || ratio < 0.1 || ratio > 3) {
    throw new Error("ノート欄の幅は10%から300%の範囲で指定してください。");
  }
  return ratio;
}

function updatePreview() {
  const selected = elements.ratioInputs.find((input) => input.checked);
  const isCustom = selected?.value === "custom";
  elements.customRatio.disabled = !isCustom;

  let ratio = selectedRatio();
  if (!Number.isFinite(ratio)) ratio = 1;
  ratio = Math.min(Math.max(ratio, 0.1), 3);

  const sourcePercent = 100 / (1 + ratio);
  elements.previewSource.style.width = `${sourcePercent}%`;
  elements.previewNotes.classList.toggle("is-plain", !elements.ruled.checked);
  elements.ratioBadge.textContent = `本文 1 : ノート ${Number(ratio.toFixed(2))}`;
}

function updateProgress(percent, message) {
  const safePercent = Math.min(100, Math.max(0, Math.round(percent)));
  elements.status.hidden = false;
  elements.statusText.textContent = message;
  elements.statusPercent.textContent = `${safePercent}%`;
  elements.progressBar.style.width = `${safePercent}%`;
}

function showError(message) {
  elements.status.hidden = false;
  elements.statusText.textContent = message;
  elements.statusPercent.textContent = "エラー";
  elements.progressBar.style.width = "100%";
  elements.progressBar.style.background = "#c94e38";
}

function friendlyError(error) {
  const message = String(error?.message || error);
  if (/encrypted|password/i.test(message)) {
    return "パスワード付きPDFは変換できません。保護を解除したPDFでお試しください。";
  }
  if (/Failed to parse|No PDF header|Invalid PDF/i.test(message)) {
    return "PDFを読み取れませんでした。ファイルが破損していないか確認してください。";
  }
  return `変換に失敗しました。${message}`;
}

function nextFrame() {
  return new Promise((resolve) => requestAnimationFrame(() => resolve()));
}

async function convertPdf() {
  if (!state.file || state.processing) return;

  let ratio;
  try {
    ratio = validateRatio();
  } catch (error) {
    showError(error.message);
    return;
  }

  if (!window.PDFLib) {
    showError("PDF処理ライブラリを読み込めませんでした。通信状態を確認して再読み込みしてください。");
    return;
  }

  state.processing = true;
  clearResult();
  elements.progressBar.style.background = "";
  elements.convertButton.disabled = true;
  elements.convertButton.classList.add("is-working");
  elements.convertButton.querySelector("span").textContent = "変換しています…";
  elements.removeFile.disabled = true;
  updateProgress(2, "PDFを読み込んでいます…");

  try {
    const { PDFDocument, rgb } = window.PDFLib;
    const bytes = await state.file.arrayBuffer();
    const sourcePdf = await PDFDocument.load(bytes, { updateMetadata: false });
    const pageCount = sourcePdf.getPageCount();

    if (pageCount === 0) {
      throw new Error("ページがありません。");
    }

    const outputPdf = await PDFDocument.create();
    outputPdf.setProducer("PDF Side Note Maker Web");
    outputPdf.setCreator("PDF Side Note Maker Web");

    for (let index = 0; index < pageCount; index += 1) {
      const [page] = await outputPdf.copyPages(sourcePdf, [index]);
      const originalWidth = page.getWidth();
      const originalHeight = page.getHeight();
      const noteWidth = originalWidth * ratio;
      const newWidth = originalWidth + noteWidth;
      const padding = Math.min(24, noteWidth * 0.14);

      page.setSize(newWidth, originalHeight);
      page.drawRectangle({
        x: originalWidth,
        y: 0,
        width: noteWidth,
        height: originalHeight,
        color: rgb(1, 1, 0.985),
      });
      page.drawLine({
        start: { x: originalWidth, y: 0 },
        end: { x: originalWidth, y: originalHeight },
        thickness: 0.8,
        color: rgb(0.73, 0.78, 0.75),
      });

      if (elements.ruled.checked && noteWidth > padding * 2) {
        const topMargin = Math.min(36, originalHeight * 0.1);
        const bottomMargin = Math.min(36, originalHeight * 0.1);
        for (let y = originalHeight - topMargin; y > bottomMargin; y -= 24) {
          page.drawLine({
            start: { x: originalWidth + padding, y },
            end: { x: newWidth - padding, y },
            thickness: 0.45,
            color: rgb(0.81, 0.85, 0.83),
          });
        }
      }

      outputPdf.addPage(page);
      const progress = 10 + ((index + 1) / pageCount) * 78;
      updateProgress(progress, `${pageCount}ページ中 ${index + 1}ページを処理中…`);
      await nextFrame();
    }

    updateProgress(92, "ダウンロード用PDFを仕上げています…");
    const outputBytes = await outputPdf.save({
      useObjectStreams: true,
      addDefaultPage: false,
      objectsPerTick: 40,
    });
    const blob = new Blob([outputBytes], { type: "application/pdf" });
    state.resultUrl = URL.createObjectURL(blob);

    elements.downloadButton.href = state.resultUrl;
    elements.downloadButton.download = outputFileName(state.file.name);
    elements.resultSummary.textContent = `${pageCount}ページ ・ ${formatBytes(outputBytes.length)}`;
    elements.resultCard.hidden = false;
    updateProgress(100, "変換が完了しました");
  } catch (error) {
    console.error(error);
    showError(friendlyError(error));
  } finally {
    state.processing = false;
    elements.convertButton.disabled = !state.file;
    elements.convertButton.classList.remove("is-working");
    elements.convertButton.querySelector("span").textContent = "ノート欄付きPDFを作成";
    elements.removeFile.disabled = false;
  }
}

elements.input.addEventListener("change", (event) => selectFile(event.target.files?.[0]));
elements.removeFile.addEventListener("click", removeSelectedFile);
elements.convertButton.addEventListener("click", convertPdf);

for (const input of elements.ratioInputs) {
  input.addEventListener("change", updatePreview);
}

elements.customRatio.addEventListener("input", updatePreview);
elements.customRatio.addEventListener("focus", () => {
  const customOption = elements.ratioInputs.find((input) => input.value === "custom");
  customOption.checked = true;
  updatePreview();
});
elements.ruled.addEventListener("change", updatePreview);

for (const eventName of ["dragenter", "dragover"]) {
  elements.dropZone.addEventListener(eventName, (event) => {
    event.preventDefault();
    elements.dropZone.classList.add("is-dragging");
  });
}

for (const eventName of ["dragleave", "drop"]) {
  elements.dropZone.addEventListener(eventName, (event) => {
    event.preventDefault();
    elements.dropZone.classList.remove("is-dragging");
  });
}

elements.dropZone.addEventListener("drop", (event) => {
  selectFile(event.dataTransfer?.files?.[0]);
});

window.addEventListener("beforeunload", () => {
  if (state.resultUrl) URL.revokeObjectURL(state.resultUrl);
});

updatePreview();
