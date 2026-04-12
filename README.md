<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PDF Mapper • Dynamic Detection</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.min.js"></script>
    <style>
        body { font-family: 'Inter', system-ui, sans-serif; }
        .drop-zone { transition: all 0.3s; }
        .drop-zone.dragover { background-color: #1a1a2e; border-color: #22d3ee; }
    </style>
</head>
<body class="bg-[#0a0a0a] text-white">

<nav class="border-b border-white/10 bg-black/80 backdrop-blur fixed w-full z-50">
    <div class="max-w-7xl mx-auto px-8 py-5 flex justify-between items-center">
        <h1 class="text-2xl font-semibold">📄 PDF Mapper</h1>
        <div class="flex gap-6">
            <button onclick="showTab(0)" id="tab-0" class="tab-btn border-b-2 border-cyan-400 pb-1">Manage Presets</button>
            <button onclick="showTab(1)" id="tab-1" class="tab-btn pb-1">Upload Package</button>
        </div>
    </div>
</nav>

<div id="tab-content-0" class="pt-28 max-w-5xl mx-auto px-8">
    <h2 class="text-3xl font-bold mb-2">Your Saved Presets</h2>
    <div class="bg-[#111111] rounded-3xl p-8">
        <div class="flex gap-4 mb-8">
            <input id="new-name" placeholder="Document Name" class="flex-1 bg-[#1a1a1a] border border-white/20 rounded-2xl px-5 py-4 focus:outline-none focus:border-cyan-400">
            <input id="new-instr" placeholder="Instructions..." class="flex-1 bg-[#1a1a1a] border border-white/20 rounded-2xl px-5 py-4 focus:outline-none focus:border-cyan-400">
            <button onclick="addNewPreset()" class="bg-cyan-400 hover:bg-cyan-300 text-black font-semibold px-8 rounded-2xl">Add Preset</button>
        </div>
        <div id="presets-list" class="space-y-4 max-h-[65vh] overflow-auto"></div>
    </div>
</div>

<div id="tab-content-1" class="pt-28 max-w-5xl mx-auto px-8 hidden">
    <div id="upload-zone" class="drop-zone border-2 border-dashed border-white/30 bg-[#111111] rounded-3xl p-20 text-center cursor-pointer">
        <input type="file" id="file-input" accept="application/pdf" class="hidden" onchange="handleFileSelect(event)">
        <div onclick="document.getElementById('file-input').click()">
            <div class="text-7xl mb-6">📤</div>
            <h3 class="text-3xl font-semibold mb-2">Drop any PDF</h3>
            <p class="text-white/70">Dynamic detection — finds every document title automatically</p>
        </div>
    </div>

    <div id="processing" class="hidden mt-12 text-center">
        <div class="inline-flex items-center gap-4 bg-[#1a1a1a] px-10 py-6 rounded-3xl">
            <div class="w-6 h-6 border-4 border-cyan-400 border-t-transparent animate-spin rounded-full"></div>
            <span class="text-lg">Reading PDF and detecting every document title...</span>
        </div>
    </div>

    <div id="results" class="hidden mt-10">
        <h3 class="text-2xl font-semibold mb-6">Documents Found Inside Your PDF</h3>
        <div id="detected-list" class="space-y-4"></div>
        <button onclick="confirmAndGeneratePDF()" class="mt-10 w-full bg-cyan-400 text-black font-semibold py-6 rounded-3xl text-xl">✅ Generate Mapped PDF</button>
    </div>
</div>

<script>
pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js';

let presets = [];
let currentDetectedDocs = [];
let currentFileName = "";

function loadPresets() { /* same as before - keeps your saved presets */ 
    const saved = localStorage.getItem("pdfMapper_presets_v13");
    if (saved) presets = JSON.parse(saved);
    else presets = [];
    renderPresets();
}
function savePresets() { localStorage.setItem("pdfMapper_presets_v13", JSON.stringify(presets)); }
function renderPresets() { /* same */ }
function addNewPreset() { /* same */ }
function editPreset(i) { /* same */ }
function deletePreset(i) { /* same */ }

async function handleFileSelect(e) {
    const file = e.target.files[0];
    if (!file) return;
    currentFileName = file.name;

    document.getElementById("upload-zone").classList.add("hidden");
    document.getElementById("processing").classList.remove("hidden");

    const arrayBuffer = await file.arrayBuffer();
    const pdf = await pdfjsLib.getDocument(new Uint8Array(arrayBuffer)).promise;
    let fullText = "";

    for (let i = 1; i <= Math.min(pdf.numPages, 1000); i++) {
        const page = await pdf.getPage(i);
        const textContent = await page.getTextContent();
        fullText += "\n" + textContent.items.map(item => item.str).join(" ");
    }

    detectDocumentsDynamically(fullText);
}

function detectDocumentsDynamically(text) {
    const lines = text.split(/\n+/).map(l => l.trim()).filter(l => l.length > 3);

    const potentialTitles = new Set();

    lines.forEach(line => {
        // Look for likely document titles: ALL CAPS, short, or ending with common title words
        if (line === line.toUpperCase() && line.length < 120 && 
            (line.length > 8 || /AGREEMENT|DISCLOSURE|STATEMENT|AMENDMENT|INSTRUCTIONS|ATTESTATION|NOTICE|DEMAND|ADDENDUM|EXHIBIT/i.test(line))) {
            potentialTitles.add(line);
        }
    });

    currentDetectedDocs = Array.from(potentialTitles).map(title => ({
        name: title,
        matched: presets.some(p => p.name.toLowerCase() === title.toLowerCase())
    }));

    // Fallback if nothing found
    if (currentDetectedDocs.length === 0) {
        currentDetectedDocs = [{name: "Full PDF Content", matched: false}];
    }

    document.getElementById("processing").classList.add("hidden");
    renderDetectedDocuments();
}

function renderDetectedDocuments() {
    const container = document.getElementById("detected-list");
    container.innerHTML = "";
    currentDetectedDocs.forEach((doc, i) => {
        const hasPreset = presets.some(p => p.name.toLowerCase() === doc.name.toLowerCase());
        const div = document.createElement("div");
        div.className = `p-6 rounded-3xl ${hasPreset ? 'bg-emerald-900/30 border border-emerald-400' : 'bg-amber-900/30 border border-amber-400'}`;
        div.innerHTML = `<div class="flex justify-between items-start"><div><strong>${doc.name}</strong><p class="text-sm mt-1 ${hasPreset ? 'text-emerald-400' : 'text-amber-400'}">${hasPreset ? '✅ Preset ready' : '⚠️ No preset yet'}</p></div>${!hasPreset ? `<button onclick="createPresetFor(${i})" class="bg-white/10 hover:bg-white/20 px-6 py-3 rounded-2xl text-sm">Create Preset</button>` : ''}</div>`;
        container.appendChild(div);
    });
    document.getElementById("results").classList.remove("hidden");
}

function createPresetFor(i) { /* same prompt as before */ }
function confirmAndGeneratePDF() { /* same */ }
function generateMappedPDF() { /* same */ }
function showTab(n) { /* same */ }

const dropZone = document.getElementById('upload-zone');
dropZone.addEventListener('dragover', e => { e.preventDefault(); dropZone.classList.add('dragover'); });
dropZone.addEventListener('dragleave', () => dropZone.classList.remove('dragover'));
dropZone.addEventListener('drop', e => {
    e.preventDefault(); dropZone.classList.remove('dragover');
    if (e.dataTransfer.files[0]) {
        const dt = new DataTransfer();
        dt.items.add(e.dataTransfer.files[0]);
        document.getElementById('file-input').files = dt.files;
        handleFileSelect({target: {files: dt.files}});
    }
});

window.onload = loadPresets;
</script>
</body>
</html>
