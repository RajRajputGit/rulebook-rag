document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('question-form');
  const input = document.getElementById('question-input');
  const submitBtn = document.getElementById('submit-btn');
  const btnText = submitBtn.querySelector('.btn-text');
  const btnSpinner = document.getElementById('btn-spinner');
  
  const resultsSection = document.getElementById('results-section');
  const stateBadge = document.getElementById('state-badge');
  const displayQuestion = document.getElementById('display-question');
  const answerText = document.getElementById('answer-text');
  const evidenceCount = document.getElementById('evidence-count');
  const evidenceList = document.getElementById('evidence-list');

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const question = input.value.trim();
    if (!question) return;

    // Loading state UI
    submitBtn.disabled = true;
    btnText.textContent = 'Analyzing...';
    btnSpinner.classList.remove('hidden');

    try {
      const response = await fetch('/api/ask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question })
      });

      if (!response.ok) {
        throw new Error(`Server returned HTTP ${response.status}`);
      }

      const data = await response.json();
      renderResults(data);
    } catch (err) {
      alert(`Error fetching response: ${err.message}`);
    } finally {
      submitBtn.disabled = false;
      btnText.textContent = 'Ask Assistant';
      btnSpinner.classList.add('hidden');
    }
  });

  function renderResults(data) {
    displayQuestion.textContent = data.question;
    stateBadge.textContent = data.state;
    stateBadge.className = `state-badge ${data.state}`;

    answerText.textContent = data.answer;

    // Render evidence
    evidenceList.innerHTML = '';
    const evidence = data.evidence || [];
    evidenceCount.textContent = `${evidence.length} Passage${evidence.length === 1 ? '' : 's'}`;

    if (evidence.length === 0) {
      evidenceList.innerHTML = `
        <div class="evidence-card" style="text-align: center; color: var(--text-secondary);">
          No exact supporting evidence retrieved for this question. (Refusal / Out of Scope)
        </div>
      `;
    } else {
      evidence.forEach((item) => {
        const card = document.createElement('div');
        card.className = 'evidence-card';
        
        const pageBadgeHtml = item.page ? `<span class="badge-page">Page ${item.page}</span>` : '';
        
        card.innerHTML = `
          <div class="evidence-meta">
            <span class="badge-source">${escapeHtml(item.source)}</span>
            ${pageBadgeHtml}
            <span class="evidence-section-name">${escapeHtml(item.section)}</span>
          </div>
          <div class="evidence-snippet">${escapeHtml(item.text)}</div>
        `;
        evidenceList.appendChild(card);
      });
    }

    resultsSection.classList.remove('hidden');
    resultsSection.scrollIntoView({ behavior: 'smooth' });
  }

  function escapeHtml(text) {
    if (!text) return '';
    return text
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }
});

function fillQuestion(text) {
  const input = document.getElementById('question-input');
  input.value = text;
  input.focus();
  document.getElementById('question-form').dispatchEvent(new Event('submit'));
}
