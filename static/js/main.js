document.addEventListener('DOMContentLoaded', function () {
    const messages = document.querySelectorAll('.message');
    messages.forEach(function (msg) {
        const btn = document.createElement('span');
        btn.innerHTML = ' &times;';
        btn.style.cssText = 'cursor:pointer; float:right; font-size:16px; margin-left:12px;';
        btn.onclick = function () { msg.remove(); };
        msg.appendChild(btn);

        // Some automaticamente após 4 segundos
        setTimeout(function () {
            msg.style.transition = 'opacity 0.5s';
            msg.style.opacity = '0';
            setTimeout(function () { msg.remove(); }, 500);
        }, 4000);
    });
});