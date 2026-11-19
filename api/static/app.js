/**
 * PlantCare AI – Interactive Front-End Engine
 * Monochromatic Architecture & Agricultural Intelligence
 */

document.addEventListener('DOMContentLoaded', () => {
  // 1. Theme Management (Obsidian Dark <-> Light Grey Monochromatic)
  initThemeManager();

  // 2. Global Keyboard Shortcuts
  initKeyboardShortcuts();

  // 3. Mobile Navigation Drawer
  initMobileNav();

  // 4. Scanner Engine (Upload, Drag&Drop, Preview, Sample Selector)
  initScannerEngine();

  // 5. Landing Page Interactive Features (Demo Simulator, Crop Matrix, FAQ)
  initLandingInteractions();

  // 6. Result Page Inspection Lens & Action Tools
  initResultPageTools();

  // 7. Table Search & Filtering (Dashboard & History)
  initTableFiltering();

  // 8. Flash message dismiss
  initFlashDismiss();
});

/* ==========================================================================
   1. Theme Management
   ========================================================================== */
function initThemeManager() {
  const themeBtn = document.getElementById('theme-toggle-btn');
  const storedTheme = localStorage.getItem('plantcare_theme') || 'dark';

  document.documentElement.setAttribute('data-theme', storedTheme);
  updateThemeIcon(storedTheme);

  if (themeBtn) {
    themeBtn.addEventListener('click', () => {
      const current = document.documentElement.getAttribute('data-theme') || 'dark';
      const next = current === 'dark' ? 'light' : 'dark';
      document.documentElement.setAttribute('data-theme', next);
      localStorage.setItem('plantcare_theme', next);
      updateThemeIcon(next);
    });
  }
}

function updateThemeIcon(theme) {
  const themeBtn = document.getElementById('theme-toggle-btn');
  if (!themeBtn) return;
  themeBtn.innerHTML = theme === 'dark' 
    ? '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/></svg>'
    : '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>';
}

/* ==========================================================================
   2. Keyboard Shortcuts
   ========================================================================== */
function initKeyboardShortcuts() {
  document.addEventListener('keydown', (e) => {
    // Avoid triggering when focused on an input or textarea
    if (['INPUT', 'SELECT', 'TEXTAREA'].includes(document.activeElement.tagName)) return;

    if (e.key === 's' || e.key === 'S') {
      window.location.href = '/scan';
    } else if (e.key === 'd' || e.key === 'D') {
      window.location.href = '/dashboard';
    } else if (e.key === 'h' || e.key === 'H') {
      window.location.href = '/history';
    } else if (e.key === 't' || e.key === 'T') {
      const themeBtn = document.getElementById('theme-toggle-btn');
      if (themeBtn) themeBtn.click();
    }
  });
}

/* ==========================================================================
   3. Mobile Navigation
   ========================================================================== */
function initMobileNav() {
  const menuBtn = document.getElementById('mobile-menu-btn');
  const navLinks = document.getElementById('nav-links');
  if (menuBtn && navLinks) {
    menuBtn.addEventListener('click', () => {
      navLinks.classList.toggle('mobile-open');
    });
  }
}

/* ==========================================================================
   4. Scanner Engine
   ========================================================================== */
