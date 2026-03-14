/* ═══════════════════════════════════════════════════════════════════════════
   STUDENT HUB — Search, Filter, Theme, Bookmarks & Ratings
   ═══════════════════════════════════════════════════════════════════════════ */

(function () {
    'use strict';

    // ─── DOM References ───────────────────────────────────────────────────
    var searchInput = document.getElementById('searchInput') || document.getElementById('marketplaceSearch');
    var filterBar = document.getElementById('filterBar');
    var noResults = document.getElementById('noResults');
    var navbar = document.getElementById('main-navbar');
    var themeToggle = document.getElementById('themeToggle');
    var themeIcon = document.getElementById('themeIcon');

    var filterPills = filterBar ? filterBar.querySelectorAll('.filter-pill') : [];
    var categoryBlocks = document.querySelectorAll('.category-block');

    var activeCategory = 'all';

    // ═══════════════════════════════════════════════════════════════════════
    //  THEME TOGGLE
    // ═══════════════════════════════════════════════════════════════════════
    function getStoredTheme() {
        return localStorage.getItem('studenthub-theme') || 'dark';
    }

    function setTheme(theme) {
        var html = document.documentElement;
        html.setAttribute('data-theme', theme);
        html.setAttribute('data-bs-theme', theme);
        localStorage.setItem('studenthub-theme', theme);

        if (themeIcon) {
            if (theme === 'dark') {
                themeIcon.className = 'bi bi-sun-fill';
            } else {
                themeIcon.className = 'bi bi-moon-stars-fill';
            }
        }
    }

    // Apply stored theme on load
    setTheme(getStoredTheme());

    // Toggle on click
    if (themeToggle) {
        themeToggle.addEventListener('click', function () {
            var current = document.documentElement.getAttribute('data-theme');
            setTheme(current === 'dark' ? 'light' : 'dark');
        });
    }

    // ═══════════════════════════════════════════════════════════════════════
    //  NAVBAR SCROLL EFFECT
    // ═══════════════════════════════════════════════════════════════════════
    function handleScroll() {
        if (navbar && window.scrollY > 20) {
            navbar.classList.add('scrolled');
        } else if (navbar) {
            navbar.classList.remove('scrolled');
        }
    }
    window.addEventListener('scroll', handleScroll, { passive: true });

    // ═══════════════════════════════════════════════════════════════════════
    //  KEYBOARD SHORTCUT (Ctrl+K)
    // ═══════════════════════════════════════════════════════════════════════
    document.addEventListener('keydown', function (e) {
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            if (searchInput) {
                searchInput.focus();
                searchInput.select();
            }
        }
        if (e.key === 'Escape' && searchInput && document.activeElement === searchInput) {
            searchInput.value = '';
            searchInput.blur();
            applyFilters();
        }
    });

    // ═══════════════════════════════════════════════════════════════════════
    //  CATEGORY FILTER
    // ═══════════════════════════════════════════════════════════════════════
    filterPills.forEach(function (pill) {
        pill.addEventListener('click', function () {
            filterPills.forEach(function (p) { p.classList.remove('active'); });
            pill.classList.add('active');
            activeCategory = pill.getAttribute('data-category');
            applyFilters();
        });
    });

    // ═══════════════════════════════════════════════════════════════════════
    //  LIVE SEARCH
    // ═══════════════════════════════════════════════════════════════════════
    if (searchInput) {
        searchInput.addEventListener('input', debounce(function () {
            applyFilters();
        }, 150));
    }

    // ═══════════════════════════════════════════════════════════════════════
    //  CORE FILTER LOGIC
    // ═══════════════════════════════════════════════════════════════════════
    function applyFilters() {
        var query = searchInput ? searchInput.value.trim().toLowerCase() : '';
        var visibleCount = 0;

        categoryBlocks.forEach(function (block) {
            var blockCategory = block.getAttribute('data-category-block');
            var categoryMatch = (activeCategory === 'all' || activeCategory === blockCategory);

            if (!categoryMatch) {
                block.classList.add('hidden');
                return;
            }

            var cards = block.querySelectorAll('.tool-card-col');
            var categoryVisibleCount = 0;

            cards.forEach(function (card) {
                var name = card.getAttribute('data-tool-name') || '';
                var desc = card.getAttribute('data-tool-desc') || '';
                var matchesSearch = !query || name.indexOf(query) !== -1 || desc.indexOf(query) !== -1;

                if (matchesSearch) {
                    card.classList.remove('hidden');
                    categoryVisibleCount++;
                    visibleCount++;
                } else {
                    card.classList.add('hidden');
                }
            });

            if (categoryVisibleCount === 0) {
                block.classList.add('hidden');
            } else {
                block.classList.remove('hidden');
            }
        });

        if (noResults) {
            if (visibleCount === 0) {
                noResults.classList.remove('d-none');
            } else {
                noResults.classList.add('d-none');
            }
        }
    }

    // ═══════════════════════════════════════════════════════════════════════
    //  DEBOUNCE UTILITY
    // ═══════════════════════════════════════════════════════════════════════
    function debounce(func, wait) {
        var timeout;
        return function () {
            var context = this;
            var args = arguments;
            clearTimeout(timeout);
            timeout = setTimeout(function () {
                func.apply(context, args);
            }, wait);
        };
    }

    // ═══════════════════════════════════════════════════════════════════════
    //  SMOOTH SCROLL FOR NAV LINKS
    // ═══════════════════════════════════════════════════════════════════════
    document.querySelectorAll('a[href^="#"]').forEach(function (anchor) {
        anchor.addEventListener('click', function (e) {
            var targetId = this.getAttribute('href');
            if (targetId === '#') return;
            var target = document.querySelector(targetId);
            if (target) {
                e.preventDefault();
                target.scrollIntoView({ behavior: 'smooth', block: 'start' });
                var navCollapse = document.getElementById('navContent');
                if (navCollapse) {
                    var bsCollapse = bootstrap.Collapse.getInstance(navCollapse);
                    if (bsCollapse) bsCollapse.hide();
                }
            }
        });
    });

    // ═══════════════════════════════════════════════════════════════════════
    //  INTERSECTION OBSERVER FOR SCROLL ANIMATIONS
    // ═══════════════════════════════════════════════════════════════════════
    if ('IntersectionObserver' in window) {
        var animObserver = new IntersectionObserver(function (entries) {
            entries.forEach(function (entry) {
                if (entry.isIntersecting) {
                    entry.target.style.animationPlayState = 'running';
                    animObserver.unobserve(entry.target);
                }
            });
        }, { threshold: 0.1 });

        categoryBlocks.forEach(function (block) {
            block.style.animationPlayState = 'paused';
            animObserver.observe(block);
        });
    }

})();


