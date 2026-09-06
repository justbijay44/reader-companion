pdfjsLib.GlobalWorkerOptions.workerSrc =
    "https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js";

let pdfDoc = null;
let currentPage = 1;
let documentId = null;

async function loadBookList() {
    const res = await fetch("/books/");
    const books = await res.json();

    const list = document.getElementById("book-list");
    list.innerHTML = "";

    for (const book of books) {
        const item = document.createElement("li");

        const title = document.createElement("span");
        title.textContent = book.filename.replace(/\.pdf$/i, "");
        item.appendChild(title);

        if (book.status !== "ready") {
            const badge = document.createElement("span");
            badge.className = "book-status";
            badge.textContent = "Processing…";
            item.appendChild(badge);
        }

        item.addEventListener("click", () => openBook(book));
        list.appendChild(item);
    }
}

async function openBook(book) {
    documentId = book.document_id;

    const progressRes = await fetch(`/books/${documentId}/progress`);
    const progress = await progressRes.json();
    currentPage = progress.current_page;

    document.getElementById("reader-empty").hidden = true;
    document.getElementById("pdf-canvas").hidden = false;
    document.getElementById("reader-controls").hidden = false;

    await loadPDF(`/uploads/${book.filename}`);

    document.getElementById("qna-messages").innerHTML = "";
    document.getElementById("qna-panel").hidden = false;
}

async function loadPDF(url) {
    pdfDoc = await pdfjsLib.getDocument(url).promise;
    renderPage(currentPage);
    updatePageInfo();
}

async function renderPage(pageNum) {
    const page = await pdfDoc.getPage(pageNum);
    const wrap = document.getElementById("canvas-wrap");
    const baseViewport = page.getViewport({ scale: 1 });
    const scale = Math.min(
        wrap.clientWidth / baseViewport.width,
        wrap.clientHeight / baseViewport.height
    );
    const dpr = window.devicePixelRatio || 1;
    const viewport = page.getViewport({ scale: scale * dpr });

    const canvas = document.getElementById("pdf-canvas");
    canvas.width = viewport.width;
    canvas.height = viewport.height;
    canvas.style.width = `${viewport.width / dpr}px`;
    canvas.style.height = `${viewport.height / dpr}px`;

    const ctx = canvas.getContext("2d");
    await page.render({ canvasContext: ctx, viewport: viewport }).promise;
}

let resizeTimeout;
new ResizeObserver(() => {
    if (!pdfDoc) return;
    clearTimeout(resizeTimeout);
    resizeTimeout = setTimeout(() => renderPage(currentPage), 120);
}).observe(document.getElementById("canvas-wrap"));

function updatePageInfo() {
    document.getElementById("page-info").textContent =
        `Page ${currentPage} of ${pdfDoc.numPages}`;
}

async function saveProgress() {
    await fetch(`/books/${documentId}/progress`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ current_page: currentPage }),
    });
}

document.getElementById("prev-btn").addEventListener("click", () => {
    if (pdfDoc && currentPage > 1) {
        currentPage--;
        renderPage(currentPage);
        updatePageInfo();
        saveProgress();
    }
});

document.getElementById("next-btn").addEventListener("click", () => {
    if (pdfDoc && currentPage < pdfDoc.numPages) {
        currentPage++;
        renderPage(currentPage);
        updatePageInfo();
        saveProgress();
    }
});

document.getElementById("jump-btn").addEventListener("click", () => {
    if (!pdfDoc) return;
    const target = parseInt(document.getElementById("page-jump").value, 10);
    if (target >= 1 && target <= pdfDoc.numPages) {
        currentPage = target;
        renderPage(currentPage);
        updatePageInfo();
        saveProgress();
    }
});

document.getElementById("focus-btn").addEventListener("click", () => {
    const entering = !document.body.classList.contains("focus-mode");
    document.body.classList.toggle("focus-mode", entering);
    if (entering) {
        document.documentElement.requestFullscreen?.().catch(() => {});
    } else if (document.fullscreenElement) {
        document.exitFullscreen?.();
    }
});

document.addEventListener("fullscreenchange", () => {
    if (!document.fullscreenElement) {
        document.body.classList.remove("focus-mode");
    }
});

document.addEventListener("keydown", (e) => {
    if (e.key === "ArrowRight") document.getElementById("next-btn").click();
    if (e.key === "ArrowLeft") document.getElementById("prev-btn").click();
});

document.getElementById("qna-ask-btn").addEventListener("click", async () => {
    if (!documentId) return;

    const input = document.getElementById("qna-input");
    const question = input.value.trim();
    if (!question) return;

    const messages = document.getElementById("qna-messages");
    messages.innerHTML += `<p><strong>You:</strong> ${question}</p>`;
    input.value = "";

    const res = await fetch(`/books/${documentId}/ask`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question }),
    });
    const data = await res.json();

    messages.innerHTML += `<p><strong>Answer:</strong> ${data.answer}</p>`;
    messages.scrollTop = messages.scrollHeight;
});

document.getElementById("upload-input").addEventListener("change", () => {
    const input = document.getElementById("upload-input");
    const label = document.getElementById("upload-filename");
    label.textContent = input.files.length ? input.files[0].name : "No file chosen";
});

document.getElementById("upload-btn").addEventListener("click", async () => {
    const input = document.getElementById("upload-input");
    if (!input.files.length) return;

    const formData = new FormData();
    formData.append("file", input.files[0]);

    await fetch("/books/upload", {
        method: "POST",
        body: formData,
    });

    input.value = "";
    document.getElementById("upload-filename").textContent = "No file chosen";
    loadBookList();
});

loadBookList();
setInterval(loadBookList, 5000);
