// instagram-view — Interactive Instagram gallery viewer

(function () {
  const data = window.GALLERY_DATA;
  if (!data) {
    document.getElementById('app').innerHTML = '<div class="header"><h1>Error: No gallery data found</h1></div>';
    return;
  }

  const app = document.getElementById('app');

  // ── Header ──────────────────────────────────
  const totalImages = data.accounts.reduce((sum, a) => sum + a.posts.length, 0);
  const header = document.createElement('div');
  header.className = 'header';
  header.innerHTML = `
    <h1>${escHtml(data.title)}</h1>
    <div class="meta">Generated ${escHtml(data.generated_at)}</div>
    <div class="stats">${data.accounts.length} accounts · ${totalImages} images</div>
  `;
  app.appendChild(header);

  // ── Lightbox ────────────────────────────────
  const lightbox = document.createElement('div');
  lightbox.className = 'lightbox';
  lightbox.innerHTML = '<img src="" alt="">';
  lightbox.addEventListener('click', () => lightbox.classList.remove('active'));
  document.body.appendChild(lightbox);
  const lightboxImg = lightbox.querySelector('img');

  function openLightbox(src) {
    lightboxImg.src = src;
    lightbox.classList.add('active');
  }

  // ── Accounts ────────────────────────────────
  data.accounts.forEach(acc => {
    const section = document.createElement('div');
    section.className = 'account';

    // Account header
    const avatarSrc = acc.profile.profile_pic_local || `https://www.instagram.com/${acc.profile.username}/`; // fallback
    const verified = acc.profile.is_verified ? '<span class="verified">✓</span>' : '';
    const followers = fmtNum(acc.profile.followers);
    const bio = acc.profile.biography ? `<div class="account-bio">${escHtml(acc.profile.biography)}</div>` : '';

    section.innerHTML = `
      <div class="account-header">
        <img class="account-avatar" src="${avatarSrc}" alt="${escHtml(acc.profile.username)}"
             onerror="this.src='data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><rect fill=%22%231a1d27%22 width=%22100%22 height=%22100%22/><text x=%2250%22 y=%2255%22 text-anchor=%22middle%22 fill=%22%236b7084%22 font-size=%2240%22>📷</text></svg>'">
        <div class="account-info">
          <div class="account-name">${escHtml(acc.profile.full_name || acc.profile.username)} ${verified}</div>
          <div class="account-username">@${escHtml(acc.profile.username)}</div>
          ${bio}
          <div class="account-stats">${followers} followers</div>
        </div>
      </div>
    `;

    // Post grid
    if (acc.posts.length === 0) {
      const empty = document.createElement('div');
      empty.className = 'error-section';
      empty.textContent = 'No posts found for this account.';
      section.appendChild(empty);
    } else {
      const grid = document.createElement('div');
      grid.className = 'post-grid';

      acc.posts.forEach(post => {
        const card = document.createElement('div');
        card.className = 'post-card';

        const imgSrc = post.local_path || post.remote_url || '';
        const caption = post.caption ? `<div class="post-caption">${escHtml(truncate(post.caption, 120))}</div>` : '';
        const videoBadge = post.is_video ? '<span class="video-badge">Video</span>' : '';

        card.innerHTML = `
          <img src="${imgSrc}" alt="Post by ${escHtml(acc.profile.username)}"
               loading="lazy"
               onerror="this.parentElement.innerHTML='<div style=\\'padding:40px;text-align:center;color:var(--muted);font-size:0.8rem\\'>Failed to load</div>'">
          <div class="post-info">
            <div class="row">
              <span class="likes">♥ ${post.likes}</span>
              <span>💬 ${post.comments}</span>
              ${videoBadge}
              <span>${post.taken_at ? formatDate(post.taken_at) : ''}</span>
            </div>
          </div>
          ${caption}
        `;

        // Click to open lightbox
        card.querySelector('img')?.addEventListener('click', (e) => {
          e.stopPropagation();
          openLightbox(imgSrc);
        });

        grid.appendChild(card);
      });

      section.appendChild(grid);
    }

    app.appendChild(section);
  });

  // ── Footer ──────────────────────────────────
  const footer = document.createElement('div');
  footer.className = 'footer';
  footer.innerHTML = `<span>🔮 Aynite Instagram View</span><span>${data.accounts.length} accounts · ${totalImages} images</span>`;
  app.appendChild(footer);

  // ── Helpers ────────────────────────────────
  function escHtml(s) {
    if (s == null) return '';
    return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }

  function truncate(s, max) {
    if (!s || s.length <= max) return s || '';
    return s.substring(0, max) + '...';
  }

  function fmtNum(v) {
    if (v == null) return '—';
    if (v >= 1e6) return (v / 1e6).toFixed(1) + 'M';
    if (v >= 1e3) return (v / 1e3).toFixed(1) + 'K';
    return String(v);
  }

  function formatDate(ts) {
    const d = new Date(ts * 1000);
    return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  }
})();