// ═══════════════════════════════════════════════════════════════════════════
//  BOOKMARK TOGGLE (global scope — called from onclick)
// ═══════════════════════════════════════════════════════════════════════════
function toggleBookmark(btn) {
    if (typeof IS_AUTHENTICATED === 'undefined' || !IS_AUTHENTICATED) {
        window.location.href = typeof SIGNIN_URL !== 'undefined' ? SIGNIN_URL : '/signin';
        return;
    }

    var itemName = btn.getAttribute('data-item');
    var itemType = btn.getAttribute('data-type');
    var category = btn.getAttribute('data-category');

    fetch('/api/bookmark', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            item_name: itemName,
            item_type: itemType,
            category: category,
        }),
    })
        .then(function (res) { return res.json(); })
        .then(function (data) {
            var icon = btn.querySelector('i');
            if (data.bookmarked) {
                btn.classList.add('bookmarked');
                icon.className = 'bi bi-heart-fill';
            } else {
                btn.classList.remove('bookmarked');
                icon.className = 'bi bi-heart';
            }
        })
        .catch(function (err) {
            console.error('Bookmark error:', err);
        });
}


// ═══════════════════════════════════════════════════════════════════════════
//  STAR RATING (global scope — called from onclick)
// ═══════════════════════════════════════════════════════════════════════════
function submitRating(toolName, score, starEl) {
    if (typeof IS_AUTHENTICATED === 'undefined' || !IS_AUTHENTICATED) {
        window.location.href = typeof SIGNIN_URL !== 'undefined' ? SIGNIN_URL : '/signin';
        return;
    }

    // Quick visual feedback on the stars
    var container = starEl.closest('.star-rating');
    var stars = container.querySelectorAll('.star-btn');
    stars.forEach(function (s, i) {
        if (i < score) {
            s.className = 'bi bi-star-fill star-btn';
        } else {
            s.className = 'bi bi-star star-btn';
        }
    });

    fetch('/api/rate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            tool_name: toolName,
            score: score,
            review: '',
        }),
    })
        .then(function (res) { return res.json(); })
        .then(function (data) {
            if (data.success) {
                var avgSpan = container.querySelector('.rating-avg');
                if (avgSpan) {
                    avgSpan.innerHTML = data.avg + ' <small>(' + data.count + ')</small>';
                }
            }
        })
        .catch(function (err) {
            console.error('Rating error:', err);
        });
}
