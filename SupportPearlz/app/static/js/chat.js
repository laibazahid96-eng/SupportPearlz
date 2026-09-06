document.addEventListener('DOMContentLoaded', function () {
    var form = document.getElementById('chat-form');
    var button = document.getElementById('submit-btn');
    if (!form || !button) return;

    form.addEventListener('submit', function () {
        var question = document.getElementById('question');
        if (question && !question.value.trim()) return;
        button.disabled = true;
        button.textContent = 'Thinking...';
    });
});
