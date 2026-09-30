const VISITOR_NAMESPACE = 'modernlife101';
const STATS_ID = 'modernlife-visitor-stats';

function ensureVisitorStats() {
  if (document.getElementById(STATS_ID)) return;

  const stats = document.createElement('div');
  stats.id = STATS_ID;
  stats.className = 'modernlife-visitor-stats';
  stats.innerHTML = `
    <div class="modernlife-stat">
      <span class="modernlife-label">Total</span>
      <strong id="modernlife-total">--</strong>
    </div>
    <div class="modernlife-stat">
      <span class="modernlife-label">Today / 今日</span>
      <strong id="modernlife-today">--</strong>
    </div>
  `;

  const main = document.querySelector('main');
  if (main) {
    main.parentNode.insertBefore(stats, main);
  } else {
    document.body.prepend(stats);
  }
}

async function updateVisitorStats() {
  ensureVisitorStats();

  const totalNode = document.getElementById('modernlife-total');
  const todayNode = document.getElementById('modernlife-today');
  const todayKey = `traffic-${new Date().toISOString().slice(0, 10)}`;

  try {
    const [totalRes, todayRes] = await Promise.all([
      fetch(`https://api.countapi.xyz/hit/${VISITOR_NAMESPACE}/traffic-total`),
      fetch(`https://api.countapi.xyz/hit/${VISITOR_NAMESPACE}/${todayKey}`)
    ]);

    const [totalData, todayData] = await Promise.all([totalRes.json(), todayRes.json()]);

    if (totalNode) totalNode.textContent = Number(totalData.value || 0).toLocaleString();
    if (todayNode) todayNode.textContent = Number(todayData.value || 0).toLocaleString();
  } catch (error) {
    console.warn('Visitor stats unavailable:', error);
    if (totalNode) totalNode.textContent = 'n/a';
    if (todayNode) todayNode.textContent = 'n/a';
  }
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', updateVisitorStats);
} else {
  updateVisitorStats();
}
