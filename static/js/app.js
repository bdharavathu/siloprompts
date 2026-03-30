// SiloPrompts Web Application
// Frontend JavaScript

class SiloPrompts {
    constructor() {
        this.prompts = [];
        this.categories = {};
        this.currentFilter = 'all';
        this.init();
    }

    async init() {
        this.initTheme();
        this.bindEvents();
        await this.loadCategories();
        await this.loadPrompts();
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

        // ESC key to close modal
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') this.closeModal();
        });

        // Theme toggle
        document.getElementById('themeToggle').addEventListener('click', () => this.toggleTheme());
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

        promptsList.innerHTML = prompts.map(prompt => `
            <div class="prompt-card" data-path="${prompt.path}">
                <span class="prompt-category">${prompt.category}</span>
                <h3 class="prompt-title">${prompt.title}</h3>
                <div class="prompt-meta">
                    <span class="prompt-meta-item">
                        📝 ${prompt.sections} section${prompt.sections !== 1 ? 's' : ''}
                    </span>
                    <span class="prompt-meta-item">
                        📦 ${this.formatBytes(prompt.size)}
                    </span>
                </div>
            </div>
        `).join('');

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

        document.querySelectorAll('.pill').forEach(pill => {
            pill.classList.toggle('active', pill.dataset.category === category);
        });

        // Filter prompts
        if (category === 'all') {
            document.getElementById('viewTitle').textContent = 'All Prompts';
            this.renderPrompts();
        } else {
            document.getElementById('viewTitle').textContent =
                `${this.categories[category].name} Prompts`;
            const filtered = this.prompts.filter(p => p.category === category);
            this.renderPrompts(filtered);
        }

        // Hide search results
        document.getElementById('searchResults').style.display = 'none';
        document.getElementById('promptsList').style.display = 'grid';
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

        modalBody.innerHTML = '<div class="loading">Loading prompt details...</div>';
        modal.classList.add('active');

        try {
            const response = await fetch(`/api/prompts/${path}`);
            const data = await response.json();

            modalTitle.textContent = path;

            if (data.sections.length === 0) {
                modalBody.innerHTML = '<p>No prompt sections found in this file.</p>';
                return;
            }

            // Store sections data for copy functionality
            this.currentSections = data.sections;

            modalBody.innerHTML = data.sections.map((section, index) => `
                <div class="prompt-section" data-section-index="${index}">
                    <div class="prompt-section-header">
                        <h3 class="prompt-section-title">${section.title}</h3>
                        <button class="copy-btn" data-index="${index}">
                            📋 Copy
                        </button>
                    </div>
                    <div class="prompt-text">${this.escapeHtml(section.prompt)}</div>
                </div>
            `).join('');

            // Add copy handlers
            document.querySelectorAll('.copy-btn').forEach(btn => {
                btn.addEventListener('click', (e) => {
                    e.stopPropagation();
                    const sectionIndex = parseInt(btn.dataset.index);
                    const promptText = this.currentSections[sectionIndex].prompt;
                    this.copyToClipboard(promptText);
                });
            });

        } catch (error) {
            console.error('Error loading prompt detail:', error);
            modalBody.innerHTML = '<p>Error loading prompt details.</p>';
            this.showToast('Error loading prompt', 'error');
        }
    }

    closeModal() {
        document.getElementById('promptModal').classList.remove('active');
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
