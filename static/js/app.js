// SiloPrompts Web Application
// Frontend JavaScript

class SiloPrompts {
    constructor() {
        this.prompts = [];
        this.categories = {};
        this.tags = {};
        this.currentFilter = 'all';
        this.activeTags = [];
        this.favorites = new Set();
        this.sortOrder = localStorage.getItem('siloprompts_sort') || 'name-asc';
        this.init();
    }

    async init() {
        this.initTheme();
        this.loadFavorites();
        this.bindEvents();
        await this.loadCategories();
        await this.loadPrompts();
        await this.loadTags();
    }

    // Favorites
    loadFavorites() {
        try {
            const saved = localStorage.getItem('siloprompts_favorites') || '[]';
            const parsed = JSON.parse(saved);
            // Only keep section-level keys (must contain #)
            this.favorites = new Set(parsed.filter(key => key.includes('#')));
            if (this.favorites.size !== parsed.length) this.saveFavorites();
        } catch { this.favorites = new Set(); }
    }

    saveFavorites() {
        localStorage.setItem('siloprompts_favorites', JSON.stringify([...this.favorites]));
    }

    toggleFavorite(favKey) {
        if (this.favorites.has(favKey)) {
            this.favorites.delete(favKey);
        } else {
            this.favorites.add(favKey);
        }
        this.saveFavorites();
        this.renderCategories();
        // Re-render prompt cards so the ★ indicator updates live
        if (this.currentFilter !== '__favorites__') {
            this.applyFilters();
        }
    }

    getFavoriteKey(path, sectionIndex) {
        return `${path}#${sectionIndex}`;
    }

    getFavoriteCountForFile(path) {
        let count = 0;
        for (const key of this.favorites) {
            if (key.startsWith(path + '#')) count++;
        }
        return count;
    }

    filterByFavorites() {
        this.currentFilter = '__favorites__';
        document.querySelectorAll('.category-item').forEach(item => {
            item.classList.toggle('active', item.dataset.category === '__favorites__');
        });
        document.querySelectorAll('.pill[data-category]').forEach(pill => {
            pill.classList.remove('active');
        });
        document.getElementById('viewTitle').textContent = 'Favorites';
        document.getElementById('searchResults').style.display = 'none';
        document.getElementById('promptsList').style.display = 'grid';
        this.renderFavoritesSections();
    }

