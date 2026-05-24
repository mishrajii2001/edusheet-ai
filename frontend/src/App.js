import React, { useState, useEffect } from 'react';
import './App.css';
import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://127.0.0.1:8000';

const SECTIONS = [
  { key: 'aim', label: 'Aim', icon: '🎯' },
  { key: 'introduction', label: 'Introduction', icon: '📖' },
  { key: 'objective', label: 'Objective', icon: '✅' },
  { key: 'apparatus', label: 'Apparatus', icon: '🔧' },
  { key: 'theory', label: 'Theory', icon: '💡' },
  { key: 'algorithm', label: 'Algorithm', icon: '⚙️' },
  { key: 'code', label: 'Code', icon: '💻' },
  { key: 'expected_output', label: 'Expected Output', icon: '📊' },
  { key: 'result', label: 'Result', icon: '📋' },
  { key: 'conclusion', label: 'Conclusion', icon: '🏁' },
  { key: 'learning_outcomes', label: 'Learning Outcomes', icon: '🎓' },
  { key: 'viva_questions', label: 'Viva Questions', icon: '❓' },
  { key: 'references', label: 'References', icon: '📚' },
];

const FONTS = ['Times New Roman', 'Arial', 'Calibri', 'Georgia', 'Garamond'];
const ALIGNMENTS = ['justified', 'left', 'center', 'right'];
const LANGUAGES = ['Python', 'Java', 'C++', 'C', 'JavaScript', 'R', 'MATLAB'];

const STEPS = [
  { icon: '🌐', label: 'Searching the web' },
  { icon: '🤖', label: 'AI generating content' },
  { icon: '📄', label: 'Formatting document' },
  { icon: '✅', label: 'Almost ready!' },
];

