

/**
 * Toggle password field visibility.
 * @param {string} fieldId - ID of the password input
 * @param {HTMLElement} btn - The button that was clicked
 */
function togglePassword(fieldId, btn) {
  const field = document.getElementById(fieldId);
  if (!field) return;

  if (field.type === 'password') {
    field.type = 'text';
    btn.innerHTML = '<i class="bi bi-eye-slash"></i>';
  } else {
    field.type = 'password';
    btn.innerHTML = '<i class="bi bi-eye"></i>';
  }
}

document.addEventListener('DOMContentLoaded', function () {
  const alerts = document.querySelectorAll('.alert.alert-dismissible');
  alerts.forEach(function (alert) {
    setTimeout(function () {
      const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
      if (bsAlert) bsAlert.close();
    }, 4000);
  });
});
