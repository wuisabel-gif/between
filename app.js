(() => {
  'use strict';

  const samples = {
    sarcasm: {
      contact: 'Maya',
      channel: 'weekend plans',
      target: 's2',
      messages: [
        { id: 's1', author: 'Maya', time: '10:41', text: 'I thought you were going to tell me if the time changed.' },
        { id: 's2', author: 'Maya', time: '10:42', text: 'Wow thanks for telling me 🙃' },
        { id: 's3', author: 'You', time: '10:43', text: 'I only found out this morning.' }
      ],
      analysis: {
        tone: 'orange',
        status: 'May be sarcastic / frustrated',
        headline: 'Probably not literal, but keep the playful possibility open.',
        confidence: 72,
        caution: '“Wow thanks” is positive on the surface. The upside-down face and the earlier disagreement pull it toward irony, but they do not prove it.',
        literal: 'Maya is thanking you for telling her about the change.',
        implied: [
          'She may be pointing out that the update arrived too late and expressing frustration.',
          'If teasing is normal between you, this could be playful rather than a serious complaint.'
        ],
        emotions: ['frustrated', 'disappointed', 'possibly playful'],
        speechAct: 'Calling attention to a late update',
        literalness: 'Wording may be ironic',
        evidence: '“Wow thanks” sounds positive on its own, but 🙃 often signals that the surface meaning is being bent. The preceding message gives the irony a reason to be there.',
        contextTags: ['late update', 'timing disagreement', '🙃 emoji'],
        action: 'Acknowledge the late notice instead of debating whether the sarcasm is “real.”',
        actionQuote: '“You’re right — I should have told you earlier. Sorry.”'
      }
    },
    permission: {
      contact: 'Maya',
      channel: 'weekend plans',
      target: 'p3',
      messages: [
        { id: 'p1', author: 'Maya', time: '18:06', text: 'I don’t know if I want to go anymore.' },
        { id: 'p2', author: 'You', time: '18:07', text: 'I can stay home if you’d rather.' },
        { id: 'p3', author: 'Maya', time: '18:08', text: 'Do whatever you want.' }
      ],
      analysis: {
        tone: 'blue',
        status: 'Ambiguous',
        headline: 'It may be permission, frustration, or a way to hand the decision back to you.',
        confidence: 56,
        caution: 'Do not assume that “whatever you want” means Maya genuinely does not care. The sentence allows that reading, but the context keeps other readings open.',
        literal: 'Maya says you are free to choose what you do.',
        implied: [
          'She may mean exactly that and be comfortable with either option.',
          'She may feel frustrated or withdrawn and not want to be responsible for the decision.'
        ],
        emotions: ['neutral', 'possibly frustrated', 'resigned'],
        speechAct: 'Giving the decision back to you',
        literalness: 'Words can be literal; intention is unclear',
        evidence: 'The line follows Maya saying she may not want to go. That makes “whatever you want” less like a simple invitation and more like a response to pressure.',
        contextTags: ['change of plan', 'decision pressure', 'short reply'],
        action: 'Ask a specific, low-pressure question that does not make Maya decode your guess.',
        actionQuote: '“Do you actually want me to come, or would space feel better?”'
      }
    },
    fine: {
      contact: 'Maya',
      channel: 'after a disagreement',
      target: 'f3',
      messages: [
        { id: 'f1', author: 'You', time: '21:12', text: 'I can change the plan if this isn’t working.' },
        { id: 'f2', author: 'Maya', time: '21:13', text: 'I don’t want to make this a whole thing.' },
        { id: 'f3', author: 'Maya', time: '21:14', text: 'It’s fine.' }
      ],
      analysis: {
        tone: 'blue',
        status: 'Could be closing the conversation',
        headline: '“Fine” might mean acceptable — or “I do not want to discuss this right now.”',
        confidence: 49,
        caution: 'A short answer can be a boundary, a genuine reassurance, or both. The message alone cannot tell you which one.',
        literal: 'Maya says the situation is acceptable.',
        implied: [
          'She may still be unhappy but not ready to explain what she needs.',
          'She may genuinely want to move on and not see the issue as important anymore.'
        ],
        emotions: ['neutral', 'possibly disappointed', 'possibly tired'],
        speechAct: 'Closing or de-escalating the conversation',
        literalness: 'Could be literal or emotionally softened',
        evidence: 'The short reply comes after Maya says she does not want to make this “a whole thing.” That can signal limited capacity for more conversation, not necessarily that everything feels good.',
        contextTags: ['short reply', 'avoiding a bigger talk', 'boundary'],
        action: 'Respect the possibility that Maya wants to pause, while leaving room for a clearer check-in later.',
        actionQuote: '“Okay. I’ll leave it here — if you do want to talk later, I’m open.”'
      }
    }
  };

  const state = {
    sample: 'sarcasm',
    selected: samples.sarcasm.target,
    custom: null
  };

  const messagesEl = document.querySelector('#messages');
  const readingPanel = document.querySelector('#readingPanel');
  const threadCount = document.querySelector('#threadCount');
  const contextCount = document.querySelector('#contextCount');
  const contextNotice = document.querySelector('#contextNotice');
  const contactName = document.querySelector('#contactName');
  const threadChannel = document.querySelector('#threadChannel');
  const customMessage = document.querySelector('#customMessage');
  const customContext = document.querySelector('#customContext');
  const customAnalyze = document.querySelector('#customAnalyze');
  const privacyDialog = document.querySelector('#privacyDialog');
  const privacyButton = document.querySelector('#privacyButton');
  const closingPrivacyButton = document.querySelector('#closingPrivacyButton');
  const savedState = document.querySelector('#savedState');
  const settingsKey = 'between-settings-v1';
  const defaultSettings = { mode: 'click', contextLength: '3' };
  let settings = loadSettings();

  function escapeHtml(value) {
    return String(value)
      .replaceAll('&', '&amp;')
      .replaceAll('<', '&lt;')
      .replaceAll('>', '&gt;')
      .replaceAll('"', '&quot;')
      .replaceAll("'", '&#039;');
  }

  function icon(name) {
    const icons = {
      alert: '<svg aria-hidden="true" viewBox="0 0 20 20" fill="none"><path d="M10 3.1 17 16H3l7-12.9Z" stroke="currentColor" stroke-width="1.35" stroke-linejoin="round"/><path d="M10 7.1v4.1M10 13.55v.1" stroke="currentColor" stroke-width="1.45" stroke-linecap="round"/></svg>',
      quote: '<svg aria-hidden="true" viewBox="0 0 20 20" fill="none"><path d="M6.9 9.1H4.6a2 2 0 0 0-2 2v1.4a2 2 0 0 0 2 2h1.1a2 2 0 0 0 2-2V8.7c0-2.2-1.1-3.9-3.1-4.7M15.1 9.1h-2.3a2 2 0 0 0-2 2v1.4a2 2 0 0 0 2 2h1.1a2 2 0 0 0 2-2V8.7c0-2.2-1.1-3.9-3.1-4.7" stroke="currentColor" stroke-width="1.25" stroke-linecap="round"/></svg>',
      context: '<svg aria-hidden="true" viewBox="0 0 20 20" fill="none"><path d="M4 4.2h12v8.1a1.5 1.5 0 0 1-1.5 1.5H9l-3.2 2.1v-2.1H5.5A1.5 1.5 0 0 1 4 12.3V4.2Z" stroke="currentColor" stroke-width="1.3" stroke-linejoin="round"/><path d="M6.8 7.2h6.4M6.8 10h4.2" stroke="currentColor" stroke-width="1.25" stroke-linecap="round"/></svg>',
      action: '<svg aria-hidden="true" viewBox="0 0 20 20" fill="none"><path d="M10 3.4v13.2M3.4 10h13.2" stroke="currentColor" stroke-width="1.55" stroke-linecap="round"/></svg>',
      shield: '<svg aria-hidden="true" viewBox="0 0 20 20" fill="none"><path d="M10 2.5 16 5v4.4c0 3.7-2.4 6.9-6 8.1-3.6-1.2-6-4.4-6-8.1V5l6-2.5Z" stroke="currentColor" stroke-width="1.35"/><path d="M7.3 10.1 9.1 12l3.7-4" stroke="currentColor" stroke-width="1.35" stroke-linecap="round" stroke-linejoin="round"/></svg>'
    };
    return icons[name] || '';
  }

  function loadSettings() {
    try {
      const stored = JSON.parse(localStorage.getItem(settingsKey) || '{}');
      return { ...defaultSettings, ...stored };
    } catch (_error) {
      return { ...defaultSettings };
    }
  }

  function saveSettings() {
    try {
      localStorage.setItem(settingsKey, JSON.stringify(settings));
      savedState.textContent = 'Saved on this device';
    } catch (_error) {
      savedState.textContent = 'Used for this session only';
    }
  }

  function applySettings() {
    document.querySelectorAll('input[name="mode"]').forEach((input) => {
      input.checked = input.value === settings.mode;
    });
    document.querySelector('#contextLength').value = settings.contextLength;
  }

  function currentSample() {
    return samples[state.sample];
  }

  function currentMessage() {
    if (state.custom) return { author: 'Your message', time: 'now', text: state.custom.text };
    return currentSample().messages.find((message) => message.id === state.selected) || currentSample().messages[0];
  }

  function renderThread() {
    const sample = currentSample();
    contactName.textContent = sample.contact;
    threadChannel.textContent = sample.channel;
    contextCount.textContent = state.custom ? 'custom input' : `${sample.messages.length} messages`;
    contextNotice.textContent = state.custom ? 'custom message + context used' : `${sample.messages.length} messages included`;
    const selectedIndex = sample.messages.findIndex((message) => message.id === state.selected);
    threadCount.textContent = state.custom ? 'custom' : `${selectedIndex >= 0 ? selectedIndex + 1 : sample.messages.length} / ${sample.messages.length}`;

    messagesEl.innerHTML = sample.messages.map((message) => {
      const isSelected = message.id === state.selected && !state.custom;
      const isTarget = !state.custom && message.id === sample.target;
      return `<button class="message-select${isSelected ? ' is-selected' : ''}" type="button" data-message-id="${escapeHtml(message.id)}" aria-pressed="${isSelected}">
        <span class="message-top"><span><strong>${escapeHtml(message.author)}</strong> · ${escapeHtml(message.time)}</span>${isTarget ? `<span class="message-target">${isSelected ? 'looking at this' : 'look here'} ↗</span>` : ''}</span>
        <span class="message-body">${escapeHtml(message.text)}</span>
      </button>`;
    }).join('');
  }

  function renderSampleTabs() {
    document.querySelectorAll('.sample-tab').forEach((tab) => {
      const active = tab.dataset.sample === state.sample && !state.custom;
      tab.classList.toggle('is-active', active);
      tab.setAttribute('aria-pressed', String(active));
    });
  }

  function renderAnalysis() {
    const message = currentMessage();
    let analysis;
    let source = 'fixture analysis';
    let label = state.custom ? 'CUSTOM MESSAGE' : `INTERPRETATION / ${String(Object.keys(samples).indexOf(state.sample) + 1).padStart(2, '0')}`;

    if (state.custom) {
      analysis = buildHeuristic(state.custom.text, state.custom.context);
      source = 'local demo heuristic';
    } else if (message.id === currentSample().target) {
      analysis = currentSample().analysis;
    } else {
      analysis = buildHeuristic(message.text, currentSample().messages.map((item) => item.text).join(' '));
      source = 'local demo heuristic';
      label = 'MESSAGE CHECK / CONTEXT MATTERS';
    }

    const confidence = Math.max(0, Math.min(100, Number(analysis.confidence) || 0));
    const tone = ['orange', 'blue', 'sage'].includes(analysis.tone) ? analysis.tone : 'blue';
    const emotionTags = analysis.emotions.map((emotion) => `<span class="tiny-tag">${escapeHtml(emotion)}</span>`).join('');
    const implied = analysis.implied.map((item) => `<li>${escapeHtml(item)}</li>`).join('');
    const contextTags = analysis.contextTags.map((tag) => `<span class="context-chip">${escapeHtml(tag)}</span>`).join('');

    readingPanel.innerHTML = `<article class="reading-panel">
      <header class="reading-header">
        <div class="reading-meta"><span class="eyebrow">${escapeHtml(label)}</span><span class="reading-source"><span class="source-dot" aria-hidden="true"></span>${escapeHtml(source)}</span></div>
        <blockquote class="reading-quote">${escapeHtml(message.text)}</blockquote>
        <p class="reading-subtitle">For autistic readers who choose to use it: Between can point out signals, but it cannot know what Maya meant without asking Maya.</p>
      </header>
      <div class="reading-body">
        <div class="verdict-row">
          <div>
            <span class="verdict-label tone-${tone}">${escapeHtml(analysis.status)}</span>
            <p class="verdict-lede">${escapeHtml(analysis.headline)}</p>
          </div>
          <div class="confidence">
            <small>confidence</small>
            <strong>${confidence}%</strong>
            <div class="confidence-bar tone-${tone}" aria-hidden="true"><span style="width: ${confidence}%"></span></div>
          </div>
        </div>
        <div class="uncertainty-note">${icon('alert')}<div><strong>Keep the uncertainty visible.</strong> ${escapeHtml(analysis.caution)}</div></div>
        <div class="reading-divider"></div>
        <div class="reading-grid">
          <article class="insight">
            <div class="insight-kicker">${icon('quote')} what the words say</div>
            <h3>Literal meaning</h3>
            <p>${escapeHtml(analysis.literal)}</p>
          </article>
          <article class="insight">
            <div class="insight-kicker">${icon('context')} beyond the words</div>
            <h3>Possible implied meanings</h3>
            <ul>${implied}</ul>
          </article>
          <article class="insight">
            <div class="insight-kicker">communication layer</div>
            <h3>Possible emotion</h3>
            <div class="tag-row">${emotionTags}</div>
          </article>
          <article class="insight">
            <div class="insight-kicker">communication layer</div>
            <h3>Speech act</h3>
            <p class="speech-act">${escapeHtml(analysis.speechAct)}</p>
            <div class="tag-row"><span class="tiny-tag literalness"><span class="mini-signal" aria-hidden="true"></span>${escapeHtml(analysis.literalness)}</span></div>
          </article>
          <article class="insight full">
            <div class="insight-kicker">${icon('context')} why this reading?</div>
            <h3>Evidence from the nearby context</h3>
            <p class="evidence">${escapeHtml(analysis.evidence)}</p>
            <div class="context-evidence">${contextTags}</div>
          </article>
          <article class="insight full">
            <div class="action-card">
              <span class="action-icon" aria-hidden="true">?</span>
              <div><div class="insight-kicker">a possible next step</div><h3>${escapeHtml(analysis.action)}</h3><p class="action-quote">${escapeHtml(analysis.actionQuote)}</p></div>
            </div>
          </article>
        </div>
        <div class="boundary-box">${icon('shield')}<span><strong>Boundary:</strong> this is one set of possibilities, not a fact about another person. If it matters, asking is more reliable than inferring.</span></div>
      </div>
    </article>`;
  }

  function buildHeuristic(text, context) {
    const message = text.trim();
    const lower = message.toLowerCase();
    const contextText = context.trim();
    if (!message) return buildHeuristic('There is not enough text to read yet.', contextText);

    if (/whatever|do what|up to you|your choice/.test(lower)) {
      return {
        tone: 'blue', status: 'Ambiguous', headline: 'This may grant permission, or it may hand the decision back with some distance.', confidence: 48,
        caution: 'A phrase that sounds like permission can still carry frustration. The message alone cannot distinguish care from withdrawal.',
        literal: 'The writer says you may make the choice yourself.',
        implied: ['They may genuinely be comfortable with either option.', 'They may be tired of deciding, frustrated, or hoping you will notice a preference without them spelling it out.'],
        emotions: ['neutral', 'possibly frustrated', 'withdrawn'], speechAct: 'Returning a decision to you', literalness: 'Could be literal or indirect',
        evidence: contextText ? `The extra context you supplied is part of the picture, but this short phrase still leaves the writer’s preference unstated.` : 'There is no clear marker of whether the permission is warm, reluctant, or final.', contextTags: contextText ? ['custom context added', 'choice language', 'short reply'] : ['choice language', 'short reply', 'no clear signal'],
        action: 'Ask what they would prefer, rather than asking whether they “really mean it.”', actionQuote: '“What would feel best to you?”'
      };
    }

    if (/\bfine\b|\bokay\b|\bok\b/.test(lower)) {
      return {
        tone: 'blue', status: 'Not enough context', headline: 'This could be reassurance, a boundary, or a softened way to end the exchange.', confidence: 39,
        caution: 'Short replies often carry less information than we want them to. Do not turn a vague signal into a certain emotion.',
        literal: 'The writer says the situation is acceptable.',
        implied: ['They may be genuinely okay and ready to move on.', 'They may not want to explain more right now, even if the situation still feels difficult.'],
        emotions: ['neutral', 'possibly tired', 'unclear'], speechAct: 'Reassuring or closing', literalness: 'No strong signal either way',
        evidence: contextText ? 'The context may change the reading, but the message itself does not tell us whether “okay” means content, finished, or avoiding a longer conversation.' : 'The message is too short to separate an emotional state from a conversational boundary.', contextTags: contextText ? ['custom context added', 'short reply', 'softened language'] : ['short reply', 'softened language', 'more context needed'],
        action: 'Ask one gentle, concrete question and make it easy not to answer immediately.', actionQuote: '“Are you okay with the plan, or would you rather pause?”'
      };
    }

    if (/🙃|wow thanks|great|sure|lol|yeah right|exactly what i needed/.test(lower)) {
      return {
        tone: 'orange', status: 'Possible irony or tonal mismatch', headline: 'The surface words and the surrounding situation may be pulling in different directions.', confidence: 45,
        caution: 'Irony is one possibility, not a translation. Playfulness, habit, or a genuinely positive message can look similar in text.',
        literal: `The writer’s literal words are: “${message}”.`,
        implied: ['They may be saying the opposite of the surface wording to signal annoyance or disbelief.', 'They may be joking or softening a genuine reaction rather than making a serious complaint.'],
        emotions: ['possibly annoyed', 'possibly playful', 'unclear'], speechAct: 'Reacting to what came before', literalness: 'Could be nonliteral',
        evidence: contextText ? 'The custom context may explain the mismatch, but a text-only reading should keep at least one literal possibility open.' : 'The wording includes a common tonal cue, but no message can establish intention without more context.', contextTags: contextText ? ['custom context added', 'tonal cue', 'literal reading remains'] : ['tonal cue', 'surface positivity', 'literal reading remains'],
        action: 'Name the situation you are responding to and invite correction.', actionQuote: '“I may be reading that wrong — are you annoyed, or are you joking?”'
      };
    }

    return {
      tone: 'blue', status: 'Several readings are possible', headline: 'The message does not contain enough signal for a confident interpretation.', confidence: 28,
      caution: 'A confident label would add information that is not in the message. Keep the literal meaning and ask if the distinction matters.',
      literal: `The writer says: “${message}”.`,
      implied: ['They may mean the words directly.', 'They may be implying a request, feeling, or boundary that would only become clear with more context.'],
      emotions: ['unclear', 'possibly neutral'], speechAct: 'Responding to the conversation', literalness: 'No strong signal either way',
      evidence: contextText ? 'You supplied context, but the prototype heuristic cannot reliably turn it into a single intention. A person’s own clarification is better evidence.' : 'No surrounding context was supplied, so there is no responsible basis for a stronger reading.', contextTags: contextText ? ['custom context added', 'literal reading remains', 'ask if it matters'] : ['message alone', 'literal reading remains', 'more context needed'],
      action: 'Ask a clear question that gives the other person room to correct the interpretation.', actionQuote: '“What did you mean by that?”'
    };
  }

  function selectSample(sampleName) {
    if (!samples[sampleName]) return;
    state.sample = sampleName;
    state.selected = samples[sampleName].target;
    state.custom = null;
    customMessage.value = '';
    customContext.value = '';
    renderSampleTabs();
    renderThread();
    renderAnalysis();
  }

  document.querySelector('.sample-nav').addEventListener('click', (event) => {
    const tab = event.target.closest('[data-sample]');
    if (tab) selectSample(tab.dataset.sample);
  });

  messagesEl.addEventListener('click', (event) => {
    const button = event.target.closest('[data-message-id]');
    if (!button) return;
    state.selected = button.dataset.messageId;
    state.custom = null;
    customMessage.value = '';
    customContext.value = '';
    renderSampleTabs();
    renderThread();
    renderAnalysis();
  });

  customAnalyze.addEventListener('click', () => {
    const text = customMessage.value.trim();
    if (!text) {
      customMessage.focus();
      customMessage.setAttribute('aria-invalid', 'true');
      customMessage.placeholder = 'Add a message first…';
      return;
    }
    customMessage.removeAttribute('aria-invalid');
    state.custom = { text, context: customContext.value.trim() };
    renderSampleTabs();
    renderThread();
    renderAnalysis();
    readingPanel.scrollIntoView({ behavior: 'smooth', block: 'start' });
  });

  customMessage.addEventListener('input', () => {
    customMessage.removeAttribute('aria-invalid');
  });

  function openPrivacy() {
    applySettings();
    if (typeof privacyDialog.showModal === 'function') privacyDialog.showModal();
    else privacyDialog.setAttribute('open', '');
  }

  privacyButton.addEventListener('click', openPrivacy);
  closingPrivacyButton.addEventListener('click', openPrivacy);
  privacyDialog.addEventListener('click', (event) => {
    if (event.target === privacyDialog) privacyDialog.close();
  });

  document.querySelectorAll('input[name="mode"]').forEach((input) => {
    input.addEventListener('change', () => {
      settings.mode = input.value;
      saveSettings();
    });
  });
  document.querySelector('#contextLength').addEventListener('change', (event) => {
    settings.contextLength = event.target.value;
    saveSettings();
  });

  applySettings();
  renderSampleTabs();
  renderThread();
  renderAnalysis();
})();
