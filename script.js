'use strict';

const components = {
  user: {
    title: 'More controllable conversations.',
    description: 'Combine explicit symbolic rules with natural LLM responses. The meta-agent can revise disclosure rules, persona instructions, generation settings, and the mixture between the two simulators.',
    knobs: ['Symbolic rules', 'Mixing coefficient ε', 'User persona'],
  },
  environment: {
    title: 'A more informative learning signal.',
    description: 'Revise intermediate rewards when task success is too sparse to guide exploration. The meta-agent can reward meaningful progress, correct unhelpful reward designs, and adjust supported interaction limits.',
    knobs: ['Intermediate rewards', 'Reward rules', 'Episode length'],
  },
  agent: {
    title: 'Training dynamics that can adapt.',
    description: 'The neural policy learns through PPO with an action-token critic. The meta-agent monitors optimization logs and trajectories, adjusting configurable dynamics such as entropy and KL coefficients while keeping the training algorithm fixed.',
    knobs: ['Entropy coefficient', 'KL coefficient', 'Training diagnostics'],
  },
};

const tabs = [...document.querySelectorAll('[data-component]')];
function selectComponent(tab, focus = false) {
  const name = tab.dataset.component;
  const content = components[name];
  tabs.forEach(item => {
    const selected = item === tab;
    item.setAttribute('aria-selected', String(selected));
    item.tabIndex = selected ? 0 : -1;
  });
  document.querySelector('#component-panel').setAttribute('aria-labelledby', tab.id);
  document.querySelector('#component-title').textContent = content.title;
  document.querySelector('#component-description').textContent = content.description;
  document.querySelector('#component-knobs').replaceChildren(...content.knobs.map(knob => {
    const span = document.createElement('span');
    span.textContent = knob;
    return span;
  }));
  document.querySelector('.system-diagram').dataset.active = name;
  document.querySelectorAll('[data-node]').forEach(node => node.classList.toggle('is-active', node.dataset.node === name));
  if (focus) tab.focus();
}
tabs.forEach((tab, index) => {
  tab.addEventListener('click', () => selectComponent(tab));
  tab.addEventListener('keydown', event => {
    let target;
    if (event.key === 'ArrowRight' || event.key === 'ArrowDown') target = (index + 1) % tabs.length;
    if (event.key === 'ArrowLeft' || event.key === 'ArrowUp') target = (index - 1 + tabs.length) % tabs.length;
    if (event.key === 'Home') target = 0;
    if (event.key === 'End') target = tabs.length - 1;
    if (target !== undefined) {
      event.preventDefault();
      selectComponent(tabs[target], true);
    }
  });
});