function initScannerEngine() {
  const form = document.getElementById('upload-form');
  const fileInput = document.getElementById('image');
  const dropZone = document.getElementById('drop-zone');
  const previewDeck = document.getElementById('preview-deck');
  const previewImg = document.getElementById('preview-img');
  const fileInfo = document.getElementById('preview-file-info');
  const removeBtn = document.getElementById('remove-btn');
  const zoomInBtn = document.getElementById('zoom-in-btn');
  const zoomOutBtn = document.getElementById('zoom-out-btn');
  const filterBtn = document.getElementById('filter-btn');
  const scannerOverlay = document.getElementById('scanner-overlay');
  const progressMsg = document.getElementById('scan-progress-msg');
  const cropSelect = document.getElementById('crop');

  if (!form || !fileInput) return;

  let currentScale = 1;
  let isInverted = false;

  // Crop Radio Selection Sync
  const cropRadios = document.querySelectorAll('input[name="crop"]');
  cropRadios.forEach(radio => {
    radio.addEventListener('change', () => {
      document.querySelectorAll('.crop-pill-btn').forEach(p => p.classList.remove('active'));
      const label = radio.closest('.crop-pill-btn');
      if (label) label.classList.add('active');
    });
  });

  // Drag and drop handlers
  if (dropZone) {
    ['dragenter', 'dragover'].forEach(name => {
      dropZone.addEventListener(name, (e) => {
        e.preventDefault();
        dropZone.classList.add('dragover');
      });
    });

    ['dragleave', 'drop'].forEach(name => {
      dropZone.addEventListener(name, (e) => {
        e.preventDefault();
        dropZone.classList.remove('dragover');
      });
    });

    dropZone.addEventListener('drop', (e) => {
      if (e.dataTransfer && e.dataTransfer.files.length > 0) {
        handleFileSelection(e.dataTransfer.files[0]);
      }
    });

    dropZone.addEventListener('click', () => {
      fileInput.click();
    });
  }

  fileInput.addEventListener('change', (e) => {
    if (fileInput.files && fileInput.files.length > 0) {
      handleFileSelection(fileInput.files[0]);
    }
  });

  function handleFileSelection(file) {
    const allowed = ['image/jpeg', 'image/png', 'image/jpg'];
    if (!allowed.includes(file.type)) {
      showToast('Only JPG, JPEG, or PNG images are supported.', 'error');
      return;
    }

    const maxMb = 5;
    if (file.size > maxMb * 1024 * 1024) {
      showToast(`File size is ${(file.size / (1024 * 1024)).toFixed(1)}MB. Limit is ${maxMb}MB.`, 'error');
      return;
    }

    // Set file to input via DataTransfer if dropped
    const dt = new DataTransfer();
    dt.items.add(file);
    fileInput.files = dt.files;

    // Show Preview
    const reader = new FileReader();
    reader.onload = (e) => {
      previewImg.src = e.target.result;
      if (dropZone) dropZone.style.display = 'none';
      if (previewDeck) previewDeck.classList.add('active');
      
      const kb = Math.round(file.size / 1024);
      if (fileInfo) {
        fileInfo.textContent = `${file.name} • ${kb} KB • ${file.type.split('/')[1].toUpperCase()}`;
      }
      currentScale = 1;
      previewImg.style.transform = `scale(1)`;
    };
    reader.readAsDataURL(file);
  }

  // Remove / Re-upload Button
  if (removeBtn) {
    removeBtn.addEventListener('click', () => {
      fileInput.value = '';
      if (previewDeck) previewDeck.classList.remove('active');
      if (dropZone) dropZone.style.display = 'flex';
      previewImg.src = '';
    });
  }

  // Zoom In / Out
  if (zoomInBtn) {
    zoomInBtn.addEventListener('click', () => {
      currentScale = Math.min(currentScale + 0.25, 2.5);
      previewImg.style.transform = `scale(${currentScale})`;
    });
  }

  if (zoomOutBtn) {
    zoomOutBtn.addEventListener('click', () => {
      currentScale = Math.max(currentScale - 0.25, 0.75);
      previewImg.style.transform = `scale(${currentScale})`;
    });
  }

  // Contrast Filter Toggle
  if (filterBtn) {
    filterBtn.addEventListener('click', () => {
      isInverted = !isInverted;
      const viewport = document.getElementById('preview-viewport');
      if (viewport) {
        viewport.classList.toggle('filter-invert', isInverted);
      }
    });
  }

  // Quick Sample Leaf Selector
  const sampleChips = document.querySelectorAll('.sample-leaf-chip');
  sampleChips.forEach(chip => {
    chip.addEventListener('click', async () => {
      const samplePath = chip.getAttribute('data-sample');
      const crop = chip.getAttribute('data-crop');

      // Select crop radio
      const targetRadio = document.querySelector(`input[name="crop"][value="${crop}"]`);
      if (targetRadio) {
        targetRadio.checked = true;
        targetRadio.dispatchEvent(new Event('change'));
      }

      try {
        const response = await fetch(samplePath);
        const blob = await response.blob();
        const filename = samplePath.split('/').pop();
        const file = new File([blob], filename, { type: blob.type || 'image/jpeg' });
        handleFileSelection(file);
        showToast(`Loaded sample leaf for ${crop.toUpperCase()}`, 'info');
      } catch (err) {
        showToast('Could not load sample leaf.', 'error');
      }
    });
  });

  // Form Submit & Scanning Radar HUD Animation
  form.addEventListener('submit', (e) => {
    if (!fileInput.files || fileInput.files.length === 0) {
      e.preventDefault();
      showToast('Please upload or choose a leaf image first.', 'warning');
      return;
    }

    // Activate radar scanning HUD
    if (scannerOverlay) scannerOverlay.classList.add('active');

    // Simulate animated diagnostic progress steps
    const steps = [
      '[1/3] Calibrating leaf edge morphology...',
      '[2/3] Querying PlantCare Vision AI...',
      '[3/3] Generating pathology report and agronomy actions...'
    ];
    let stepIndex = 0;
    const interval = setInterval(() => {
      stepIndex++;
      if (stepIndex < steps.length && progressMsg) {
        progressMsg.textContent = steps[stepIndex];
      } else {
        clearInterval(interval);
      }
    }, 1800);
  });
}

