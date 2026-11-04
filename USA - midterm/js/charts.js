/**
 * charts.js - Interactive SVG visualizations for US Midterm Elections
 * - Senate 100-seat hemicycle (Felsőház / Szenátus) with every senator & candidate detailed
 * - House 435-seat balance bar (Alsóház / Képviselőház)
 * - Interactive Seat Inspector
 */

const Charts = {
  // Render the Senate 100-Seat Hemicycle in SVG using real 100-seat dataset
  renderSenateHemicycle(containerId, senateData, seatsList) {
    const container = document.getElementById(containerId);
    if (!container) return;

    // Fallback if seatsList is not supplied
    if (!seatsList || seatsList.length !== 100) {
      if (typeof SENATE_SEATS_DATA !== 'undefined') {
        seatsList = SENATE_SEATS_DATA;
      }
    }

    // Sort the 100 seats for display on the hemicycle:
    // Left: Safe Dem (not up) -> Dem 2026 -> Toss-ups -> Rep 2026 -> Safe Rep (not up)
    const sortedSeats = [...(seatsList || [])].sort((a, b) => {
      const getScore = (s) => {
        if (!s.is_election_2026) {
          return s.party_code === 'dem' ? 10 : 90;
        }
        // Election 2026 seats
        if (s.forecast && s.forecast.includes('Biztos Demokrata')) return 20;
        if (s.forecast && s.forecast.includes('Valószínű Demokrata')) return 30;
        if (s.forecast && s.forecast.includes('Hajló Demokrata')) return 40;
        if (s.forecast && (s.forecast.includes('Csatatér') || s.forecast.includes('Döntetlen'))) return 50;
        if (s.forecast && s.forecast.includes('Hajló Rep')) return 60;
        if (s.forecast && s.forecast.includes('Valószínű Republikánus')) return 70;
        if (s.forecast && s.forecast.includes('Biztos Republikánus')) return 80;
        return s.party_code === 'dem' ? 35 : 65;
      };
      return getScore(a) - getScore(b);
    });

    const getSeatColor = (s) => {
      if (!s.is_election_2026) {
        return s.party_code === 'dem' ? '#1e3a8a' : '#991b1b';
      }
      if (s.forecast.includes('Csatatér') || s.forecast.includes('Döntetlen')) return '#f59e0b';
      if (s.forecast.includes('Biztos Demokrata')) return '#2563eb';
      if (s.forecast.includes('Valószínű Demokrata') || s.forecast.includes('Hajló Demokrata')) return '#60a5fa';
      if (s.forecast.includes('Biztos Republikánus')) return '#dc2626';
      if (s.forecast.includes('Valószínű Republikánus') || s.forecast.includes('Hajló Rep')) return '#f87171';
      return s.party_code === 'dem' ? '#3b82f6' : '#ef4444';
    };

    // Layout seats on 4 concentric semi-circular rings
    // Ring seat distribution: 19, 23, 27, 31 = 100 total seats
    const rings = [
      { count: 19, radius: 95 },
      { count: 23, radius: 125 },
      { count: 27, radius: 155 },
      { count: 31, radius: 185 }
    ];

    const centerX = 220;
    const centerY = 210;
    let seatIndex = 0;
    const dotsSvg = [];

    rings.forEach((ring) => {
      const { count, radius } = ring;
      for (let i = 0; i < count; i++) {
        if (seatIndex >= sortedSeats.length) break;
        const seat = sortedSeats[seatIndex];
        const color = getSeatColor(seat);
        // Angle from 180 deg (left) to 0 deg (right)
        const angleDeg = 180 - (i / (count - 1)) * 180;
        const angleRad = (angleDeg * Math.PI) / 180;
        const x = centerX + radius * Math.cos(angleRad);
        const y = centerY - radius * Math.sin(angleRad);

        // Escape helper for html attributes
        const stateName = seat.state;
        const seatNum = seatIndex + 1;

        dotsSvg.push(`
          <circle 
            cx="${x.toFixed(1)}" 
            cy="${y.toFixed(1)}" 
            r="6.8" 
            fill="${color}" 
            stroke="#0b0f19" 
            stroke-width="1.3"
            class="seat-dot"
            id="dot-${seat.id}"
            data-index="${seatNum}"
            data-seat-id="${seat.id}"
            data-state="${stateName}"
            data-is-election="${seat.is_election_2026}"
            style="cursor: pointer; transition: transform 0.2s, r 0.2s;"
          />
        `);
        seatIndex++;
      }
    });

    const svgHtml = `
      <svg class="hemicycle-svg" viewBox="0 0 440 230" xmlns="http://www.w3.org/2000/svg">
        <!-- Guide arches -->
        <path d="M 35 210 A 185 185 0 0 1 405 210" fill="none" stroke="rgba(255,255,255,0.06)" stroke-dasharray="3,3" stroke-width="1.5" />
        <path d="M 65 210 A 155 155 0 0 1 375 210" fill="none" stroke="rgba(255,255,255,0.06)" stroke-dasharray="3,3" stroke-width="1.5" />
        <path d="M 95 210 A 125 125 0 0 1 345 210" fill="none" stroke="rgba(255,255,255,0.06)" stroke-dasharray="3,3" stroke-width="1.5" />
        <path d="M 125 210 A 95 95 0 0 1 315 210" fill="none" stroke="rgba(255,255,255,0.06)" stroke-dasharray="3,3" stroke-width="1.5" />
        
        <!-- Threshold dividing line (center 51 seats) -->
        <line x1="220" y1="20" x2="220" y2="215" stroke="rgba(255,255,255,0.4)" stroke-width="1.5" stroke-dasharray="4,4" />
        <text x="220" y="15" fill="#f59e0b" font-size="10" font-weight="700" text-anchor="middle">51 TÖBBSÉG</text>

        <!-- Seat Dots -->
        <g id="seats-group">
          ${dotsSvg.join('')}
        </g>
      </svg>
      <div class="hemicycle-tooltip" id="hemicycle-tooltip">
        <div class="focus-seats" id="focus-seats">100</div>
        <div class="focus-title" id="focus-title">Szenátusi Mandátum</div>
      </div>
      <p class="hemicycle-hint">👆 Kattints vagy vigyél rá az egeret bármelyik székre a részletek megtekintéséhez!</p>
    `;

    container.innerHTML = svgHtml;

    // Attach interactive hover and click events to dots
    const dots = container.querySelectorAll('.seat-dot');
    const focusSeats = container.querySelector('#focus-seats');
    const focusTitle = container.querySelector('#focus-title');

    dots.forEach((dot) => {
      const seatId = dot.getAttribute('data-seat-id');
      const seat = sortedSeats.find(s => s.id === seatId);

      dot.addEventListener('mouseenter', function () {
        this.setAttribute('r', '10.5');
        if (seat) {
          focusSeats.textContent = seat.state_code;
          focusSeats.style.color = this.getAttribute('fill');
          if (seat.is_election_2026) {
            focusTitle.textContent = `${seat.state}: Verseny (${seat.favored})`;
          } else {
            focusTitle.textContent = `${seat.state}: ${seat.current_senator} (${seat.party_code.toUpperCase()})`;
          }
          Charts.updateSeatInspector(seat);
        }
      });

      dot.addEventListener('mouseleave', function () {
        this.setAttribute('r', '6.8');
      });

      dot.addEventListener('click', function () {
        if (seat) {
          Charts.updateSeatInspector(seat, true);
        }
      });
    });

    // Default inspector to a prominent battleground (e.g. Texas TX-2 or first toss-up)
    const defaultSeat = sortedSeats.find(s => s.id === 'TX-2') || sortedSeats[0];
    if (defaultSeat) {
      Charts.updateSeatInspector(defaultSeat);
    }
  },

  // Update the dedicated Seat Inspector Panel
  updateSeatInspector(seat, isPinned = false) {
    const inspector = document.getElementById('senate-seat-inspector');
    if (!inspector) return;

    if (seat.is_election_2026) {
      inspector.className = 'seat-inspector election-active';
      inspector.innerHTML = `
        <div class="inspector-header">
          <div class="inspector-state">
            <span class="state-pill">${seat.state_code}</span>
            <span>${seat.state} — <strong>${seat.class}</strong></span>
          </div>
          <span class="inspector-badge election">🔥 2026-os Választási Verseny</span>
        </div>
        <div class="inspector-body">
          <div class="inspector-item">
            <span class="inspector-label">👤 Régi / Hivatalban lévő szenátor:</span>
            <span class="inspector-val incumbent-name">${seat.old_senator}</span>
          </div>
          <div class="inspector-item">
            <span class="inspector-label">⚔️ Induló jelöltek:</span>
            <span class="inspector-val candidates-text">${seat.candidates}</span>
          </div>
          <div class="inspector-item highlight">
            <span class="inspector-label">🏆 Esélyes a győzelemre:</span>
            <span class="inspector-val favored-name">${seat.favored} <span style="font-size: 0.8rem; font-weight: normal; color: var(--text-muted);">(${seat.forecast})</span></span>
          </div>
        </div>
      `;
    } else {
      inspector.className = 'seat-inspector';
      inspector.innerHTML = `
        <div class="inspector-header">
          <div class="inspector-state">
            <span class="state-pill">${seat.state_code}</span>
            <span>${seat.state} — <strong>${seat.class}</strong></span>
          </div>
          <span class="inspector-badge no-election">🔒 Nem lesz választás 2026-ban</span>
        </div>
        <div class="inspector-body">
          <div class="inspector-item">
            <span class="inspector-label">🏛️ Hivatalban lévő szenátor:</span>
            <span class="inspector-val senator-name">${seat.current_senator} (${seat.party})</span>
          </div>
          <div class="inspector-item">
            <span class="inspector-label">📅 Mandátum érvényessége:</span>
            <span class="inspector-val">${seat.next_election}-ig mandátumban marad</span>
          </div>
          <div class="inspector-item">
            <span class="inspector-label">ℹ️ Státusz:</span>
            <span class="inspector-val" style="color: var(--text-muted); font-size: 0.8rem;">Nem érinti a 2026-os félidős választás</span>
          </div>
        </div>
      `;
    }
  },

  // Render Horizontal Segmented Balance Bar
  renderBalanceBar(containerId, categories, totalSeats, majorityNeeded) {
    const container = document.getElementById(containerId);
    if (!container) return;

    const segments = [
      { key: 'solid_dem', name: 'Biztos Dem.', color: 'segment-solid-dem', count: categories.solid_dem },
      { key: 'likely_dem', name: 'Valószínű Dem.', color: 'segment-likely-dem', count: categories.likely_dem },
      { key: 'lean_dem', name: 'Hajló Dem.', color: 'segment-lean-dem', count: categories.lean_dem },
      { key: 'toss_up', name: 'Csatatér', color: 'segment-tossup', count: categories.toss_up },
      { key: 'lean_rep', name: 'Hajló Rep.', color: 'segment-lean-rep', count: categories.lean_rep },
      { key: 'likely_rep', name: 'Valószínű Rep.', color: 'segment-likely-rep', count: categories.likely_rep },
      { key: 'solid_rep', name: 'Biztos Rep.', color: 'segment-solid-rep', count: categories.solid_rep },
    ];

    const majorityPct = (majorityNeeded / totalSeats) * 100;

    let barHtml = `
      <div class="balance-bar-wrapper">
        <div class="threshold-marker" style="left: ${majorityPct.toFixed(1)}%;" data-label="Többség: ${majorityNeeded}"></div>
        <div class="balance-bar">
    `;

    segments.forEach((seg) => {
      const pct = (seg.count / totalSeats) * 100;
      barHtml += `
        <div 
          class="bar-segment ${seg.color}" 
          style="width: ${pct.toFixed(2)}%;" 
          title="${seg.name}: ${seg.count} mandátum (${pct.toFixed(1)}%)"
        ></div>
      `;
    });

    barHtml += `
        </div>
      </div>
      <div class="bar-legend">
        ${segments.map(s => `
          <div class="legend-item">
            <span class="legend-color ${s.color}"></span>
            <span>${s.name}: <strong>${s.count}</strong></span>
          </div>
        `).join('')}
      </div>
    `;

    container.innerHTML = barHtml;
  }
};
