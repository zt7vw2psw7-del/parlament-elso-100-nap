/**
 * app.js - Main Application Logic for US Midterm Elections 2026 Dashboard
 */

document.addEventListener('DOMContentLoaded', () => {
  App.init();
});

const App = {
  data: {
    projections: null,
    polls: null,
    news: null,
    senate_seats: null,
    trump_tracker: null
  },
  activeTab: 'overview',
  activePollFilter: 'all',
  pollSearchQuery: '',
  activeSenateFilter: 'all',
  senateSearchQuery: '',
  activeNewsSubtab: 'daily',

  async init() {
    this.initTheme();
    this.initCountdown();
    this.initEventListeners();
    await this.loadAllData();
    this.render();
  },

  // Dark/Light Theme Handler
  initTheme() {
    const savedTheme = localStorage.getItem('midterm_theme') || 'dark';
    document.documentElement.setAttribute('data-theme', savedTheme);
    this.updateThemeButton(savedTheme);
  },

  toggleTheme() {
    const current = document.documentElement.getAttribute('data-theme');
    const next = current === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', next);
    localStorage.setItem('midterm_theme', next);
    this.updateThemeButton(next);
  },

  updateThemeButton(theme) {
    const btn = document.getElementById('theme-toggle-btn');
    if (!btn) return;
    btn.innerHTML = theme === 'dark' 
      ? '☀️ Világos mód' 
      : '🌙 Sötét mód';
  },

  // Countdown to Election Day: Nov 3, 2026
  initCountdown() {
    const targetDate = new Date('2026-11-03T07:00:00-05:00').getTime();

    const updateTimer = () => {
      const now = new Date().getTime();
      const diff = targetDate - now;

      const countdownEl = document.getElementById('election-countdown');
      if (!countdownEl) return;

      if (diff <= 0) {
        countdownEl.textContent = 'Választás Napja!';
        return;
      }

      const days = Math.floor(diff / (1000 * 60 * 60 * 24));
      const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
      const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));

      countdownEl.textContent = `${days} nap, ${hours} óra, ${minutes} perc`;
    };

    updateTimer();
    setInterval(updateTimer, 60000);
  },

  // Event Listeners
  initEventListeners() {
    // Theme toggle
    document.getElementById('theme-toggle-btn')?.addEventListener('click', () => this.toggleTheme());

    // Manual Refresh button
    document.getElementById('refresh-btn')?.addEventListener('click', () => this.triggerRefresh());

    // Tab Navigation
    document.querySelectorAll('.tab-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const tab = e.currentTarget.getAttribute('data-tab');
        this.switchTab(tab);
      });
    });

    // Poll Filter Pills
    document.querySelectorAll('.filter-pill').forEach(pill => {
      pill.addEventListener('click', (e) => {
        document.querySelectorAll('.filter-pill').forEach(p => p.classList.remove('active'));
        e.currentTarget.classList.add('active');
        this.activePollFilter = e.currentTarget.getAttribute('data-filter');
        this.renderPollsTable();
      });
    });

    // Poll Search Input
    document.getElementById('poll-search')?.addEventListener('input', (e) => {
      this.pollSearchQuery = e.target.value.toLowerCase().trim();
      this.renderPollsTable();
    });

    // Senate Explorer Filter Pills
    document.querySelectorAll('[data-senate-filter]').forEach(pill => {
      pill.addEventListener('click', (e) => {
        document.querySelectorAll('[data-senate-filter]').forEach(p => p.classList.remove('active'));
        e.currentTarget.classList.add('active');
        this.activeSenateFilter = e.currentTarget.getAttribute('data-senate-filter');
        this.renderSenateSeatsTable();
      });
    });

    // Senate Explorer Search Input
    document.getElementById('senate-seats-search')?.addEventListener('input', (e) => {
      this.senateSearchQuery = e.target.value.toLowerCase().trim();
      this.renderSenateSeatsTable();
    });

    // News Subtabs (Daily / Weekly / All)
    document.querySelectorAll('[data-news-subtab]').forEach(btn => {
      btn.addEventListener('click', (e) => {
        document.querySelectorAll('[data-news-subtab]').forEach(b => b.classList.remove('active'));
        e.currentTarget.classList.add('active');
        const subtab = e.currentTarget.getAttribute('data-news-subtab');
        this.switchNewsSubtab(subtab);
      });
    });
  },

  // Switch News Subtab
  switchNewsSubtab(subtab) {
    this.activeNewsSubtab = subtab;
    const dailyView = document.getElementById('news-subview-daily');
    const weeklyView = document.getElementById('news-subview-weekly');
    const allView = document.getElementById('news-subview-all');

    if (dailyView) dailyView.style.display = subtab === 'daily' ? 'block' : 'none';
    if (weeklyView) weeklyView.style.display = subtab === 'weekly' ? 'block' : 'none';
    if (allView) allView.style.display = subtab === 'all' ? 'block' : 'none';
  },

  // Switch Active Tab
  switchTab(tabId) {
    this.activeTab = tabId;
    document.querySelectorAll('.tab-btn').forEach(b => {
      b.classList.toggle('active', b.getAttribute('data-tab') === tabId);
    });

    document.querySelectorAll('.tab-pane').forEach(pane => {
      pane.style.display = pane.id === `tab-${tabId}` ? 'block' : 'none';
    });

    // Re-render charts when switching to tabs to ensure dimensions are accurate
    if (tabId === 'overview' || tabId === 'senate' || tabId === 'house') {
      this.renderCharts();
    }
    if (tabId === 'trump') {
      this.loadTruthStats();
      if (!this.truthState.posts || this.truthState.posts.length === 0) {
        this.loadTruthPosts();
      }
    }
  },

  // Load Data Files
  async loadAllData() {
    try {
      const [projRes, pollsRes, newsRes, seatsRes, trumpRes] = await Promise.all([
        fetch('data/projections.json?t=' + Date.now()),
        fetch('data/polls.json?t=' + Date.now()),
        fetch('data/news.json?t=' + Date.now()),
        fetch('data/senate_seats.json?t=' + Date.now()),
        fetch('data/trump_tracker.json?t=' + Date.now())
      ]);

      if (projRes.ok) this.data.projections = await projRes.json();
      if (pollsRes.ok) this.data.polls = await pollsRes.json();
      if (newsRes.ok) this.data.news = await newsRes.json();
      if (seatsRes && seatsRes.ok) this.data.senate_seats = await seatsRes.json();
      if (trumpRes && trumpRes.ok) this.data.trump_tracker = await trumpRes.json();
    } catch (err) {
      console.warn('Direct fetch failed, falling back to embedded dataset', err);
    }

    // Fallback if fetch was blocked (e.g. file:// protocol)
    if (!this.data.projections && typeof FALLBACK_DATA !== 'undefined') {
      this.data.projections = FALLBACK_DATA.projections;
      this.data.polls = FALLBACK_DATA.polls;
      this.data.news = FALLBACK_DATA.news;
      this.data.senate_seats = FALLBACK_DATA.senate_seats;
      this.data.trump_tracker = FALLBACK_DATA.trump_tracker;
    }

    if (!this.data.senate_seats && typeof SENATE_SEATS_DATA !== 'undefined') {
      this.data.senate_seats = SENATE_SEATS_DATA;
    }

    if (!this.data.trump_tracker && typeof TRUMP_TRACKER_DATA !== 'undefined') {
      this.data.trump_tracker = TRUMP_TRACKER_DATA;
    }
  },

  // Trigger manual refresh via server API
  async triggerRefresh() {
    const btn = document.getElementById('refresh-btn');
    if (btn) {
      btn.disabled = true;
      btn.innerHTML = '⏳ Frissítés folyamatban...';
    }

    try {
      const res = await fetch('/api/update', { method: 'POST' });
      if (res.ok) {
        this.showToast('✅ Sikeres frissítés! A legfrissebb adatok betöltve.');
      } else {
        this.showToast('ℹ️ Adatok újraolvasva.');
      }
    } catch (e) {
      this.showToast('ℹ️ Frissítve a legújabb helyi adatokkal.');
    }

    await this.loadAllData();
    this.render();

    if (btn) {
      btn.disabled = false;
      btn.innerHTML = '🔄 Frissítés most';
    }
  },

  showToast(message) {
    let toast = document.getElementById('toast-msg');
    if (!toast) {
      toast = document.createElement('div');
      toast.id = 'toast-msg';
      toast.className = 'toast';
      document.body.appendChild(toast);
    }
    toast.textContent = message;
    toast.classList.add('show');
    setTimeout(() => {
      toast.classList.remove('show');
    }, 3500);
  },

  // Master Render
  render() {
    if (!this.data.projections) return;

    this.renderHeaderInfo();
    this.renderGenericBallot();
    this.renderProjectionsSummary();
    this.renderCharts();
    this.renderBattlegrounds();
    this.renderPollsTable();
    this.renderSenateSeatsTable();
    this.renderDailyNewsDigest();
    this.renderWeeklyNewsDigest();
    this.renderNewsFeed();
    this.renderTrumpTracker();
  },

  renderHeaderInfo() {
    const lastUpdated = new Date(this.data.projections.last_updated);
    const dateFormatted = lastUpdated.toLocaleString('hu-HU', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });

    const updateEl = document.getElementById('last-updated-text');
    if (updateEl) {
      updateEl.textContent = `Utolsó frissítés: ${dateFormatted} | Automata napi frissítés aktív`;
    }
  },

  // Render Generic Ballot
  renderGenericBallot() {
    const gb = this.data.projections.generic_ballot;
    if (!gb) return;

    const demEl = document.getElementById('gb-dem-val');
    const repEl = document.getElementById('gb-rep-val');
    const spreadEl = document.getElementById('gb-spread-badge');
    const trendEl = document.getElementById('gb-trend-text');
    const barDem = document.getElementById('gb-bar-dem');
    const barRep = document.getElementById('gb-bar-rep');

    if (demEl) demEl.textContent = `${gb.democrat}%`;
    if (repEl) repEl.textContent = `${gb.republican}%`;
    if (spreadEl) spreadEl.textContent = gb.spread;
    if (trendEl) trendEl.textContent = `${gb.trend} — Forrás: ${gb.sources}`;

    if (barDem) barDem.style.width = `${gb.democrat}%`;
    if (barRep) barRep.style.width = `${gb.republican}%`;
  },

  // Projections Header Numbers
  renderProjectionsSummary() {
    const sen = this.data.projections.senate;
    const house = this.data.projections.house;

    // Senate summary
    const senDemEl = document.getElementById('sen-dem-proj');
    const senRepEl = document.getElementById('sen-rep-proj');
    const senDemRange = document.getElementById('sen-dem-range');
    const senRepRange = document.getElementById('sen-rep-range');
    const senProbDem = document.getElementById('sen-prob-dem');
    const senProbRep = document.getElementById('sen-prob-rep');
    const senProbDemBar = document.getElementById('sen-prob-dem-bar');
    const senProbRepBar = document.getElementById('sen-prob-rep-bar');

    if (senDemEl) senDemEl.textContent = sen.projection.median_outcome.democrat;
    if (senRepEl) senRepEl.textContent = sen.projection.median_outcome.republican;
    if (senDemRange) senDemRange.textContent = `Várható sáv: ${sen.projection.democrat_projected_range[0]} - ${sen.projection.democrat_projected_range[1]}`;
    if (senRepRange) senRepRange.textContent = `Várható sáv: ${sen.projection.republican_projected_range[0]} - ${sen.projection.republican_projected_range[1]}`;
    if (senProbDem) senProbDem.textContent = `${sen.projection.control_probability.democrat}%`;
    if (senProbRep) senProbRep.textContent = `${sen.projection.control_probability.republican}%`;
    if (senProbDemBar) senProbDemBar.style.width = `${sen.projection.control_probability.democrat}%`;
    if (senProbRepBar) senProbRepBar.style.width = `${sen.projection.control_probability.republican}%`;

    // House summary
    const houseDemEl = document.getElementById('house-dem-proj');
    const houseRepEl = document.getElementById('house-rep-proj');
    const houseDemRange = document.getElementById('house-dem-range');
    const houseRepRange = document.getElementById('house-rep-range');
    const houseProbDem = document.getElementById('house-prob-dem');
    const houseProbRep = document.getElementById('house-prob-rep');
    const houseProbDemBar = document.getElementById('house-prob-dem-bar');
    const houseProbRepBar = document.getElementById('house-prob-rep-bar');

    if (houseDemEl) houseDemEl.textContent = house.projection.median_outcome.democrat;
    if (houseRepEl) houseRepEl.textContent = house.projection.median_outcome.republican;
    if (houseDemRange) houseDemRange.textContent = `Várható sáv: ${house.projection.democrat_projected_range[0]} - ${house.projection.democrat_projected_range[1]}`;
    if (houseRepRange) houseRepRange.textContent = `Várható sáv: ${house.projection.republican_projected_range[0]} - ${house.projection.republican_projected_range[1]}`;
    if (houseProbDem) houseProbDem.textContent = `${house.projection.control_probability.democrat}%`;
    if (houseProbRep) houseProbRep.textContent = `${house.projection.control_probability.republican}%`;
    if (houseProbDemBar) houseProbDemBar.style.width = `${house.projection.control_probability.democrat}%`;
    if (houseProbRepBar) houseProbRepBar.style.width = `${house.projection.control_probability.republican}%`;
  },

  // Visual Charts
  renderCharts() {
    const sen = this.data.projections.senate;
    const house = this.data.projections.house;

    // 1. Senate Hemicycle with 100 seats
    Charts.renderSenateHemicycle('senate-hemicycle-chart', sen, this.data.senate_seats);

    // 2. Senate Balance Bar
    Charts.renderBalanceBar('senate-balance-bar', sen.projection.categories, 100, 51);

    // 3. House Balance Bar
    Charts.renderBalanceBar('house-balance-bar', house.projection.categories, 435, 218);
  },

  // Battleground cards
  renderBattlegrounds() {
    const container = document.getElementById('battleground-container');
    if (!container) return;

    const bgs = this.data.projections.senate.battlegrounds;
    container.innerHTML = bgs.map(bg => {
      let ratingClass = 'tossup';
      if (bg.rating.includes('Dem')) ratingClass = 'dem';
      else if (bg.rating.includes('Rep')) ratingClass = 'rep';

      return `
        <div class="bg-card">
          <div class="bg-header">
            <div class="bg-state">
              <span class="state-flag">${bg.state_code}</span>
              <span>${bg.state}</span>
            </div>
            <span class="bg-rating-badge ${ratingClass}">${bg.rating}</span>
          </div>

          <div class="bg-candidates">
            <div class="candidate-row">
              <span class="candidate-name" style="color: var(--dem-blue-light);">${bg.challenger || bg.candidates?.split('vs')[0]}</span>
              <span class="candidate-poll">${bg.poll_avg_dem}%</span>
            </div>
            <div class="candidate-row">
              <span class="candidate-name" style="color: var(--rep-red-light);">${bg.incumbent || bg.candidates?.split('vs')[1]}</span>
              <span class="candidate-poll">${bg.poll_avg_rep}%</span>
            </div>
          </div>

          <div class="bg-lead">Előny: <strong>${bg.lead}</strong></div>
          <p class="bg-desc"><strong>Kiemelt témák:</strong> ${bg.key_issues}</p>
          <p class="bg-desc" style="margin-top: 0.35rem; font-style: italic;">${bg.importance}</p>
        </div>
      `;
    }).join('');
  },

  // Filterable Polling Table
  renderPollsTable() {
    const tbody = document.getElementById('polls-tbody');
    if (!tbody || !this.data.polls) return;

    let filtered = this.data.polls.polls.filter(poll => {
      // Scope filter
      if (this.activePollFilter === 'national' && poll.scope !== 'National') return false;
      if (this.activePollFilter === 'senate' && !poll.race.toLowerCase().includes('senate')) return false;
      if (this.activePollFilter === 'house' && (!poll.race.toLowerCase().includes('generic') && !poll.race.toLowerCase().includes('house'))) return false;

      // Text query
      if (this.pollSearchQuery) {
        const text = `${poll.race} ${poll.pollster} ${poll.scope} ${poll.lead}`.toLowerCase();
        if (!text.includes(this.pollSearchQuery)) return false;
      }
      return true;
    });

    if (filtered.length === 0) {
      tbody.innerHTML = `<tr><td colspan="7" style="text-align: center; padding: 2rem; color: var(--text-muted);">Nincs a szűrésnek megfelelő felmérés.</td></tr>`;
      return;
    }

    tbody.innerHTML = filtered.map(poll => {
      let gradeClass = 'grade-B-plus';
      if (poll.grade === 'A+') gradeClass = 'grade-A-plus';
      else if (poll.grade === 'A') gradeClass = 'grade-A';
      else if (poll.grade === 'A-') gradeClass = 'grade-A-minus';

      let leadClass = 'lead-even';
      if (poll.lead.includes('Dem') || poll.lead.includes('Talarico') || poll.lead.includes('El-Sayed') || poll.lead.includes('Brown') || poll.lead.includes('Turek')) {
        leadClass = 'lead-dem';
      } else if (poll.lead.includes('Rep') || poll.lead.includes('Tillis') || poll.lead.includes('Sullivan')) {
        leadClass = 'lead-rep';
      }

      return `
        <tr>
          <td><span style="font-weight: 600;">${poll.date}</span></td>
          <td>
            <div style="font-weight: 700; color: var(--text-main);">${poll.race}</div>
            <div style="font-size: 0.75rem; color: var(--text-muted);">${poll.sample} | Hibahatár: ${poll.margin_of_error}</div>
          </td>
          <td>
            <div class="pollster-badge">
              <span>${poll.pollster}</span>
              <span class="grade-tag ${gradeClass}">${poll.grade}</span>
            </div>
          </td>
          <td style="font-weight: 700; color: var(--dem-blue-light);">${poll.dem_pct}%</td>
          <td style="font-weight: 700; color: var(--rep-red-light);">${poll.rep_pct}%</td>
          <td><span class="lead-pill ${leadClass}">${poll.lead}</span></td>
          <td>
            <a href="${poll.url}" target="_blank" rel="noopener noreferrer" class="read-link">
              Forrás ↗
            </a>
          </td>
        </tr>
      `;
    }).join('');
  },

  // 100-Seat Senate Table / Directory
  renderSenateSeatsTable() {
    const tbody = document.getElementById('senate-seats-tbody');
    if (!tbody || !this.data.senate_seats) return;

    let filtered = this.data.senate_seats.filter(seat => {
      if (this.activeSenateFilter === 'election' && !seat.is_election_2026) return false;
      if (this.activeSenateFilter === 'no-election' && seat.is_election_2026) return false;

      if (this.senateSearchQuery) {
        const text = `${seat.state} ${seat.state_code} ${seat.current_senator || ''} ${seat.old_senator || ''} ${seat.candidates || ''} ${seat.favored || ''} ${seat.class}`.toLowerCase();
        if (!text.includes(this.senateSearchQuery)) return false;
      }
      return true;
    });

    if (filtered.length === 0) {
      tbody.innerHTML = `<tr><td colspan="7" style="text-align: center; padding: 2rem; color: var(--text-muted);">Nincs a keresésnek megfelelő szenátusi szék.</td></tr>`;
      return;
    }

    tbody.innerHTML = filtered.map(seat => {
      if (seat.is_election_2026) {
        let forecastClass = 'lead-even';
        if (seat.forecast && seat.forecast.includes('Dem')) forecastClass = 'lead-dem';
        else if (seat.forecast && seat.forecast.includes('Rep')) forecastClass = 'lead-rep';

        return `
          <tr style="cursor: pointer;" onclick="Charts.updateSeatInspector(App.data.senate_seats.find(s=>s.id==='${seat.id}'), true); App.switchTab('overview');" title="Kattints az infografika megjelenítéséhez!">
            <td>
              <div style="font-weight: 700; display: flex; align-items: center; gap: 0.4rem;">
                <span class="state-pill">${seat.state_code}</span>
                <span>${seat.state}</span>
              </div>
            </td>
            <td><span style="font-size: 0.8rem; font-weight: 600; color: var(--text-muted);">${seat.class}</span></td>
            <td><span class="inspector-badge election" style="display: inline-block;">🔥 Választás (2026)</span></td>
            <td>
              <div style="font-weight: 700; color: #f87171;">${seat.old_senator}</div>
              <div style="font-size: 0.72rem; color: var(--text-muted);">Régi / Hivatalban lévő</div>
            </td>
            <td>
              <div style="font-weight: 600; color: var(--text-main); font-size: 0.85rem;">${seat.candidates}</div>
            </td>
            <td>
              <div style="font-weight: 800; color: #34d399;">🏆 ${seat.favored}</div>
            </td>
            <td>
              <span class="lead-pill ${forecastClass}">${seat.forecast}</span>
            </td>
          </tr>
        `;
      } else {
        const partyClass = seat.party_code === 'dem' ? 'lead-dem' : 'lead-rep';
        return `
          <tr style="cursor: pointer;" onclick="Charts.updateSeatInspector(App.data.senate_seats.find(s=>s.id==='${seat.id}'), true); App.switchTab('overview');" title="Kattints az infografika megjelenítéséhez!">
            <td>
              <div style="font-weight: 700; display: flex; align-items: center; gap: 0.4rem;">
                <span class="state-pill">${seat.state_code}</span>
                <span>${seat.state}</span>
              </div>
            </td>
            <td><span style="font-size: 0.8rem; font-weight: 600; color: var(--text-muted);">${seat.class}</span></td>
            <td><span class="inspector-badge no-election" style="display: inline-block;">🔒 Nincs választás</span></td>
            <td>
              <div style="font-weight: 700; color: ${seat.party_code === 'dem' ? '#60a5fa' : '#f87171'};">${seat.current_senator}</div>
              <div style="font-size: 0.72rem; color: var(--text-muted);">${seat.party}</div>
            </td>
            <td>
              <span style="color: var(--text-muted); font-size: 0.8rem;">— (Mandátum nem jár le)</span>
            </td>
            <td>
              <span style="color: var(--text-muted); font-size: 0.8rem;">Nem releváns</span>
            </td>
            <td>
              <span class="lead-pill ${partyClass}" style="opacity: 0.85;">${seat.next_election}-ig érvényes</span>
            </td>
          </tr>
        `;
      }
    }).join('');
  },

  // News Feed Grid
  renderNewsFeed() {
    const container = document.getElementById('news-grid-container');
    if (!container || !this.data.news) return;

    container.innerHTML = this.data.news.articles.map(art => {
      const pubDate = new Date(art.published_at);
      const timeStr = pubDate.toLocaleDateString('hu-HU', {
        month: 'short',
        day: 'numeric'
      });

      return `
        <article class="news-card">
          <div>
            <div class="news-meta">
              <span class="news-source-tag">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
                ${art.source}
              </span>
              <span class="news-time">${timeStr}</span>
            </div>
            <h3 class="news-title">${art.title}</h3>
            <p class="news-summary">${art.summary}</p>
          </div>
          <div class="news-footer">
            <span class="news-category-badge">${art.category}</span>
            <a href="${art.url}" target="_blank" rel="noopener noreferrer" class="read-link">
              Eredeti cikk ↗
            </a>
          </div>
        </article>
      `;
    }).join('');
  },

  // Daily News Digest & Keyword Trends
  renderDailyNewsDigest() {
    const kwContainer = document.getElementById('trending-keywords-pills');
    const digestContainer = document.getElementById('daily-digest-container');
    if (!this.data.news) return;

    // 1. Trending Keywords Cloud
    if (kwContainer && this.data.news.trending_keywords) {
      kwContainer.innerHTML = this.data.news.trending_keywords.map(kw => `
        <span class="keyword-pill" title="${kw.mentions} médiamegjelenés ma">
          <span>#${kw.keyword}</span>
          <span class="keyword-count">${kw.mentions}</span>
          <span style="font-size: 0.68rem; color: #4ade80; font-weight: 700;">${kw.trend}</span>
        </span>
      `).join('');
    }

    // 2. Daily Lead Stories
    if (digestContainer && this.data.news.daily_digest) {
      const dd = this.data.news.daily_digest;
      digestContainer.innerHTML = `
        <div class="daily-digest-box">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem; flex-wrap: wrap; gap: 0.5rem;">
            <div style="font-size: 0.82rem; font-weight: 800; color: #f59e0b; text-transform: uppercase; letter-spacing: 0.05em;">
              🔥 A Nap Kiemelt Témája • ${dd.date}
            </div>
            <span class="news-source-tag">Összesített Médiafigyelés (AP, Reuters, NYT)</span>
          </div>

          <h3 style="font-size: 1.3rem; font-weight: 800; line-height: 1.4; margin-bottom: 0.75rem;">
            ${dd.headline}
          </h3>
          <p style="font-size: 0.9rem; color: var(--text-muted); line-height: 1.6; margin-bottom: 1.5rem;">
            ${dd.lead_summary}
          </p>

          <div style="display: flex; flex-direction: column; gap: 1rem;">
            ${dd.top_stories.map(story => {
              const impactClass = story.impact_score === 'Kritikus' ? 'impact-kritikus' : 'impact-magas';
              return `
                <div style="background: var(--bg-card); padding: 1.15rem; border-radius: var(--radius-md); border: 1px solid var(--border-color);">
                  <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem; flex-wrap: wrap; gap: 0.5rem;">
                    <span style="font-size: 0.78rem; font-weight: 700; color: var(--accent);">${story.source}</span>
                    <span class="impact-badge ${impactClass}">Hangsúly: ${story.impact_score}</span>
                  </div>
                  <h4 style="font-size: 1.05rem; font-weight: 700; margin-bottom: 0.4rem; color: var(--text-main);">
                    ${story.title}
                  </h4>
                  <p style="font-size: 0.85rem; color: var(--text-muted); line-height: 1.55; margin-bottom: 0.75rem;">
                    ${story.summary}
                  </p>
                  <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 0.5rem;">
                    <div style="display: flex; gap: 0.35rem; flex-wrap: wrap;">
                      ${(story.keywords || []).map(k => `<span class="source-pill" style="font-size: 0.7rem;">#${k}</span>`).join('')}
                    </div>
                    <a href="${story.url}" target="_blank" rel="noopener noreferrer" class="read-link">
                      Forrásanyag ↗
                    </a>
                  </div>
                </div>
              `;
            }).join('')}
          </div>
        </div>
      `;
    }
  },

  // Weekly News Digest
  renderWeeklyNewsDigest() {
    const container = document.getElementById('weekly-digest-container');
    if (!container || !this.data.news || !this.data.news.weekly_digest) return;

    const wd = this.data.news.weekly_digest;
    container.innerHTML = `
      <div class="weekly-analysis-card">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem; flex-wrap: wrap; gap: 0.5rem;">
          <span style="font-size: 0.82rem; font-weight: 800; color: var(--accent); text-transform: uppercase;">
            📅 ${wd.week_number}
          </span>
          <span class="news-source-tag">Heti Elemzői Konszenzus</span>
        </div>

        <h3 style="font-size: 1.35rem; font-weight: 800; margin-bottom: 0.75rem;">
          ${wd.title}
        </h3>
        <p style="font-size: 0.92rem; color: var(--text-muted); line-height: 1.6; margin-bottom: 1.25rem;">
          ${wd.editorial_analysis}
        </p>

        <h4 style="font-size: 0.95rem; font-weight: 800; margin-top: 1.25rem; color: var(--text-main);">
          📌 A Hét 4 Legfontosabb Politikai Tanulsága:
        </h4>
        <div class="takeaway-list">
          ${wd.key_takeaways.map(t => `<div class="takeaway-item">${t}</div>`).join('')}
        </div>

        <h4 style="font-size: 0.95rem; font-weight: 800; margin-top: 1.75rem; margin-bottom: 0.75rem; color: var(--text-main);">
          📚 Kiemelt Heti Mélyelemzések:
        </h4>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 1rem;">
          ${(wd.top_articles_of_the_week || []).map(a => `
            <div style="background: var(--bg-secondary); padding: 1rem; border-radius: var(--radius-md); border: 1px solid var(--border-color);">
              <span style="font-size: 0.75rem; font-weight: 700; color: var(--accent);">${a.source}</span>
              <h5 style="font-size: 0.95rem; font-weight: 700; margin: 0.35rem 0 0.5rem 0;">${a.title}</h5>
              <p style="font-size: 0.82rem; color: var(--text-muted); line-height: 1.5; margin-bottom: 0.75rem;">${a.summary}</p>
              <a href="${a.url}" target="_blank" rel="noopener noreferrer" class="read-link">Cikk elolvasása ↗</a>
            </div>
          `).join('')}
        </div>
      </div>
    `;
  },

  // Trump Tracker & Truth Social Explorer
  truthState: {
    page: 1,
    limit: 20,
    q: '',
    topic: 'all',
    has_media: false,
    sort: 'newest',
    total: 36703,
    filtered_total: 36703,
    total_pages: 1836,
    posts: [],
    cachedArchive: null,
    stats: null,
    activeSubtab: 'posts',
    isLoading: false
  },

  switchTrumpSubtab(subtab) {
    this.truthState.activeSubtab = subtab;
    const tabs = ['posts', 'rallies', 'initiatives'];
    tabs.forEach(t => {
      const btn = document.getElementById(`btn-subtab-truth-${t}`);
      const content = document.getElementById(`trump-subtab-${t}`);
      if (btn) btn.classList.toggle('active', t === subtab);
      if (content) content.style.display = t === subtab ? 'block' : 'none';
    });

    if (subtab === 'posts' && (!this.truthState.posts || this.truthState.posts.length === 0)) {
      this.loadTruthPosts();
    }
  },

  async loadTruthStats() {
    try {
      const res = await fetch('/api/truth-stats');
      if (res.ok) {
        const stats = await res.json();
        this.truthState.stats = stats;
        const totalEl = document.getElementById('truth-stat-total');
        const mediaEl = document.getElementById('truth-stat-media');
        const latestEl = document.getElementById('truth-stat-latest');
        const favEl = document.getElementById('truth-stat-top-favs');
        if (totalEl) totalEl.textContent = Number(stats.total_posts).toLocaleString('hu-HU');
        if (mediaEl) mediaEl.textContent = Number(stats.total_media_posts).toLocaleString('hu-HU');
        if (latestEl && stats.latest_post_date) {
          const d = new Date(stats.latest_post_date);
          latestEl.textContent = d.toLocaleDateString('hu-HU', { month: 'short', day: 'numeric' });
        }
        if (favEl && stats.top_liked_post) {
          const k = Math.round(stats.top_liked_post.likes / 1000);
          favEl.textContent = `${k}K+`;
        }
      }
    } catch (e) {
      console.log('Truth stats local fallback');
    }
  },

  async loadTruthPosts() {
    if (this.truthState.isLoading) return;
    this.truthState.isLoading = true;

    const countEl = document.getElementById('truth-results-count');
    const feedEl = document.getElementById('truth-posts-feed');
    if (countEl) countEl.innerHTML = '⏳ <em>Bejegyzések keresése és rendezése...</em>';
    if (feedEl && (!this.truthState.posts || this.truthState.posts.length === 0)) {
      feedEl.innerHTML = '<div style="padding: 2.5rem; text-align: center; color: var(--text-muted); font-size: 0.9rem;">⏳ Bejegyzések betöltése az adatbázisból...</div>';
    }

    try {
      const params = new URLSearchParams({
        page: this.truthState.page,
        limit: this.truthState.limit,
        q: this.truthState.q,
        topic: this.truthState.topic,
        sort: this.truthState.sort,
        has_media: this.truthState.has_media ? '1' : '0'
      });

      const res = await fetch(`/api/truth-posts?${params.toString()}`);
      if (res.ok) {
        const data = await res.json();
        this.truthState.posts = data.posts || [];
        this.truthState.total = data.total || 36703;
        this.truthState.filtered_total = data.filtered_total;
        this.truthState.total_pages = data.total_pages;
        this.truthState.page = data.page;
        this.renderTruthPosts();
        this.renderTruthPagination();
        this.truthState.isLoading = false;
        return;
      }
    } catch (err) {
      console.warn('Server API /api/truth-posts not available, using client-side fallback', err);
    }

    // Client-side fallback if server API is not available
    await this.loadTruthPostsClientFallback();
    this.renderTruthPosts();
    this.renderTruthPagination();
    this.truthState.isLoading = false;
  },

  async loadTruthPostsClientFallback() {
    if (!this.truthState.cachedArchive) {
      try {
        const res = await fetch('data/truth_archive.json');
        if (res.ok) {
          this.truthState.cachedArchive = await res.json();
        }
      } catch (e) {
        console.warn('Could not load data/truth_archive.json', e);
      }
    }

    let list = this.truthState.cachedArchive || (this.data.trump_tracker?.posts || []);
    const q = this.truthState.q.toLowerCase().trim();
    if (q) {
      list = list.filter(p => (p.content || p.text || '').toLowerCase().includes(q));
    }
    if (this.truthState.has_media) {
      list = list.filter(p => p.media && p.media.length > 0);
    }
    if (this.truthState.topic && this.truthState.topic !== 'all') {
      const topicKeywords = {
        election: ["election", "midterm", "vote", "ballot", "republican", "democrat", "senate", "house", "poll", "rally", "paxton", "victory"],
        economy: ["tariff", "tariffs", "inflation", "economy", "tax", "taxes", "jobs", "trade", "dollar", "china", "manufacturing", "energy", "oil"],
        border: ["border", "wall", "migrant", "migrants", "immigration", "illegal", "ice", "patrol", "invasion", "cartel", "texas"],
        legal: ["court", "judge", "doj", "fbi", "witch hunt", "indictment", "trial", "lawyer", "justice", "prosecutor"],
        china: ["china", "xi", "beijing", "chinese", "taiwan"]
      };
      const kws = topicKeywords[this.truthState.topic] || [this.truthState.topic];
      list = list.filter(p => kws.some(kw => (p.content || p.text || '').toLowerCase().includes(kw)));
    }

    if (this.truthState.sort === 'likes') {
      list.sort((a,b) => (b.favourites_count || 0) - (a.favourites_count || 0));
    } else if (this.truthState.sort === 'retruths') {
      list.sort((a,b) => (b.reblogs_count || 0) - (a.reblogs_count || 0));
    } else if (this.truthState.sort === 'oldest') {
      list.sort((a,b) => (a.created_at || a.date || '').localeCompare(b.created_at || b.date || ''));
    } else {
      list.sort((a,b) => (b.created_at || b.date || '').localeCompare(a.created_at || a.date || ''));
    }

    this.truthState.total = this.truthState.cachedArchive ? this.truthState.cachedArchive.length : list.length;
    this.truthState.filtered_total = list.length;
    this.truthState.total_pages = Math.max(1, Math.ceil(list.length / this.truthState.limit));
    this.truthState.page = Math.min(this.truthState.page, this.truthState.total_pages);
    const start = (this.truthState.page - 1) * this.truthState.limit;
    this.truthState.posts = list.slice(start, start + this.truthState.limit);
  },

  renderTruthPosts() {
    const countEl = document.getElementById('truth-results-count');
    const feedEl = document.getElementById('truth-posts-feed');
    if (!feedEl) return;

    if (countEl) {
      const totalStr = Number(this.truthState.filtered_total).toLocaleString('hu-HU');
      const allTotalStr = Number(this.truthState.total).toLocaleString('hu-HU');
      countEl.innerHTML = `Összesen <strong>${totalStr}</strong> találat (archívumban: ${allTotalStr}) &bull; Oldal: <strong>${this.truthState.page} / ${this.truthState.total_pages}</strong>`;
    }

    if (!this.truthState.posts || this.truthState.posts.length === 0) {
      feedEl.innerHTML = `
        <div style="background: var(--bg-card); border: 1px solid var(--border-color); border-radius: var(--radius-md); padding: 3rem 1.5rem; text-align: center;">
          <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">🔍</div>
          <h4 style="font-size: 1.1rem; font-weight: 700; margin-bottom: 0.5rem;">Nincs a szűrésnek megfelelő bejegyzés</h4>
          <p style="color: var(--text-muted); font-size: 0.85rem; max-width: 400px; margin: 0 auto 1.5rem auto;">
            Próbálj más keresőkifejezést, vagy kattints a Visszaállítás gombra az összes poszt megjelenítéséhez.
          </p>
          <button class="btn btn-secondary" onclick="MidtermApp.resetTruthFilters()">Minden szűrő visszaállítása</button>
        </div>
      `;
      return;
    }

    feedEl.innerHTML = this.truthState.posts.map(post => {
      const dateVal = post.created_at || post.date;
      let dateFormatted = '';
      let relativeTime = '';
      if (dateVal) {
        const d = new Date(dateVal);
        dateFormatted = d.toLocaleString('hu-HU', {
          year: 'numeric',
          month: 'short',
          day: 'numeric',
          hour: '2-digit',
          minute: '2-digit'
        });
        const diffMs = Date.now() - d.getTime();
        const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
        const diffDays = Math.floor(diffHours / 24);
        if (diffHours < 1) relativeTime = 'Nemrég';
        else if (diffHours < 24) relativeTime = `${diffHours} órája`;
        else if (diffDays < 30) relativeTime = `${diffDays} napja`;
      }

      // Format text content
      let textContent = post.content || post.text || '';
      if (!textContent.includes('<p>') && !textContent.includes('<div>')) {
        textContent = textContent.replace(/\n/g, '<br>');
      }

      // Media attachments
      let mediaHtml = '';
      if (post.media && Array.isArray(post.media) && post.media.length > 0) {
        mediaHtml = `
          <div class="truth-media-gallery">
            ${post.media.map(m => `
              <img src="${m}" loading="lazy" alt="Trump Truth Social Media" onclick="MidtermApp.openLightbox('${m}')" onerror="this.style.display='none'">
            `).join('')}
          </div>
        `;
      }

      const replies = Number(post.replies_count || 0).toLocaleString('hu-HU');
      const reblogs = Number(post.reblogs_count || 0).toLocaleString('hu-HU');
      const favs = Number(post.favourites_count || 0).toLocaleString('hu-HU');
      const truthUrl = post.url || `https://truthsocial.com/@realDonaldTrump/${post.id}`;

      return `
        <article class="truth-post-feed-card" id="post-${post.id}">
          <div class="truth-author-row">
            <div class="truth-author-info">
              <div class="truth-author-pfp">45</div>
              <div class="truth-author-names">
                <span class="truth-display-name">
                  Donald J. Trump
                  <span class="truth-verified-icon" title="Ellenőrzött fiók">✓</span>
                </span>
                <span class="truth-username">@realDonaldTrump &bull; Truth Social</span>
              </div>
            </div>
            <div class="truth-post-timestamp">
              ${relativeTime ? `<span style="font-weight: 700; color: #f87171;">${relativeTime}</span> &bull; ` : ''}${dateFormatted}
            </div>
          </div>

          <div class="truth-post-body">
            ${textContent}
          </div>

          ${mediaHtml}

          <div class="truth-metrics-footer">
            <div class="truth-metrics-counters">
              <span class="truth-metric-item" title="Hozzászólások">
                💬 <strong>${replies}</strong>
              </span>
              <span class="truth-metric-item" title="Re-Truth megosztások">
                🔁 <strong>${reblogs}</strong>
              </span>
              <span class="truth-metric-item" title="Kedvelések">
                ❤️ <strong>${favs}</strong>
              </span>
            </div>
            <a href="${truthUrl}" target="_blank" rel="noopener noreferrer" class="truth-external-link">
              Megnyitás a Truth Social-ön ↗
            </a>
          </div>
        </article>
      `;
    }).join('');
  },

  renderTruthPagination() {
    const container = document.getElementById('truth-pagination-bar');
    if (!container) return;

    const totalPages = this.truthState.total_pages;
    const cur = this.truthState.page;
    if (totalPages <= 1) {
      container.innerHTML = '';
      return;
    }

    let html = '';
    html += `<button class="truth-page-btn" ${cur === 1 ? 'disabled' : ''} onclick="MidtermApp.jumpToTruthPage(1)" title="Első oldal">« Első</button>`;
    html += `<button class="truth-page-btn" ${cur === 1 ? 'disabled' : ''} onclick="MidtermApp.jumpToTruthPage(${cur - 1})" title="Előző oldal">‹ Előző</button>`;

    // Page window
    let startPage = Math.max(1, cur - 2);
    let endPage = Math.min(totalPages, cur + 2);
    if (endPage - startPage < 4) {
      if (startPage === 1) endPage = Math.min(totalPages, 5);
      else if (endPage === totalPages) startPage = Math.max(1, totalPages - 4);
    }

    if (startPage > 1) html += `<span style="color: var(--text-muted); align-self: center;">...</span>`;

    for (let p = startPage; p <= endPage; p++) {
      html += `<button class="truth-page-btn ${p === cur ? 'active' : ''}" onclick="MidtermApp.jumpToTruthPage(${p})">${p}</button>`;
    }

    if (endPage < totalPages) html += `<span style="color: var(--text-muted); align-self: center;">...</span>`;

    html += `<button class="truth-page-btn" ${cur === totalPages ? 'disabled' : ''} onclick="MidtermApp.jumpToTruthPage(${cur + 1})" title="Következő oldal">Következő ›</button>`;
    html += `<button class="truth-page-btn" ${cur === totalPages ? 'disabled' : ''} onclick="MidtermApp.jumpToTruthPage(${totalPages})" title="Utolsó oldal">Utolsó (${totalPages}) »</button>`;

    html += `
      <div class="truth-page-jump">
        <span>Ugrás:</span>
        <input type="number" min="1" max="${totalPages}" id="truth-jump-input" placeholder="${cur}" onkeydown="if(event.key==='Enter') MidtermApp.jumpToTruthPage(this.value)">
        <button class="truth-page-btn" style="padding: 0.35rem 0.6rem; font-size: 0.8rem;" onclick="MidtermApp.jumpToTruthPage(document.getElementById('truth-jump-input').value)">OK</button>
      </div>
    `;

    container.innerHTML = html;
  },

  handleTruthSearch() {
    const input = document.getElementById('truth-search-input');
    const val = input ? input.value.trim() : '';
    this.truthState.q = val;
    this.truthState.page = 1;
    const clearBtn = document.getElementById('truth-clear-btn');
    if (clearBtn) clearBtn.style.display = val ? 'inline-block' : 'none';
    this.loadTruthPosts();
  },

  clearTruthSearch() {
    const input = document.getElementById('truth-search-input');
    if (input) input.value = '';
    this.truthState.q = '';
    this.truthState.page = 1;
    const clearBtn = document.getElementById('truth-clear-btn');
    if (clearBtn) clearBtn.style.display = 'none';
    this.loadTruthPosts();
  },

  resetTruthFilters() {
    this.truthState.q = '';
    this.truthState.topic = 'all';
    this.truthState.has_media = false;
    this.truthState.sort = 'newest';
    this.truthState.page = 1;

    const input = document.getElementById('truth-search-input');
    if (input) input.value = '';
    const clearBtn = document.getElementById('truth-clear-btn');
    if (clearBtn) clearBtn.style.display = 'none';

    document.querySelectorAll('.topic-chip').forEach(c => {
      c.classList.toggle('active', c.getAttribute('data-topic') === 'all');
    });
    const mediaChip = document.getElementById('chip-media-only');
    if (mediaChip) mediaChip.classList.remove('active');

    const sortSelect = document.getElementById('truth-sort-select');
    if (sortSelect) sortSelect.value = 'newest';

    this.loadTruthPosts();
  },

  setTruthTopic(topic) {
    this.truthState.topic = topic;
    this.truthState.page = 1;
    document.querySelectorAll('.topic-chip').forEach(c => {
      c.classList.toggle('active', c.getAttribute('data-topic') === topic);
    });
    this.loadTruthPosts();
  },

  toggleTruthMediaOnly() {
    this.truthState.has_media = !this.truthState.has_media;
    this.truthState.page = 1;
    const chip = document.getElementById('chip-media-only');
    if (chip) chip.classList.toggle('active', this.truthState.has_media);
    this.loadTruthPosts();
  },

  handleTruthSort(val) {
    this.truthState.sort = val;
    this.truthState.page = 1;
    this.loadTruthPosts();
  },

  handleTruthLimit(val) {
    this.truthState.limit = parseInt(val, 10) || 20;
    this.truthState.page = 1;
    this.loadTruthPosts();
  },

  jumpToTruthPage(pageStr) {
    const p = parseInt(pageStr, 10);
    if (!isNaN(p) && p >= 1 && p <= this.truthState.total_pages) {
      this.truthState.page = p;
      this.loadTruthPosts();
      document.querySelector('.truth-explorer-controls')?.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  },

  openLightbox(imgUrl) {
    let lb = document.getElementById('image-lightbox-modal');
    if (!lb) {
      lb = document.createElement('div');
      lb.id = 'image-lightbox-modal';
      lb.style.cssText = 'position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.92);z-index:9999;display:flex;align-items:center;justify-content:center;padding:1rem;cursor:zoom-out;';
      lb.innerHTML = '<img id="lightbox-img" style="max-width:95%;max-height:95%;object-fit:contain;border-radius:8px;box-shadow:0 10px 40px rgba(0,0,0,0.8);">';
      lb.onclick = () => { lb.style.display = 'none'; };
      document.body.appendChild(lb);
    }
    const img = document.getElementById('lightbox-img');
    if (img) img.src = imgUrl;
    lb.style.display = 'flex';
  },

  // Trump Tracker Component
  renderTrumpTracker() {
    if (!this.data.trump_tracker) return;
    const tt = this.data.trump_tracker;

    // Approval Rating
    const appEl = document.getElementById('trump-approve-val');
    const disEl = document.getElementById('trump-disapprove-val');
    const sprEl = document.getElementById('trump-spread-badge');
    const appBar = document.getElementById('trump-prob-approve-bar');
    const disBar = document.getElementById('trump-prob-disapprove-bar');

    if (appEl) appEl.textContent = `${tt.approval_rating.approve}%`;
    if (disEl) disEl.textContent = `${tt.approval_rating.disapprove}%`;
    if (sprEl) sprEl.textContent = `${tt.approval_rating.spread}% Netto`;
    if (appBar) appBar.style.width = `${tt.approval_rating.approve}%`;
    if (disBar) disBar.style.width = `${tt.approval_rating.disapprove}%`;

    // Load initial truth stats & posts
    this.loadTruthStats();
    if (!this.truthState.posts || this.truthState.posts.length === 0) {
      this.loadTruthPosts();
    }

    // Rallies and Activities
    const actContainer = document.getElementById('trump-activities-container');
    if (actContainer && tt.activities) {
      actContainer.innerHTML = tt.activities.map(act => {
        const badgeClass = act.status === 'Közelgő' || act.status === 'Tervezett' ? 'upcoming' : 'past';
        return `
          <div class="rally-item">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.4rem;">
              <span style="font-weight: 700; font-size: 0.85rem; color: var(--accent);">${act.date}</span>
              <span class="rally-status-badge ${badgeClass}">${act.status}</span>
            </div>
            <h4 style="font-size: 1rem; font-weight: 700; margin-bottom: 0.25rem;">
              🏛️ ${act.location}
            </h4>
            <div style="font-size: 0.82rem; color: var(--text-main); margin-bottom: 0.35rem;">
              <strong>Cél:</strong> ${act.focus}
            </div>
            <div style="font-size: 0.78rem; color: var(--text-muted);">
              <strong>Kiemelt témák:</strong> ${act.key_topics}
            </div>
          </div>
        `;
      }).join('');
    }

    // Key Initiatives
    const initContainer = document.getElementById('trump-initiatives-container');
    if (initContainer && tt.key_campaign_focus) {
      initContainer.innerHTML = tt.key_campaign_focus.map(init => `
        <div style="background: var(--bg-card); padding: 1rem; border-radius: var(--radius-md); border: 1px solid var(--border-color); margin-bottom: 0.75rem;">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.3rem;">
            <h5 style="font-size: 0.92rem; font-weight: 700; color: var(--text-main);">${init.title}</h5>
            <span class="source-pill" style="font-size: 0.7rem;">${init.category}</span>
          </div>
          <p style="font-size: 0.82rem; color: var(--text-muted); line-height: 1.5; margin: 0;">${init.desc}</p>
        </div>
      `).join('');
    }
  }
};

window.MidtermApp = App;
window.App = App;