/* ==========================================================================
   5. Landing Page Interactions
   ========================================================================== */
function initLandingInteractions() {
  // 1. Hero Simulator
  const demoTabs = document.querySelectorAll('.demo-tab-btn');
  const demoImg = document.getElementById('demo-preview-img');
  const demoCrop = document.getElementById('demo-crop-title');
  const demoStatus = document.getElementById('demo-status-badge');
  const demoConf = document.getElementById('demo-conf-val');
  const demoSev = document.getElementById('demo-sev-val');

  const demoData = {
    tomato: {
      crop: 'Tomato (Solanum lycopersicum)',
      disease: 'Early Blight (Alternaria solani)',
      status: 'DISEASED',
      badgeClass: 'badge-diseased',
      conf: '94%',
      sev: 'High Severity',
      img: '/static/samples/sample_tomato_blight.jpg'
    },
    potato: {
      crop: 'Potato (Solanum tuberosum)',
      disease: 'Late Blight (Phytophthora)',
      status: 'DISEASED',
      badgeClass: 'badge-diseased',
      conf: '91%',
      sev: 'Medium Severity',
      img: '/static/samples/sample_potato_blight.jpg'
    },
    rice: {
      crop: 'Rice (Oryza sativa)',
      disease: 'Healthy Leaf Specimen',
      status: 'HEALTHY',
      badgeClass: 'badge-healthy',
      conf: '98%',
      sev: 'Low (Optimum)',
      img: '/static/samples/sample_rice_healthy.jpg'
    },
    maize: {
      crop: 'Maize (Zea mays)',
      disease: 'Gray Leaf Spot (Cercospora)',
      status: 'DISEASED',
      badgeClass: 'badge-diseased',
      conf: '89%',
      sev: 'Medium Severity',
      img: '/static/samples/sample_maize_spot.jpg'
    }
  };

  demoTabs.forEach(tab => {
    tab.addEventListener('click', () => {
      demoTabs.forEach(t => t.classList.remove('active'));
      tab.classList.add('active');
      const key = tab.getAttribute('data-demo');
      const d = demoData[key];
      if (d && demoCrop) {
        demoCrop.textContent = d.disease;
        demoStatus.textContent = d.status;
        demoStatus.className = `badge ${d.badgeClass}`;
        demoConf.textContent = d.conf;
        demoSev.textContent = d.sev;
        if (demoImg) demoImg.src = d.img;
      }
    });
  });

  // 2. Interactive Crop Matrix Drawer
  const cropCards = document.querySelectorAll('.crop-card');
  const cropDetailDrawer = document.getElementById('crop-detail-drawer');
  const drawerTitle = document.getElementById('drawer-crop-title');
  const drawerDesc = document.getElementById('drawer-crop-desc');
  const drawerActionBtn = document.getElementById('drawer-scan-btn');

  const cropMeta = {
    tomato: {
      title: 'Tomato Agronomy Intelligence',
      desc: 'Trained to identify Early Blight (Alternaria solani), Late Blight, Septoria leaf spot, Bacterial speck, and Leaf Mold with fine lesion contour mapping.',
      action: '/scan?crop=tomato'
    },
    potato: {
      title: 'Potato Agronomy Intelligence',
      desc: 'Engineered for rapid identification of Late Blight (Phytophthora infestans) and Early Blight, minimizing tuber rot and systemic foliage breakdown.',
      action: '/scan?crop=potato'
    },
    rice: {
      title: 'Rice Agronomy Intelligence',
      desc: 'Detects Rice Blast (Magnaporthe oryzae), Brown Spot, and Bacterial Leaf Blight under variable field light and canopy conditions.',
      action: '/scan?crop=rice'
    },
    maize: {
      title: 'Maize Agronomy Intelligence',
      desc: 'Accurately diagnoses Northern Corn Leaf Blight, Common Rust, and Gray Leaf Spot to protect harvest yield and ear development.',
      action: '/scan?crop=maize'
    },
    chilli: {
      title: 'Chilli Agronomy Intelligence',
      desc: 'Identifies Chilli Leaf Curl Virus, Anthracnose, and Cercospora leaf spot, aiding early organic bio-pesticide timing.',
      action: '/scan?crop=chilli'
    }
  };

  cropCards.forEach(card => {
    card.addEventListener('click', () => {
      cropCards.forEach(c => c.classList.remove('active'));
      card.classList.add('active');
      const crop = card.getAttribute('data-crop');
      const info = cropMeta[crop];
      if (info && cropDetailDrawer) {
        drawerTitle.textContent = info.title;
        drawerDesc.textContent = info.desc;
        if (drawerActionBtn) drawerActionBtn.href = info.action;
      }
    });
  });

  // 3. FAQ Accordion
  const faqItems = document.querySelectorAll('.faq-item');
  faqItems.forEach(item => {
    const q = item.querySelector('.faq-question');
    if (q) {
      q.addEventListener('click', () => {
        const isOpen = item.classList.contains('open');
        faqItems.forEach(i => i.classList.remove('open'));
        if (!isOpen) item.classList.add('open');
      });
    }
  });
}

