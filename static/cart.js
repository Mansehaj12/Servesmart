// Show toast when item is added
function showToast(message) {
    const toast = document.createElement('div');
    toast.className = 'cart-toast';
    toast.innerText = message;
    document.body.appendChild(toast);
  
    setTimeout(() => {
      toast.classList.add('show');
    }, 100);
  
    setTimeout(() => {
      toast.classList.remove('show');
      setTimeout(() => document.body.removeChild(toast), 500);
    }, 2500);
  }
  
  // Check if URL contains cart success param
  window.addEventListener('DOMContentLoaded', () => {
    const params = new URLSearchParams(window.location.search);
    if (params.get('added') === 'true') {
      showToast('Item added to cart!');
    }
  });
  