    async renderFavoritesSections() {
        const promptsList = document.getElementById('promptsList');

        if (this.favorites.size === 0) {
            promptsList.innerHTML = '<div class="loading">No favorite prompts yet. Open a prompt and click ☆ on any section to favorite it.</div>';
            document.getElementById('promptCount').textContent = 0;
            return;
        }

        promptsList.innerHTML = '<div class="loading">Loading favorites...</div>';

        // Group favorites by file path
        const byFile = {};
        for (const key of this.favorites) {
            const hashIdx = key.lastIndexOf('#');
            if (hashIdx < 0) continue;
            const path = key.substring(0, hashIdx);
            const sectionIdx = parseInt(key.substring(hashIdx + 1));
            if (!byFile[path]) byFile[path] = [];
            byFile[path].push(sectionIdx);
        }

        // Fetch each file and extract the favorited sections
        const cards = [];
        for (const [path, indices] of Object.entries(byFile)) {
            try {
                const response = await fetch(`/api/prompts/${path}`);
                if (!response.ok) continue;
                const data = await response.json();
                for (const idx of indices) {
                    const section = data.sections[idx];
                    if (!section) continue;
                    const favKey = this.getFavoriteKey(path, idx);
                    cards.push(`
                        <div class="prompt-card favorite-section-card" data-path="${path}" data-section="${idx}">
                            <button class="favorite-btn active" data-favkey="${favKey}" title="Remove from favorites">★</button>
                            <span class="prompt-category">${path}</span>
                            <h3 class="prompt-title">${section.title}</h3>
                            <div class="prompt-text favorite-preview">${this.escapeHtml(section.prompt.substring(0, 150))}${section.prompt.length > 150 ? '...' : ''}</div>
                        </div>
                    `);
                }
            } catch (e) {
                console.error(`Error loading favorites from ${path}:`, e);
            }
        }

        if (cards.length === 0) {
            promptsList.innerHTML = '<div class="loading">No favorite prompts found.</div>';
            document.getElementById('promptCount').textContent = 0;
            return;
        }

        promptsList.innerHTML = cards.join('');
        document.getElementById('promptCount').textContent = cards.length;

        // Click card to open the file detail
        document.querySelectorAll('.favorite-section-card').forEach(card => {
            card.addEventListener('click', () => {
                this.showPromptDetail(card.dataset.path);
            });
        });

        // Unfavorite button
        document.querySelectorAll('.favorite-section-card .favorite-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                this.toggleFavorite(btn.dataset.favkey);
                this.renderFavoritesSections();
            });
        });
    }

    // Tags
    async loadTags() {
        try {
            const response = await fetch('/api/tags');
            this.tags = await response.json();
            this.renderTags();
        } catch (error) {
            console.error('Error loading tags:', error);
        }
    }

    renderTags() {
        const tagFilter = document.getElementById('tagFilter');
        if (!tagFilter) return;
        const sortedTags = Object.entries(this.tags).sort((a, b) => a[0].localeCompare(b[0]));
        if (sortedTags.length === 0) {
            tagFilter.style.display = 'none';
            return;
        }
        tagFilter.style.display = 'flex';
        tagFilter.innerHTML = '<span class="tag-filter-label">Tags:</span>' +
            sortedTags.map(([tag, count]) => `
                <button class="tag-filter-pill ${this.activeTags.includes(tag) ? 'active' : ''}" data-tag="${tag}">
                    ${tag} <span class="tag-count">${count}</span>
                </button>
            `).join('');

        tagFilter.querySelectorAll('.tag-filter-pill').forEach(btn => {
            btn.addEventListener('click', () => this.toggleTagFilter(btn.dataset.tag));
        });
    }

    toggleTagFilter(tag) {
        const idx = this.activeTags.indexOf(tag);
        if (idx >= 0) {
            this.activeTags.splice(idx, 1);
        } else {
            this.activeTags.push(tag);
        }
        this.renderTags();
        this.applyFilters();
    }

    applyFilters() {
        // Favorites view is handled separately
        if (this.currentFilter === '__favorites__') {
            this.renderFavoritesSections();
            return;
        }

        let filtered = this.prompts;

        // Category filter
        if (this.currentFilter !== 'all') {
            filtered = filtered.filter(p => p.category === this.currentFilter);
        }

        // Tag filter (AND logic)
        if (this.activeTags.length > 0) {
            filtered = filtered.filter(p =>
                this.activeTags.every(tag => (p.tags || []).includes(tag))
            );
        }

        filtered = this.sortPrompts(filtered);
        this.renderPrompts(filtered);
    }

    sortPrompts(prompts) {
        const sorted = [...prompts];
        switch (this.sortOrder) {
            case 'name-asc': sorted.sort((a, b) => a.title.localeCompare(b.title)); break;
            case 'name-desc': sorted.sort((a, b) => b.title.localeCompare(a.title)); break;
            case 'modified': sorted.sort((a, b) => new Date(b.modified) - new Date(a.modified)); break;
            case 'size': sorted.sort((a, b) => b.size - a.size); break;
        }
        return sorted;
    }

    initTheme() {
        const saved = localStorage.getItem('theme') || 'dark';
        document.documentElement.setAttribute('data-theme', saved);
        this.updateThemeIcon(saved);
    }

    toggleTheme() {
        const current = document.documentElement.getAttribute('data-theme') || 'dark';
        const next = current === 'dark' ? 'light' : 'dark';
        document.documentElement.setAttribute('data-theme', next);
        localStorage.setItem('theme', next);
        this.updateThemeIcon(next);
    }

    updateThemeIcon(theme) {
        const btn = document.getElementById('themeToggle');
        btn.textContent = theme === 'dark' ? '☀️' : '🌙';
    }

    bindEvents() {
        // Search
        document.getElementById('searchBtn').addEventListener('click', () => this.handleSearch());
        document.getElementById('searchInput').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.handleSearch();
        });
        document.getElementById('clearBtn').addEventListener('click', () => this.clearSearch());

        // Modal
        document.getElementById('modalClose').addEventListener('click', () => this.closeModal());
        document.getElementById('promptModal').addEventListener('click', (e) => {
            if (e.target.id === 'promptModal') this.closeModal();
        });

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') this.closeModal();
            if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
                e.preventDefault();
                document.getElementById('searchInput').focus();
            }
        });

        // Category pills scroll fade
        const pillsContainer = document.getElementById('categoryFilter');
        const pillsWrapper = document.getElementById('categoryPillsWrapper');
        if (pillsContainer && pillsWrapper) {
            pillsContainer.addEventListener('scroll', () => {
                const atEnd = pillsContainer.scrollLeft + pillsContainer.clientWidth >= pillsContainer.scrollWidth - 10;
                pillsWrapper.classList.toggle('scrolled-end', atEnd);
            });
        }

        // Sidebar categories scroll fade
        const catList = document.getElementById('categoriesList');
        const catWrapper = document.getElementById('categoriesListWrapper');
        if (catList && catWrapper) {
            catList.addEventListener('scroll', () => {
                const atEnd = catList.scrollTop + catList.clientHeight >= catList.scrollHeight - 10;
                catWrapper.classList.toggle('scrolled-end', atEnd);
            });
        }

        // Theme toggle
        document.getElementById('themeToggle').addEventListener('click', () => this.toggleTheme());

        // Sort dropdown
        const sortToggle = document.getElementById('sortToggle');
        const sortDropdown = document.getElementById('sortDropdown');
        sortToggle.addEventListener('click', (e) => {
            e.stopPropagation();
            sortDropdown.style.display = sortDropdown.style.display === 'none' ? 'block' : 'none';
        });
        sortDropdown.querySelectorAll('.sort-option').forEach(btn => {
            if (btn.dataset.sort === this.sortOrder) {
                btn.classList.add('active');
            } else {
                btn.classList.remove('active');
            }
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                this.sortOrder = btn.dataset.sort;
                localStorage.setItem('siloprompts_sort', this.sortOrder);
                sortDropdown.querySelectorAll('.sort-option').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                sortDropdown.style.display = 'none';
                this.applyFilters();
            });
        });
        document.addEventListener('click', () => { sortDropdown.style.display = 'none'; });

        // New Prompt button
        document.getElementById('newPromptBtn').addEventListener('click', () => this.showCreateForm());

        // Import button
        document.getElementById('importBtn').addEventListener('click', () => this.showImportForm());

        // Tools menu (Backup & Restore)
        const toolsBtn = document.getElementById('toolsMenuBtn');
        const toolsDropdown = document.getElementById('toolsDropdown');
        toolsBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            toolsDropdown.classList.toggle('active');
        });
        document.addEventListener('click', () => toolsDropdown.classList.remove('active'));

        document.getElementById('backupBtn').addEventListener('click', () => {
            toolsDropdown.classList.remove('active');
            this.backupAll();
        });
        document.getElementById('restoreBtn').addEventListener('click', () => {
            toolsDropdown.classList.remove('active');
            this.showRestoreForm();
        });
    }

    async loadCategories() {
        try {
            const response = await fetch('/api/categories');
            this.categories = await response.json();

            this.renderCategories();
            this.updateStats();
        } catch (error) {
            console.error('Error loading categories:', error);
            this.showToast('Error loading categories', 'error');
        }
    }

    async loadPrompts() {
        try {
            const response = await fetch('/api/prompts');
            this.prompts = await response.json();

            this.renderPrompts();
            this.updateStats();
        } catch (error) {
            console.error('Error loading prompts:', error);
            this.showToast('Error loading prompts', 'error');
        }
    }

    renderCategories() {
        const categoriesList = document.getElementById('categoriesList');
        const categoryFilter = document.getElementById('categoryFilter');

        categoriesList.innerHTML = '';
        categoryFilter.innerHTML = '';
        const allPill = document.createElement('button');
        allPill.className = 'pill active';
        allPill.dataset.category = 'all';
        allPill.textContent = 'All';
        allPill.addEventListener('click', () => this.filterByCategory('all'));
        categoryFilter.appendChild(allPill);

        // Favorites sidebar item
        const favItem = document.createElement('div');
        favItem.className = `category-item favorites-item ${this.currentFilter === '__favorites__' ? 'active' : ''}`;
        favItem.dataset.category = '__favorites__';
        favItem.innerHTML = `
            <span class="category-name">★ Favorites</span>
            <span class="count-badge">${this.favorites.size}</span>
        `;
        favItem.addEventListener('click', () => this.filterByFavorites());
        categoriesList.appendChild(favItem);

        const sortedCategories = Object.entries(this.categories).sort((a, b) =>
            a[0].localeCompare(b[0])
        );

        sortedCategories.forEach(([key, category]) => {
            // Sidebar item
            const item = document.createElement('div');
            item.className = 'category-item';
            item.dataset.category = key;
            item.innerHTML = `
                <span class="category-name">${category.name}</span>
                <span class="count-badge">${category.count}</span>
            `;
            item.addEventListener('click', () => this.filterByCategory(key));
            categoriesList.appendChild(item);

            // Filter pill
            const pill = document.createElement('button');
            pill.className = 'pill';
            pill.dataset.category = key;
            pill.textContent = category.name;
            pill.addEventListener('click', () => this.filterByCategory(key));
            categoryFilter.appendChild(pill);
        });

        document.getElementById('categoryCount').textContent = sortedCategories.length;
    }

    renderPrompts(filteredPrompts = null) {
        const promptsList = document.getElementById('promptsList');
        const prompts = filteredPrompts || this.prompts;

        if (prompts.length === 0) {
            promptsList.innerHTML = '<div class="loading">No prompts found</div>';
            return;
        }

        promptsList.innerHTML = prompts.map(prompt => {
            const favCount = this.getFavoriteCountForFile(prompt.path);
            const tagsHtml = (prompt.tags || []).length > 0
                ? `<div class="prompt-tags">${prompt.tags.map(t => `<span class="tag-pill">${t}</span>`).join('')}</div>`
                : '';
            return `
                <div class="prompt-card" data-path="${prompt.path}">
                    ${favCount > 0 ? `<span class="card-fav-indicator" title="${favCount} favorited section${favCount !== 1 ? 's' : ''}">★ ${favCount}</span>` : ''}
                    <span class="prompt-category">${prompt.category}</span>
                    <h3 class="prompt-title">${prompt.title}</h3>
                    ${tagsHtml}
                    <div class="prompt-meta">
                        <span class="prompt-meta-item">
                            📝 ${prompt.sections} section${prompt.sections !== 1 ? 's' : ''}
                        </span>
                        <span class="prompt-meta-item">
                            📦 ${this.formatBytes(prompt.size)}
                        </span>
                    </div>
                </div>
            `;
        }).join('');

        // Add click handlers
        document.querySelectorAll('.prompt-card').forEach(card => {
            card.addEventListener('click', () => {
                this.showPromptDetail(card.dataset.path);
            });
        });

        document.getElementById('promptCount').textContent = prompts.length;
    }

    filterByCategory(category) {
        this.currentFilter = category;

        // Update UI
        document.querySelectorAll('.category-item').forEach(item => {
            item.classList.toggle('active', item.dataset.category === category);
        });

        document.querySelectorAll('.pill[data-category]').forEach(pill => {
            pill.classList.toggle('active', pill.dataset.category === category);
        });

        if (category === 'all') {
            document.getElementById('viewTitle').textContent = 'All Prompts';
        } else {
            document.getElementById('viewTitle').textContent =
                `${this.categories[category].name} Prompts`;
        }

        // Hide search results
        document.getElementById('searchResults').style.display = 'none';
        document.getElementById('promptsList').style.display = 'grid';
        this.applyFilters();
    }

    async handleSearch() {
        const query = document.getElementById('searchInput').value.trim();

        if (!query) {
            this.showToast('Please enter a search query', 'error');
            return;
        }

        try {
            const response = await fetch(`/api/search?q=${encodeURIComponent(query)}`);
            const data = await response.json();

            this.renderSearchResults(data);
            document.getElementById('clearBtn').style.display = 'inline-block';
        } catch (error) {
            console.error('Error searching:', error);
            this.showToast('Error performing search', 'error');
        }
    }

    renderSearchResults(data) {
        const searchResults = document.getElementById('searchResults');
        const searchResultsList = document.getElementById('searchResultsList');
        const promptsList = document.getElementById('promptsList');

        if (data.results.length === 0) {
            searchResultsList.innerHTML = '<div class="loading">No results found</div>';
        } else {
            searchResultsList.innerHTML = data.results.map(result => `
                <div class="search-result-item" data-path="${result.path}">
                    <div class="search-result-path">
                        📄 ${result.path}
                        <span style="color: var(--gray);">(${result.match_count} match${result.match_count !== 1 ? 'es' : ''})</span>
                    </div>
                    ${result.matches.map(match => `
                        <div class="search-match">→ ${this.escapeHtml(match.text)}</div>
                    `).join('')}
                </div>
            `).join('');

            // Add click handlers
            document.querySelectorAll('.search-result-item').forEach(item => {
                item.addEventListener('click', () => {
                    this.showPromptDetail(item.dataset.path);
                });
            });
        }

        document.getElementById('searchCount').textContent = data.results.length;
        searchResults.style.display = 'block';
        promptsList.style.display = 'none';
    }

    clearSearch() {
        document.getElementById('searchInput').value = '';
        document.getElementById('searchResults').style.display = 'none';
        document.getElementById('promptsList').style.display = 'grid';
        document.getElementById('clearBtn').style.display = 'none';
        this.filterByCategory(this.currentFilter);
    }

    async showPromptDetail(path) {
        const modal = document.getElementById('promptModal');
        const modalTitle = document.getElementById('modalTitle');
        const modalBody = document.getElementById('modalBody');
        const modalActions = document.getElementById('modalActions');

        modalBody.innerHTML = '<div class="loading">Loading prompt details...</div>';
        modalActions.innerHTML = '';
        modal.classList.add('active');

        try {
            const response = await fetch(`/api/prompts/${path}`);
            const data = await response.json();

            modalTitle.textContent = path;

            // Show download/edit/delete actions (favorites are per-section now)
            modalActions.innerHTML = `
                <button class="modal-action-btn download-btn" id="downloadPromptBtn">↑ Download</button>
                <button class="modal-action-btn edit-btn" id="editPromptBtn">Edit</button>
                <button class="modal-action-btn delete-btn" id="deletePromptBtn">Delete</button>
            `;
            document.getElementById('downloadPromptBtn').addEventListener('click', () => {
                window.location.href = `/api/prompts/${path}/download`;
            });
            document.getElementById('editPromptBtn').addEventListener('click', () => this.showEditForm(path));
            document.getElementById('deletePromptBtn').addEventListener('click', () => this.deletePrompt(path));

            if (data.sections.length === 0) {
                modalBody.innerHTML = '<p>No prompt sections found in this file.</p>';
                return;
            }

            // Store sections data for copy functionality
            this.currentSections = data.sections;

            modalBody.innerHTML = data.sections.map((section, index) => {
                const favKey = this.getFavoriteKey(path, index);
                const isFav = this.favorites.has(favKey);
                return `
                    <div class="prompt-section" data-section-index="${index}">
                        <div class="prompt-section-header">
                            <h3 class="prompt-section-title">${section.title}</h3>
                            <div class="section-actions">
                                <button class="section-fav-btn ${isFav ? 'active' : ''}" data-favkey="${favKey}" title="${isFav ? 'Remove from favorites' : 'Add to favorites'}">
                                    ${isFav ? '★' : '☆'}
                                </button>
                                <button class="copy-btn" data-index="${index}">
                                    📋 Copy
                                </button>
                            </div>
                        </div>
                        <div class="prompt-text">${this.escapeHtml(section.prompt)}</div>
                    </div>
                `;
            }).join('');

            // Add copy handlers
            document.querySelectorAll('.copy-btn').forEach(btn => {
                btn.addEventListener('click', (e) => {
                    e.stopPropagation();
                    const sectionIndex = parseInt(btn.dataset.index);
                    const promptText = this.currentSections[sectionIndex].prompt;
                    this.copyToClipboard(promptText);
                });
            });

            // Add section favorite handlers
            document.querySelectorAll('.section-fav-btn').forEach(btn => {
                btn.addEventListener('click', (e) => {
                    e.stopPropagation();
                    this.toggleFavorite(btn.dataset.favkey);
                    const isFav = this.favorites.has(btn.dataset.favkey);
                    btn.className = `section-fav-btn ${isFav ? 'active' : ''}`;
                    btn.textContent = isFav ? '★' : '☆';
                    btn.title = isFav ? 'Remove from favorites' : 'Add to favorites';
                });
            });

        } catch (error) {
            console.error('Error loading prompt detail:', error);
            modalBody.innerHTML = '<p>Error loading prompt details.</p>';
            this.showToast('Error loading prompt', 'error');
        }
    }

    showCreateForm() {
        const modal = document.getElementById('promptModal');
        const modalTitle = document.getElementById('modalTitle');
        const modalBody = document.getElementById('modalBody');
        const modalActions = document.getElementById('modalActions');

        modalTitle.textContent = 'New Prompt';
        modalActions.innerHTML = '';
        modal.classList.add('active');

        this.renderEditForm({ title: '', category: '', sections: [], isNew: true, tags: [] });
    }

    showImportForm() {
        const modal = document.getElementById('promptModal');
        const modalTitle = document.getElementById('modalTitle');
        const modalBody = document.getElementById('modalBody');
        const modalActions = document.getElementById('modalActions');

        modalTitle.textContent = 'Import Prompt';
        modal.classList.add('active');

        const categoryOptions = Object.keys(this.categories).sort();
        modalBody.innerHTML = `
            <form id="importForm" class="edit-form">
                <div class="form-group">
                    <label class="form-label">Select .md File</label>
                    <input type="file" class="form-input import-file-input" id="importFile" accept=".md">
                </div>
                <div class="form-group">
                    <label class="form-label">Category</label>
                    <select class="form-select" id="importCategory">
                        ${categoryOptions.map(c => `<option value="${c}">${c}</option>`).join('')}
                        <option value="__new__">+ New Category</option>
                    </select>
                </div>
                <div class="form-group" id="importNewCategoryGroup" style="display:none">
                    <label class="form-label">New Category Name</label>
                    <input type="text" class="form-input" id="importNewCategory" placeholder="e.g., testing">
                </div>
                <div id="importPreview" class="import-preview" style="display:none">
                    <label class="form-label">Preview</label>
                    <pre class="prompt-text" id="importPreviewText"></pre>
                </div>
            </form>
        `;

        modalActions.innerHTML = `
            <button class="modal-action-btn cancel-btn" id="cancelImportBtn">Cancel</button>
            <button class="modal-action-btn save-btn" id="uploadBtn">Upload</button>
        `;

        document.getElementById('importCategory').addEventListener('change', (e) => {
            document.getElementById('importNewCategoryGroup').style.display =
                e.target.value === '__new__' ? 'block' : 'none';
        });

        document.getElementById('importFile').addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = (ev) => {
                    document.getElementById('importPreview').style.display = 'block';
                    document.getElementById('importPreviewText').textContent = ev.target.result.substring(0, 500) + (ev.target.result.length > 500 ? '\n...' : '');
                };
                reader.readAsText(file);
            }
        });

        document.getElementById('cancelImportBtn').addEventListener('click', () => this.closeModal());
        document.getElementById('uploadBtn').addEventListener('click', () => this.importPrompt());
    }

    async importPrompt() {
        const fileInput = document.getElementById('importFile');
        if (!fileInput.files.length) {
            this.showToast('Please select a file', 'error');
            return;
        }

        const categorySelect = document.getElementById('importCategory');
        let category = categorySelect.value;
        if (category === '__new__') {
            category = document.getElementById('importNewCategory').value.trim();
            if (!category) {
                this.showToast('Category name is required', 'error');
                return;
            }
        }

        const formData = new FormData();
        formData.append('file', fileInput.files[0]);
        formData.append('category', category);

        try {
            const response = await fetch('/api/prompts/import', {
                method: 'POST',
                body: formData
            });
            const data = await response.json();

            if (!response.ok) {
                this.showToast(data.error || 'Import failed', 'error');
                return;
            }

            this.showToast(data.message, 'success');
            await this.loadCategories();
            await this.loadPrompts();
            await this.loadTags();
            this.showPromptDetail(data.path);
        } catch (error) {
            console.error('Error importing prompt:', error);
            this.showToast('Error importing prompt', 'error');
        }
    }

    backupAll() {
        window.location.href = '/api/backup';
        this.showToast('Backup download started', 'success');
    }

    showRestoreForm() {
        const modal = document.getElementById('promptModal');
        const modalTitle = document.getElementById('modalTitle');
        const modalBody = document.getElementById('modalBody');
        const modalActions = document.getElementById('modalActions');

        modalTitle.textContent = 'Restore from Backup';
        modalBody.innerHTML = `
            <form class="edit-form">
                <div class="form-group">
                    <label class="form-label">Select ZIP backup file</label>
                    <input type="file" id="restoreFile" accept=".zip" class="form-input import-file-input">
                </div>
                <div class="form-group">
                    <label class="form-label">If a prompt already exists:</label>
                    <div class="radio-group">
                        <label class="radio-label">
                            <input type="radio" name="restoreMode" value="skip" checked> Skip existing (keep current)
                        </label>
                        <label class="radio-label">
                            <input type="radio" name="restoreMode" value="overwrite"> Overwrite with backup version
                        </label>
                    </div>
                </div>
                <div id="restorePreview" class="import-preview" style="display:none;"></div>
            </form>
        `;

        modalActions.innerHTML = `
            <button class="modal-action-btn cancel-btn" id="cancelRestoreBtn">Cancel</button>
            <button class="modal-action-btn save-btn" id="restoreUploadBtn">Restore</button>
        `;

        document.getElementById('cancelRestoreBtn').addEventListener('click', () => this.closeModal());
        document.getElementById('restoreUploadBtn').addEventListener('click', () => this.restoreBackup());
        modal.classList.add('active');
    }

    async restoreBackup() {
        const fileInput = document.getElementById('restoreFile');
        const file = fileInput?.files[0];

        if (!file) {
            this.showToast('Please select a ZIP file', 'error');
            return;
        }

        if (!file.name.endsWith('.zip')) {
            this.showToast('Only .zip files are allowed', 'error');
            return;
        }

        const mode = document.querySelector('input[name="restoreMode"]:checked')?.value || 'skip';
        const formData = new FormData();
        formData.append('file', file);
        formData.append('mode', mode);

        try {
            const response = await fetch('/api/restore', { method: 'POST', body: formData });
            const data = await response.json();

            if (!response.ok) {
                this.showToast(data.error || 'Restore failed', 'error');
                return;
            }

            // Show results summary in the modal
            const preview = document.getElementById('restorePreview');
            preview.style.display = 'block';
            preview.innerHTML = `
                <h4>Restore Complete</h4>
                <p><strong>Created:</strong> ${data.created.length} prompt(s)</p>
                <p><strong>Skipped:</strong> ${data.skipped.length} prompt(s)</p>
                <p><strong>Overwritten:</strong> ${data.overwritten.length} prompt(s)</p>
                ${data.errors.length ? `<p><strong>Errors:</strong> ${data.errors.length}</p>` : ''}
            `;

            this.showToast(data.message, 'success');
            await this.loadCategories();
            await this.loadPrompts();
            await this.loadTags();
        } catch (error) {
            console.error('Error restoring backup:', error);
            this.showToast('Error restoring backup', 'error');
        }
    }

    async showEditForm(path) {
        const modalTitle = document.getElementById('modalTitle');
        const modalBody = document.getElementById('modalBody');
        const modalActions = document.getElementById('modalActions');

        modalBody.innerHTML = '<div class="loading">Loading...</div>';
        modalActions.innerHTML = '';

        try {
            const response = await fetch(`/api/prompts/${path}`);
            const data = await response.json();

            const parts = path.split('/');
            const category = parts.slice(0, -1).join('/');

            modalTitle.textContent = `Edit: ${path}`;
            this.renderEditForm({
                title: data.sections.length > 0 ? '' : '',
                category,
                sections: data.sections,
                isNew: false,
                path,
                rawTitle: data.raw.match(/^#\s+(.+)$/m)?.[1] || '',
                tags: data.tags || []
            });
        } catch (error) {
            console.error('Error loading prompt for edit:', error);
            this.showToast('Error loading prompt', 'error');
        }
    }

    renderEditForm({ title, category, sections, isNew, path, rawTitle, tags }) {
        const modalBody = document.getElementById('modalBody');
        const modalActions = document.getElementById('modalActions');
        const categoryOptions = Object.keys(this.categories).sort();

        const displayTitle = rawTitle || title;
        const tagsStr = (tags || []).join(', ');

        modalBody.innerHTML = `
            <form id="promptEditForm" class="edit-form">
                <div class="form-group">
                    <label class="form-label">Title</label>
                    <input type="text" class="form-input" id="editTitle" value="${this.escapeHtml(displayTitle)}" placeholder="e.g., Code Review Prompts" required>
                </div>
                <div class="form-row">
                    <div class="form-group" style="flex:1">
                        <label class="form-label">Category</label>
                        <select class="form-select" id="editCategory" ${isNew ? '' : 'disabled'}>
                            ${categoryOptions.map(c => `<option value="${c}" ${c === category ? 'selected' : ''}>${c}</option>`).join('')}
                            <option value="__new__">+ New Category</option>
                        </select>
                    </div>
                    <div class="form-group" id="newCategoryGroup" style="flex:1; display:none">
                        <label class="form-label">New Category Name</label>
                        <input type="text" class="form-input" id="editNewCategory" placeholder="e.g., testing">
                    </div>
                    ${isNew ? `
                    <div class="form-group" style="flex:1">
                        <label class="form-label">Filename</label>
                        <input type="text" class="form-input" id="editFilename" placeholder="e.g., my-prompts.md">
                    </div>
                    ` : ''}
                </div>
                <div class="form-group">
                    <label class="form-label">Tags</label>
                    <input type="text" class="form-input" id="editTags" value="${this.escapeHtml(tagsStr)}" placeholder="e.g., python, debugging, security (comma-separated)">
                </div>
                <div class="form-group">
                    <label class="form-label">Sections</label>
                    <div id="sectionsContainer">
                        ${sections.map((s, i) => this.renderSectionField(i, s.title, s.prompt)).join('')}
                    </div>
                    <button type="button" class="add-section-btn" id="addSectionBtn">+ Add Section</button>
                </div>
            </form>
        `;

        modalActions.innerHTML = `
            <button class="modal-action-btn cancel-btn" id="cancelEditBtn">Cancel</button>
            <button class="modal-action-btn save-btn" id="savePromptBtn">Save</button>
        `;

        // Event listeners
        const editCategoryEl = document.getElementById('editCategory');
        const newCategoryGroupEl = document.getElementById('newCategoryGroup');
        editCategoryEl.addEventListener('change', (e) => {
            newCategoryGroupEl.style.display = e.target.value === '__new__' ? 'block' : 'none';
        });
        // Show new category input immediately if it's the only/default option
        if (editCategoryEl.value === '__new__') {
            newCategoryGroupEl.style.display = 'block';
        }

        if (isNew) {
            document.getElementById('editTitle').addEventListener('input', (e) => {
                const filenameInput = document.getElementById('editFilename');
                if (!filenameInput.dataset.manual) {
                    const slug = this.slugify(e.target.value);
                    filenameInput.value = slug ? slug + '.md' : '';
                }
            });
            document.getElementById('editFilename').addEventListener('input', function() {
                this.dataset.manual = this.value ? 'true' : '';
            });
        }

        document.getElementById('addSectionBtn').addEventListener('click', () => this.addSectionField());
        document.getElementById('savePromptBtn').addEventListener('click', () => this.savePrompt(isNew, path));
        document.getElementById('cancelEditBtn').addEventListener('click', () => {
            if (isNew) {
                this.closeModal();
            } else {
                this.showPromptDetail(path);
            }
        });

        this.bindSectionControls();

        // Add first section if empty
        if (sections.length === 0) {
            this.addSectionField();
        }
    }

    renderSectionField(index, title = '', prompt = '') {
        return `
            <div class="section-editor" data-index="${index}">
                <div class="section-editor-header">
                    <span class="section-number">#${index + 1}</span>
                    <div class="section-controls">
                        <button type="button" class="section-ctrl-btn move-up-btn" title="Move up">&#9650;</button>
                        <button type="button" class="section-ctrl-btn move-down-btn" title="Move down">&#9660;</button>
                        <button type="button" class="section-ctrl-btn remove-section-btn" title="Remove">&#10005;</button>
                    </div>
                </div>
                <input type="text" class="form-input section-title" value="${this.escapeHtml(title)}" placeholder="e.g., General Code Review">
                <textarea class="form-textarea section-prompt" placeholder="You are an expert code reviewer. Review the following code for:\n- Bug risks and logic errors\n- Security vulnerabilities\n- Performance improvements\n- Code readability and best practices\n\nProvide specific, actionable feedback with examples." rows="10">${this.escapeHtml(prompt)}</textarea>
            </div>
        `;
    }

    addSectionField() {
        const container = document.getElementById('sectionsContainer');
        const index = container.children.length;
        const div = document.createElement('div');
        div.innerHTML = this.renderSectionField(index);
        const sectionEl = div.firstElementChild;
        container.appendChild(sectionEl);
        this.bindSectionControls();
        sectionEl.querySelector('.section-title').focus();
    }

    bindSectionControls() {
        document.querySelectorAll('.move-up-btn').forEach(btn => {
            btn.onclick = (e) => {
                const section = e.target.closest('.section-editor');
                const prev = section.previousElementSibling;
                if (prev) {
                    section.parentNode.insertBefore(section, prev);
                    this.renumberSections();
                }
            };
        });

        document.querySelectorAll('.move-down-btn').forEach(btn => {
            btn.onclick = (e) => {
                const section = e.target.closest('.section-editor');
                const next = section.nextElementSibling;
                if (next) {
                    section.parentNode.insertBefore(next, section);
                    this.renumberSections();
                }
            };
        });

        document.querySelectorAll('.remove-section-btn').forEach(btn => {
            btn.onclick = (e) => {
                const container = document.getElementById('sectionsContainer');
                if (container.children.length <= 1) {
                    this.showToast('Need at least one section', 'error');
                    return;
                }
                e.target.closest('.section-editor').remove();
                this.renumberSections();
            };
        });
    }

    renumberSections() {
        document.querySelectorAll('.section-editor').forEach((el, i) => {
            el.dataset.index = i;
            el.querySelector('.section-number').textContent = `#${i + 1}`;
        });
    }

    async savePrompt(isNew, existingPath) {
        const title = document.getElementById('editTitle').value.trim();
        if (!title) {
            this.showToast('Title is required', 'error');
            return;
        }

        const sectionEls = document.querySelectorAll('.section-editor');
        const sections = [];
        for (const el of sectionEls) {
            const sTitle = el.querySelector('.section-title').value.trim();
            const sPrompt = el.querySelector('.section-prompt').value.trim();
            if (!sTitle || !sPrompt) {
                this.showToast('All sections need a title and prompt text', 'error');
                return;
            }
            sections.push({ title: sTitle, prompt: sPrompt });
        }

        // Parse tags
        const tagsInput = document.getElementById('editTags').value;
        const tags = tagsInput ? tagsInput.split(',').map(t => t.trim().toLowerCase()).filter(Boolean) : [];

        try {
            let response;
            if (isNew) {
                const categorySelect = document.getElementById('editCategory');
                let category = categorySelect.value;
                if (category === '__new__') {
                    category = document.getElementById('editNewCategory').value.trim();
                    if (!category) {
                        this.showToast('Category name is required', 'error');
                        return;
                    }
                }
                let filename = document.getElementById('editFilename').value.trim() || this.slugify(title);
                // Strip .md suffix — backend adds it
                filename = filename.replace(/\.md$/i, '');
                if (!filename) {
                    this.showToast('Filename is required', 'error');
                    return;
                }

                response = await fetch('/api/prompts', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ category, filename, title, sections, tags })
                });
            } else {
                response = await fetch(`/api/prompts/${existingPath}`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ title, sections, tags })
                });
            }

            const data = await response.json();
            if (!response.ok) {
                this.showToast(data.error || 'Failed to save', 'error');
                return;
            }

            this.showToast(data.message, 'success');
            await this.loadCategories();
            await this.loadPrompts();
            await this.loadTags();
            this.showPromptDetail(data.path);
        } catch (error) {
            console.error('Error saving prompt:', error);
            this.showToast('Error saving prompt', 'error');
        }
    }

    async deletePrompt(path) {
        if (!confirm(`Delete "${path}"? This cannot be undone.`)) return;

        const deleteEmpty = confirm('Also delete the category folder if empty?');

        try {
            const response = await fetch(
                `/api/prompts/${path}?delete_empty_category=${deleteEmpty}`,
                { method: 'DELETE' }
            );
            const data = await response.json();

            if (!response.ok) {
                this.showToast(data.error || 'Failed to delete', 'error');
                return;
            }

            this.showToast('Prompt deleted', 'success');
            // Remove all section favorites for this file
            for (const key of [...this.favorites]) {
                if (key.startsWith(path + '#')) this.favorites.delete(key);
            }
            this.saveFavorites();
            this.closeModal();
            await this.loadCategories();
            await this.loadPrompts();
            await this.loadTags();
        } catch (error) {
            console.error('Error deleting prompt:', error);
            this.showToast('Error deleting prompt', 'error');
        }
    }

    slugify(text) {
        return text.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
    }

    closeModal() {
        const modal = document.getElementById('promptModal');
        modal.classList.remove('active');
        document.getElementById('modalActions').innerHTML = '';
    }

    async copyToClipboard(text) {
        try {
            await navigator.clipboard.writeText(text);
            this.showToast('Copied to clipboard!', 'success');
        } catch (error) {
            console.error('Error copying to clipboard:', error);
            this.showToast('Failed to copy. Please copy manually.', 'error');
        }
    }

    showToast(message, type = 'success') {
        const toast = document.getElementById('toast');
        toast.textContent = message;
        toast.className = `toast show ${type}`;

        setTimeout(() => {
            toast.classList.remove('show');
        }, 3000);
    }

    updateStats() {
        document.getElementById('totalPrompts').textContent = this.prompts.length;
        document.getElementById('totalCategories').textContent = Object.keys(this.categories).length;
    }

    formatBytes(bytes) {
        if (bytes < 1024) return bytes + ' B';
        if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
        return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new SiloPrompts();
});