// Values transcribed from tables/usergym_results.tex. See README for source discrepancies.
// Columns: method, UserGym average, ColBench pass, ColBench success, overall.
const results = {
  qwen3: {
    label: 'Qwen3-4B',
    rows: [
      ['Backbone', .426, .272, .153, .378],
      ['ReAct', .457, .269, .145, .401],
      ['Reflexion', .455, .303, .184, .408],
      ['RAGEN', .468, .479, .361, .457],
      ['Search-R1', .472, .467, .355, .459],
      ['UserRL', .509, .468, .342, .486],
      ['InfoPO', .559, .553, .439, .545],
      ['PPO', .522, .284, .200, .462],
      ['eau', .623, .685, .600, .627],
    ],
  },
  qwen25: {
    label: 'Qwen2.5-7B-Instruct',
    rows: [
      ['Backbone', .338, .242, .140, .305],
      ['ReAct', .379, .238, .135, .336],
      ['Reflexion', .361, .276, .168, .330],
      ['RAGEN', .513, .449, .348, .487],
      ['Search-R1', .501, .457, .352, .480],
      ['UserRL', .508, .436, .327, .480],
      ['InfoPO', .563, .534, .426, .544],
      ['PPO', .568, .356, .240, .508],
      ['eau', .632, .659, .533, .615],
    ],
  },
};
const metrics = [
  {title: 'UserGym', subtitle: 'Average score', column: 1},
  {title: 'ColBench', subtitle: 'Successful task completion', column: 3},
  {title: 'Overall', subtitle: 'UserGym + ColBench', column: 4},
];
function renderResults(key) {
  const data = results[key];
  const baseline = data.rows.find(row => row[0] === 'InfoPO');
  const eau = data.rows.find(row => row[0] === 'eau');
  document.querySelectorAll('[data-model]').forEach(button => button.setAttribute('aria-pressed', String(button.dataset.model === key)));
  document.querySelector('#result-charts').innerHTML = metrics.map(metric => {
    const b = baseline[metric.column];
    const e = eau[metric.column];
    const gain = ((e / b - 1) * 100).toFixed(1);
    // Each panel uses the same zero baseline and 0–0.8 scale across both models.
    const height = value => (value / .8 * 82).toFixed(2);
    return `<article class="chart-card" aria-label="${data.label}, ${metric.title} ${metric.subtitle}: InfoPO ${b.toFixed(3)}, eau ${e.toFixed(3)}, relative gain ${gain} percent.">
      <div class="chart-top"><h3>${metric.title}</h3><span class="gain">+${gain}%</span></div>
      <p class="chart-subtitle">${metric.subtitle}</p>
      <div class="bar-plot" aria-hidden="true"><div class="bar-column"><span class="bar-value">${b.toFixed(3)}</span><div class="bar" style="height:${height(b)}%"></div></div><div class="bar-column eau"><span class="bar-value">${e.toFixed(3)}</span><div class="bar" style="height:${height(e)}%"></div></div></div>
      <div class="bar-labels" aria-hidden="true"><span>InfoPO</span><span>eau</span></div>
    </article>`;
  }).join('');
  document.querySelector('#table-caption').textContent = `${data.label} · UserGym and ColBench`;
  document.querySelector('#results-table-body').innerHTML = data.rows.map(row => `<tr${row[0] === 'eau' ? ' class="ours"' : ''}><th scope="row">${row[0]}</th>${row.slice(1).map(value => `<td>${value.toFixed(3)}</td>`).join('')}</tr>`).join('');
}
document.querySelectorAll('[data-model]').forEach(button => button.addEventListener('click', () => renderResults(button.dataset.model)));
renderResults('qwen3');

document.querySelector('#copy-citation').addEventListener('click', async () => {
  const citation = document.querySelector('#citation').textContent;
  const status = document.querySelector('#copy-status');
  try {
    if (navigator.clipboard && window.isSecureContext) {
      await navigator.clipboard.writeText(citation);
    } else {
      const textarea = document.createElement('textarea');
      textarea.value = citation;
      textarea.setAttribute('readonly', '');
      textarea.style.cssText = 'position:fixed;left:-9999px;top:0';
      document.body.appendChild(textarea);
      textarea.select();
      const copied = document.execCommand('copy');
      textarea.remove();
      if (!copied) throw new Error('Clipboard unavailable');
    }
    status.textContent = 'Citation copied.';
  } catch {
    const selection = window.getSelection();
    const range = document.createRange();
    range.selectNodeContents(document.querySelector('#citation'));
    selection.removeAllRanges();
    selection.addRange(range);
    status.textContent = 'Citation selected. Press Ctrl+C or ⌘C to copy.';
  }
});

// Refuse unsafe link schemes when applying optional publication configuration.
function publicationUrl(value) {
  if (typeof value !== 'string' || !value.trim()) return null;
  try {
    const url = new URL(value, window.location.href);
    return ['https:', 'http:', 'file:'].includes(url.protocol) ? url.href : null;
  } catch { return null; }
}
const config = window.EAU_CONFIG || {};
const paperUrl = publicationUrl(config.paperUrl);
if (paperUrl) {
  document.querySelectorAll('[data-paper-link]').forEach(link => {
    link.href = paperUrl;
    link.removeAttribute('download');
    link.target = '_blank';
    link.rel = 'noopener';
    link.innerHTML = 'Read the paper <span aria-hidden="true">↗</span>';
  });
}
const codeUrl = publicationUrl(config.codeUrl);
if (codeUrl) {
  const link = document.querySelector('#code-link');
  link.href = codeUrl;
  link.target = '_blank';
  link.rel = 'noopener';
  link.hidden = false;
  document.querySelector('#code-status').hidden = true;
}