/* ==========================================================================
   6. Result Page Inspection Lens & Action Tools
   ========================================================================== */
function initResultPageTools() {
  const lens = document.getElementById('inspection-lens');
  const lensImg = document.getElementById('lens-img');

  if (lens && lensImg) {
    lens.addEventListener('mousemove', (e) => {
      const rect = lens.getBoundingClientRect();
      const x = ((e.clientX - rect.left) / rect.width) * 100;
      const y = ((e.clientY - rect.top) / rect.height) * 100;
      lensImg.style.transformOrigin = `${x}% ${y}%`;
      lensImg.style.transform = 'scale(2)';
    });

    lens.addEventListener('mouseleave', () => {
      lensImg.style.transformOrigin = 'center center';
      lensImg.style.transform = 'scale(1)';
    });
  }

  // Interactive Checklist check state
  const checkItems = document.querySelectorAll('.interactive-check-item input[type="checkbox"]');
  checkItems.forEach(cb => {
    cb.addEventListener('change', () => {
      const label = cb.closest('.interactive-check-item');
      if (cb.checked) {
        label.style.opacity = '0.6';
        label.style.textDecoration = 'line-through';
      } else {
        label.style.opacity = '1';
        label.style.textDecoration = 'none';
      }
    });
  });

  // Copy Diagnosis Report
  const copyBtn = document.getElementById('copy-report-btn');
  if (copyBtn) {
    copyBtn.addEventListener('click', () => {
      const disease = document.getElementById('report-disease-name')?.innerText || '';
      const crop = document.getElementById('report-crop-name')?.innerText || '';
      const conf = document.getElementById('report-confidence-val')?.innerText || '';
      const sev = document.getElementById('report-severity-val')?.innerText || '';

      const text = `🌱 PlantCare AI Diagnostic Summary\nCrop: ${crop}\nDiagnosis: ${disease}\nConfidence: ${conf}\nSeverity: ${sev}\nReport URL: ${window.location.href}`;
      navigator.clipboard.writeText(text).then(() => {
        showToast('Report copied to clipboard.', 'success');
      }).catch(() => {
        showToast('Could not copy report.', 'error');
      });
    });
  }

  // Print Report
  const printBtn = document.getElementById('print-report-btn');
  if (printBtn) {
    printBtn.addEventListener('click', () => {
      window.print();
    });
  }
}