export default function App() {
  const [darkMode, setDarkMode] = useState(true);
  const [activeTab, setActiveTab] = useState('content');
  const [topic, setTopic] = useState('');
  const [description, setDescription] = useState('');
  const [code, setCode] = useState('');
  const [customInstructions, setCustomInstructions] = useState('');
  const [customSections, setCustomSections] = useState('');
  const [programmingLanguage, setProgrammingLanguage] = useState('Python');
  const [sections, setSections] = useState(['objective', 'theory', 'code', 'learning_outcomes']);
  const [fontFamily, setFontFamily] = useState('Times New Roman');
  const [headingSize, setHeadingSize] = useState(14);
  const [bodySize, setBodySize] = useState(12);
  const [alignment, setAlignment] = useState('justified');
  const [margin, setMargin] = useState(1.0);
  const [loading, setLoading] = useState(false);
  const [loadingStep, setLoadingStep] = useState(0);
  const [error, setError] = useState('');
  const [fileName, setFileName] = useState('');

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', darkMode ? 'dark' : 'light');
  }, [darkMode]);

  useEffect(() => {
    if (!loading) { setLoadingStep(0); return; }
    const id = setInterval(() => setLoadingStep(s => (s < STEPS.length - 1 ? s + 1 : s)), 5000);
    return () => clearInterval(id);
  }, [loading]);

  const toggleSection = (key) => {
    setSections(prev => prev.includes(key) ? prev.filter(s => s !== key) : [...prev, key]);
  };

  const handleGenerate = async () => {
    if (!topic && !code) { setError('Please enter a topic or paste your code'); return; }
    const allSections = [...sections];
    if (customSections.trim()) {
      customSections.split(',').map(s => s.trim().toLowerCase().replace(/ /g, '_')).filter(Boolean)
        .forEach(s => { if (!allSections.includes(s)) allSections.push(s); });
    }
    if (allSections.length === 0) { setError('Please select at least one section'); return; }
    setLoading(true); setError(''); setFileName('');
    const formatting = { font_family: fontFamily, heading_size: headingSize, subheading_size: headingSize - 1, body_size: bodySize, alignment, margin };
    const params = new URLSearchParams();
    if (topic) params.append('topic', topic);
    if (description) params.append('description', description);
    if (code) params.append('code', code);
    if (customInstructions) params.append('custom_instructions', customInstructions);
    params.append('sections', JSON.stringify(allSections));
    params.append('programming_language', programmingLanguage);
    params.append('formatting', JSON.stringify(formatting));
    try {
      const res = await axios.post(`${API_URL}/api/worksheet/generate`, params);
      if (res.data.success) setFileName(res.data.file_name);
    } catch (err) {
      setError(err.response?.data?.detail || 'Something went wrong. Please try again.');
    } finally { setLoading(false); }
  };

  const handleDownload = () => window.open(`${API_URL}/api/worksheet/download/${fileName}`, '_blank');

  const resetAll = () => { setFileName(''); setTopic(''); setCode(''); setDescription(''); setCustomInstructions(''); setActiveTab('content'); };

  return (
    <div className="app">
      {/* Animated background orbs */}
      <div className="bg-orb orb1" />
      <div className="bg-orb orb2" />
      <div className="bg-orb orb3" />

      {/* Header */}
      <header className="header">
        <div className="header-inner">
          <div className="logo">
            <div className="logo-badge">
              <span>📝</span>
            </div>
            <div className="logo-text">
              <h1>EduSheet <span className="logo-accent">AI</span></h1>
              <p>College worksheets in seconds</p>
            </div>
          </div>
          <div className="header-right">
            <div className="status-pill">
              <span className="status-dot" />
              API Connected
            </div>
            <button className="theme-btn" onClick={() => setDarkMode(!darkMode)}>
              {darkMode ? '☀️' : '🌙'}
            </button>
          </div>
        </div>
      </header>

      <main className="main">
        {/* Hero section */}
        <div className="hero">
          <div className="hero-badge">✨ Powered by LLaMA 3 + RAG + LangChain</div>
          <h2 className="hero-title">Generate Perfect<br /><span className="gradient-text">Lab Worksheets</span></h2>
          <p className="hero-sub">Just enter your topic or paste your code — AI handles the rest.</p>
        </div>

        {/* Tab Navigation */}
        <div className="tab-nav">
          {[
            { id: 'content', label: 'Content', icon: '📝', num: 1 },
            { id: 'sections', label: 'Sections', icon: '📋', num: 2 },
            { id: 'formatting', label: 'Format', icon: '🎨', num: 3 },
          ].map(t => (
            <button key={t.id} className={`tab-btn ${activeTab === t.id ? 'active' : ''}`} onClick={() => setActiveTab(t.id)}>
              <span className="tab-num">{t.num}</span>
              <span>{t.icon} {t.label}</span>
              {activeTab === t.id && <span className="tab-active-bar" />}
            </button>
          ))}
        </div>

        {/* Content Tab */}
        {activeTab === 'content' && (
          <div className="card slide-in">
            <div className="card-title">
              <span>📝</span> Topic & Content
            </div>

            <div className="field">
              <label>Topic / Experiment Name <span className="req">*</span></label>
              <input className={`inp ${topic ? 'inp-filled' : ''}`} type="text" placeholder="e.g. Bubble Sort Algorithm" value={topic} onChange={e => setTopic(e.target.value)} />
            </div>

            <div className="field">
              <label>Description <span className="opt">optional</span></label>
              <input className="inp" type="text" placeholder="e.g. Focus on time complexity, include real world examples" value={description} onChange={e => setDescription(e.target.value)} />
            </div>

            <div className="field">
              <label>Paste Your Code <span className="opt">optional</span></label>
              <div className="code-wrap">
                <div className="code-top">
                  <div className="code-dots"><span /><span /><span /></div>
                  <span className="code-lang">{programmingLanguage}</span>
                </div>
                <textarea className="code-area" rows={7} placeholder="# Paste your code here — AI will analyze and use it..." value={code} onChange={e => setCode(e.target.value)} />
              </div>
            </div>

            <div className="field">
              <label>Custom Instructions <span className="opt">optional</span></label>
              <input className="inp" type="text" placeholder="e.g. Keep theory under 100 words, add 5 viva questions" value={customInstructions} onChange={e => setCustomInstructions(e.target.value)} />
            </div>

            <div className="field">
              <label>Programming Language</label>
              <div className="pill-row">
                {LANGUAGES.map(l => (
                  <button key={l} className={`pill ${programmingLanguage === l ? 'pill-active' : ''}`} onClick={() => setProgrammingLanguage(l)}>{l}</button>
                ))}
              </div>
            </div>

            <button className="btn-next" onClick={() => setActiveTab('sections')}>
              Continue to Sections <span>→</span>
            </button>
          </div>
        )}

        {/* Sections Tab */}
        {activeTab === 'sections' && (
          <div className="card slide-in">
            <div className="card-title"><span>📋</span> Sections to Include</div>
            <p className="card-hint">Select sections in the order you want them in your worksheet</p>

            {sections.length > 0 && (
              <div className="order-strip">
                <span className="order-label">Order:</span>
                {sections.map((s, i) => {
                  const found = SECTIONS.find(x => x.key === s);
                  return (
                    <span key={s} className="order-tag">
                      <span className="order-num">{i + 1}</span>
                      {found ? found.label : s.replace(/_/g, ' ')}
                      <button className="order-remove" onClick={() => toggleSection(s)}>×</button>
                    </span>
                  );
                })}
              </div>
            )}

            <div className="sec-grid">
              {SECTIONS.map(s => (
                <button key={s.key} className={`sec-btn ${sections.includes(s.key) ? 'sec-active' : ''}`} onClick={() => toggleSection(s.key)}>
                  <span className="sec-icon">{s.icon}</span>
                  <span className="sec-label">{s.label}</span>
                  {sections.includes(s.key) && <span className="sec-num">{sections.indexOf(s.key) + 1}</span>}
                </button>
              ))}
            </div>

            <div className="field" style={{ marginTop: 20 }}>
              <label>➕ Custom Sections <span className="opt">separate with commas</span></label>
              <input className="inp" type="text" placeholder="e.g. Aim, Introduction, Task to be Done, Apparatus" value={customSections} onChange={e => setCustomSections(e.target.value)} />
            </div>

            <div className="btn-row">
              <button className="btn-back" onClick={() => setActiveTab('content')}>← Back</button>
              <button className="btn-next" onClick={() => setActiveTab('formatting')}>Continue →</button>
            </div>
          </div>
        )}

        {/* Formatting Tab */}
        {activeTab === 'formatting' && (
          <div className="card slide-in">
            <div className="card-title"><span>🎨</span> Formatting Settings</div>
            <p className="card-hint">Set formatting exactly as per your college requirements</p>

            <div className="two-col">
              <div className="field">
                <label>Font Family</label>
                <select className="sel" value={fontFamily} onChange={e => setFontFamily(e.target.value)}>
                  {FONTS.map(f => <option key={f}>{f}</option>)}
                </select>
              </div>
              <div className="field">
                <label>Text Alignment</label>
                <select className="sel" value={alignment} onChange={e => setAlignment(e.target.value)}>
                  {ALIGNMENTS.map(a => <option key={a}>{a.charAt(0).toUpperCase() + a.slice(1)}</option>)}
                </select>
              </div>
            </div>

            <div className="sliders">
              {[
                { label: 'Heading Size', val: headingSize, set: setHeadingSize, min: 12, max: 20 },
                { label: 'Body Text Size', val: bodySize, set: setBodySize, min: 10, max: 16 },
                { label: 'Page Margin (inches)', val: margin, set: setMargin, min: 0.5, max: 2, step: 0.1 },
              ].map(s => (
                <div key={s.label} className="slider-row">
                  <div className="slider-top">
                    <span className="slider-label">{s.label}</span>
                    <span className="slider-val">{s.val}{s.label.includes('Size') ? 'pt' : '"'}</span>
                  </div>
                  <input type="range" min={s.min} max={s.max} step={s.step || 1} value={s.val} onChange={e => s.set(Number(e.target.value))} />
                </div>
              ))}
            </div>

            <div className="preview-box">
              <p style={{ fontFamily, fontSize: headingSize, fontWeight: 'bold', marginBottom: 6, color: 'var(--text)' }}>
                Heading Preview — {fontFamily} {headingSize}pt
              </p>
              <p style={{ fontFamily, fontSize: bodySize, color: 'var(--text2)' }}>
                Body text preview — {fontFamily} {bodySize}pt, {alignment}
              </p>
            </div>

            <div className="btn-row">
              <button className="btn-back" onClick={() => setActiveTab('sections')}>← Back</button>
            </div>
          </div>
        )}

        {/* Error */}
        {error && (
          <div className="error-box">
            <span>⚠️</span> {error}
          </div>
        )}

        {/* Loading */}
        {loading && (
          <div className="card loading-card slide-in">
            <div className="loader-ring">
              <div /><div /><div /><div />
            </div>
            <p className="loading-title">Generating your worksheet...</p>
            <p className="loading-sub">This usually takes 15–25 seconds</p>
            <div className="steps-list">
              {STEPS.map((s, i) => (
                <div key={i} className={`step-item ${i < loadingStep ? 'done' : i === loadingStep ? 'active' : 'pending'}`}>
                  <span className="step-icon">{i < loadingStep ? '✓' : s.icon}</span>
                  <span>{s.label}</span>
                  {i === loadingStep && <div className="step-pulse" />}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Success */}
        {fileName && !loading && (
          <div className="success-card slide-in">
            <div className="success-glow" />
            <div className="success-icon">🎉</div>
            <h3>Worksheet Ready!</h3>
            <p>Your formatted worksheet has been generated successfully.</p>
            <div className="success-btns">
              <button className="btn-download" onClick={handleDownload}>
                ⬇️ Download Worksheet
              </button>
              <button className="btn-new" onClick={resetAll}>
                ✨ Generate Another
              </button>
            </div>
          </div>
        )}

        {/* Generate Button */}
        <button className={`btn-generate ${loading ? 'btn-loading' : ''}`} onClick={handleGenerate} disabled={loading}>
          {loading ? (
            <><span className="btn-spinner" /> Generating...</>
          ) : (
            <>✨ Generate Worksheet</>
          )}
        </button>

      </main>

      <footer className="footer">
        <p>EduSheet AI — Built with ❤️ for college students &nbsp;|&nbsp; Powered by LangChain + Groq + ChromaDB</p>
      </footer>
    </div>
  );
}