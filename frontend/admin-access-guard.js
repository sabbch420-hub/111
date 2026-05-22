(function () {
  const apiBase = window.APP_CONFIG && window.APP_CONFIG.API_BASE ? window.APP_CONFIG.API_BASE : '';
  const pendingClass = 'admin-access-pending';

  function redirect(url) {
    window.location.replace(url);
  }

  function hidePage() {
    document.documentElement.classList.add(pendingClass);
    document.documentElement.style.visibility = 'hidden';
  }

  function showPage() {
    document.documentElement.classList.remove(pendingClass);
    document.documentElement.style.visibility = '';
  }

  async function ensureAdminAccess() {
    const token = String(localStorage.getItem('userToken') || '').trim();
    if (!token) {
      redirect('login.html');
      return;
    }

    hidePage();

    try {
      const response = await fetch(`${apiBase}/user/profile`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (!response.ok) {
        throw new Error(`profile_${response.status}`);
      }

      const profile = await response.json();
      const role = String((profile && profile.role) || localStorage.getItem('userRole') || '').trim().toLowerCase();
      if (role !== 'admin') {
        localStorage.setItem('userRole', role || 'user');
        redirect('user.html');
        return;
      }

      localStorage.setItem('userRole', 'admin');
      if (profile && profile.email) {
        localStorage.setItem('userEmail', String(profile.email));
      }
      if (profile && profile.id) {
        localStorage.setItem('userId', String(profile.id));
      }
      if (profile && profile.display_name) {
        localStorage.setItem('adminDisplayName', String(profile.display_name));
      }
      showPage();
    } catch (_error) {
      localStorage.removeItem('userRole');
      redirect('login.html');
    }
  }

  ensureAdminAccess();

  window.addEventListener('pageshow', function (event) {
    if (event.persisted) {
      ensureAdminAccess();
    }
  });
})();