/* ==========================================================================
   7. Table Search & Filtering (Dashboard & History)
   ========================================================================== */
function initTableFiltering() {
  const searchInput = document.getElementById('table-search-input');
  const table = document.getElementById('filterable-table');
  const filterPills = document.querySelectorAll('.table-filter-pill');

  if (!table) return;

  const rows = table.querySelectorAll('tbody tr');

  function applyFilters() {
    const q = (searchInput?.value || '').toLowerCase().trim();
    const activePill = document.querySelector('.table-filter-pill.active');
    const filterVal = activePill ? activePill.getAttribute('data-filter') : 'all';

    rows.forEach(row => {
      const text = row.textContent.toLowerCase();
      const status = row.getAttribute('data-status') || '';
      const crop = row.getAttribute('data-crop') || '';

      const matchesSearch = !q || text.includes(q);
      let matchesFilter = true;

      if (filterVal === 'healthy') {
        matchesFilter = status === 'healthy';
      } else if (filterVal === 'diseased') {
        matchesFilter = status === 'diseased';
      } else if (filterVal !== 'all') {
        matchesFilter = crop === filterVal;
      }

      row.style.display = (matchesSearch && matchesFilter) ? '' : 'none';
    });
  }

  if (searchInput) {
    searchInput.addEventListener('input', applyFilters);
  }

  filterPills.forEach(pill => {
    pill.addEventListener('click', () => {
      filterPills.forEach(p => p.classList.remove('active'));
      pill.classList.add('active');
      applyFilters();
    });
  });

  // Export to CSV
  const exportBtn = document.getElementById('export-csv-btn');
  if (exportBtn) {
    exportBtn.addEventListener('click', () => {
      let csv = [];
      const headers = Array.from(table.querySelectorAll('thead th')).map(th => `"${th.innerText.trim()}"`);
      csv.push(headers.join(','));

      rows.forEach(row => {
        if (row.style.display !== 'none') {
          const cols = Array.from(row.querySelectorAll('td')).map(td => `"${td.innerText.replace(/"/g, '""').trim()}"`);
          csv.push(cols.join(','));
        }
      });

      const blob = new Blob([csv.join('\n')], { type: 'text/csv' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `plantcare_scans_${new Date().toISOString().slice(0, 10)}.csv`;
      a.click();
      URL.revokeObjectURL(url);
      showToast('Exported scan records to CSV.', 'success');
    });
  }
}

/* ==========================================================================
   8. Toast & Flash Notification System
   ========================================================================== */
function initFlashDismiss() {
  const closeBtns = document.querySelectorAll('.flash-close');
  closeBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      const msg = btn.closest('.flash-message');
      if (msg) msg.remove();
    });
  });
}

function showToast(text, type = 'info') {
  let toastContainer = document.getElementById('toast-container');
  if (!toastContainer) {
    toastContainer = document.createElement('div');
    toastContainer.id = 'toast-container';
    toastContainer.style.position = 'fixed';
    toastContainer.style.bottom = '24px';
    toastContainer.style.right = '24px';
    toastContainer.style.zIndex = '9999';
    toastContainer.style.display = 'flex';
    toastContainer.style.flexDirection = 'column';
    toastContainer.style.gap = '8px';
    document.body.appendChild(toastContainer);
  }

  const toast = document.createElement('div');
  toast.className = `flash-message ${type}`;
  toast.style.margin = '0';
  toast.style.boxShadow = 'var(--shadow-lg)';
  toast.innerHTML = `
    <span>${text}</span>
    <button type="button" class="flash-close" style="margin-left: 1rem;">&times;</button>
  `;

  toast.querySelector('.flash-close').addEventListener('click', () => toast.remove());
  toastContainer.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transition = 'opacity 0.4s ease';
    setTimeout(() => toast.remove(), 400);
  }, 4000);
}
