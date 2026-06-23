import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';
import { BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, LineChart, Line } from 'recharts';
import Chatbot from './Chatbot';

function App() {
  const [file, setFile] = useState(null);
  const [analysisType, setAnalysisType] = useState('quality_control');
  const [results, setResults] = useState(null);
  const [history, setHistory] = useState([]);
  const [preview, setPreview] = useState(null);
  const [loading, setLoading] = useState(false);
  const [previewLoading, setPreviewLoading] = useState(false);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('guide');
  const [activeAnalysisTab, setActiveAnalysisTab] = useState('overview');

  const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000';

  // Load history on mount
  useEffect(() => {
    loadHistory();
  }, []);

  const loadHistory = async () => {
    try {
      const response = await axios.get(`${API_BASE}/api/history`);
      setHistory(response.data);
    } catch (err) {
      console.error('Failed to load history:', err);
    }
  };

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
    setError(null);
    setPreview(null);
  };

  const handlePreview = async () => {
    if (!file) {
      setError('Please select a file');
      return;
    }

    setPreviewLoading(true);
    setError(null);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post(`${API_BASE}/api/preview`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setPreview(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Preview failed');
    } finally {
      setPreviewLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) {
      setError('Please select a file');
      return;
    }

    setLoading(true);
    setError(null);
    const formData = new FormData();
    formData.append('file', file);

    try {
      let endpoint;
      
      switch(analysisType) {
        case 'quality_control':
          endpoint = `${API_BASE}/api/analyze/quality-control`;
          break;
        case 'sequence':
          endpoint = `${API_BASE}/api/analyze/sequence`;
          break;
        case 'quality_scores':
          endpoint = `${API_BASE}/api/analyze/quality-scores`;
          break;
        case 'base_frequency':
          endpoint = `${API_BASE}/api/analyze/base-frequency`;
          break;
        case 'orfs':
          endpoint = `${API_BASE}/api/analyze/orfs`;
          break;
        case 'translation':
          endpoint = `${API_BASE}/api/analyze/translation`;
          break;
        case 'dinucleotides':
          endpoint = `${API_BASE}/api/analyze/dinucleotides`;
          break;
        case 'repeats':
          endpoint = `${API_BASE}/api/analyze/repeats`;
          break;
        case 'alignment':
          endpoint = `${API_BASE}/api/analyze/alignment`;
          break;
        default:
          endpoint = `${API_BASE}/api/analyze/quality-control`;
      }
      
      const response = await axios.post(endpoint, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      
      setResults(response.data);
      setActiveAnalysisTab('overview');
      setActiveTab('results');
      loadHistory();
      setFile(null);
      setPreview(null);
    } catch (err) {
      setError(err.response?.data?.detail || 'Analysis failed');
    } finally {
      setLoading(false);
    }
  };

  const handleExport = (resultId, format) => {
    window.open(`${API_BASE}/api/export/${resultId}/${format}`, '_blank');
  };

  const viewResultFromHistory = async (resultId) => {
    try {
      const response = await axios.get(`${API_BASE}/api/result/${resultId}`);
      setResults(response.data);
      setActiveTab('results');
    } catch (err) {
      setError('Failed to load result');
    }
  };

  const renderGCContentChart = () => {
    if (!results || results.analysis_type !== 'quality_control' || !results.sequences) return null;
    
    const data = results.sequences.map((seq, idx) => ({
      name: seq.id.substring(0, 15),
      gc: parseFloat(seq.gc_content)
    }));

    return (
      <div className="chart-container">
        <h4>GC Content Distribution</h4>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={data}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" angle={-45} textAnchor="end" height={80} />
            <YAxis />
            <Tooltip />
            <Bar dataKey="gc" fill="#667eea" />
          </BarChart>
        </ResponsiveContainer>
      </div>
    );
  };

  const renderNucleotideChart = () => {
    if (!results || results.analysis_type !== 'sequence_analysis' || !results.summary || !results.summary.nucleotide_composition) return null;
    
    const composition = results.summary.nucleotide_composition;
    const data = [
      { name: 'A', value: composition.A },
      { name: 'T', value: composition.T },
      { name: 'G', value: composition.G },
      { name: 'C', value: composition.C }
    ].filter(item => item.value > 0);

    const COLORS = ['#667eea', '#764ba2', '#f093fb', '#4facfe'];

    return (
      <div className="chart-container">
        <h4>Nucleotide Composition</h4>
        <ResponsiveContainer width="100%" height={300}>
          <PieChart>
            <Pie data={data} cx="50%" cy="50%" labelLine={false} label>
              {data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip />
            <Legend />
          </PieChart>
        </ResponsiveContainer>
      </div>
    );
  };

  const renderSequenceLengthChart = () => {
    if (!results || !results.sequences) return null;
    
    const data = results.sequences.slice(0, 20).map((seq, idx) => ({
      name: seq.id.substring(0, 12),
      length: seq.length
    }));

    return (
      <div className="chart-container">
        <h4>Sequence Length Distribution (First 20)</h4>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={data}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" angle={-45} textAnchor="end" height={80} />
            <YAxis />
            <Tooltip />
            <Bar dataKey="length" fill="#764ba2" />
          </BarChart>
        </ResponsiveContainer>
      </div>
    );
  };

  const renderBaseFrequencyHeatmap = () => {
    if (!results || results.analysis_type !== 'base_frequency') return null;
    
    const data = results.data?.sequences || [];
    
    return (
      <div className="chart-container">
        <h4>Base Frequency Distribution</h4>
        {data.map((seq, idx) => (
          <div key={idx} className="heatmap-item">
            <strong>{seq.id}</strong>
            <div className="frequency-grid">
              {seq.frequencies.slice(0, 20).map((freq, i) => (
                <div key={i} className="frequency-cell" title={`Position ${i}: A=${freq.A}% T=${freq.T}% G=${freq.G}% C=${freq.C}%`}>
                  <div style={{
                    background: `rgb(${freq.G + freq.C}, ${freq.A + freq.T}, 100)`,
                    width: '30px',
                    height: '30px',
                    borderRadius: '3px'
                  }}></div>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    );
  };

  const renderORFsAnalysis = () => {
    if (!results || results.analysis_type !== 'orfs') return null;
    
    const data = results.data?.sequences || [];
    
    return (
      <div className="chart-container">
        <h4>Open Reading Frames (ORFs)</h4>
        <p>Total ORFs found: <strong>{results.data?.total_orfs || 0}</strong></p>
        {data.map((seq, idx) => (
          <div key={idx} className="sequence-analysis">
            <strong>{seq.id}</strong> - <em>{seq.orfs.length} ORFs found</em>
            {seq.orfs.slice(0, 5).map((orf, i) => (
              <div key={i} className="orf-item">
                <p>ORF {i+1}: {orf.start}-{orf.end} ({orf.length}bp) - Frame: {orf.frame}, Strand: {orf.strand}</p>
              </div>
            ))}
          </div>
        ))}
      </div>
    );
  };

  const renderTranslation = () => {
    if (!results || results.analysis_type !== 'translation') return null;
    
    const data = results.data?.sequences || [];
    
    return (
      <div className="chart-container">
        <h4>DNA to Protein Translation</h4>
        {data.map((seq, idx) => (
          <div key={idx} className="translation-item">
            <strong>{seq.id}</strong>
            <p>DNA Length: {seq.dna_length}bp | Protein Length: {seq.protein_length}aa</p>
            <div className="protein-display">
              <code>{seq.protein.substring(0, 100)}...</code>
            </div>
          </div>
        ))}
      </div>
    );
  };

  const renderDinucleotides = () => {
    if (!results || results.analysis_type !== 'dinucleotides') return null;
    
    const globalDinuc = results.data?.global_dinucleotides || {};
    const data = Object.entries(globalDinuc).map(([name, value]) => ({ name, value }));
    
    return (
      <div className="chart-container">
        <h4>Dinucleotide Frequencies</h4>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={data}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" />
            <YAxis />
            <Tooltip />
            <Bar dataKey="value" fill="#f093fb" />
          </BarChart>
        </ResponsiveContainer>
      </div>
    );
  };

  const renderRepeats = () => {
    if (!results || results.analysis_type !== 'repeats') return null;
    
    const data = results.data?.sequences || [];
    
    return (
      <div className="chart-container">
        <h4>Repetitive Sequences</h4>
        <p>Total repeats found: <strong>{results.data?.total_repeats || 0}</strong></p>
        {data.map((seq, idx) => (
          <div key={idx} className="repeat-analysis">
            <strong>{seq.id}</strong> - {seq.repeats.length} repeats
            {seq.repeats.slice(0, 3).map((repeat, i) => (
              <div key={i} className="repeat-item">
                <p>Unit: {repeat.unit} (x{repeat.repeat_count}, {repeat.total_length}bp)</p>
              </div>
            ))}
          </div>
        ))}
      </div>
    );
  };

  const renderAlignment = () => {
    if (!results || results.analysis_type !== 'alignment') return null;
    
    const data = results.data?.alignments || [];
    
    return (
      <div className="chart-container">
        <h4>Multiple Sequence Alignment</h4>
        {data.map((align, idx) => (
          <div key={idx} className="alignment-item">
            <strong>{align.reference} vs {align.query}</strong>
            <p>Identity: {align.identity}% | Score: {align.score}</p>
            <div className="alignment-display">
              <code>{align.seq1_aligned.substring(0, 80)}</code><br/>
              <code>{align.seq2_aligned.substring(0, 80)}</code>
            </div>
          </div>
        ))}
      </div>
    );
  };

  // Dashboard Statistics Functions
  const calculateStatistics = () => {
    const stats = {
      totalAnalyses: history.length,
      totalSequences: history.reduce((sum, h) => sum + (h.total_sequences || 0), 0),
      averageGC: history.length > 0 
        ? (history.reduce((sum, h) => sum + (h.average_gc_content || 0), 0) / history.length).toFixed(2)
        : 0,
      analysisTypes: {}
    };

    history.forEach(item => {
      const type = item.analysis_type || 'unknown';
      stats.analysisTypes[type] = (stats.analysisTypes[type] || 0) + 1;
    });

    return stats;
  };

  const getPerformanceData = () => {
    // Group analyses by date
    const dateGroups = {};
    history.forEach(item => {
      const date = new Date(item.timestamp).toLocaleDateString();
      if (!dateGroups[date]) {
        dateGroups[date] = { date, count: 0, totalSeqs: 0 };
      }
      dateGroups[date].count += 1;
      dateGroups[date].totalSeqs += item.total_sequences || 0;
    });

    return Object.values(dateGroups).sort((a, b) => new Date(a.date) - new Date(b.date));
  };

  const getAnalysisTypeData = () => {
    const stats = calculateStatistics();
    return Object.entries(stats.analysisTypes).map(([type, count]) => ({
      name: type.replace('_', ' '),
      value: count
    }));
  };

  const COLORS = ['#667eea', '#764ba2', '#f093fb', '#4facfe', '#43e97b', '#fa709a', '#fee140', '#30cfd0'];

  const analysisGuides = [
    {
      name: 'Quality Control',
      description: 'Analyze GC content, sequence lengths, and quality metrics for overall data quality assessment.'
    },
    {
      name: 'Sequence Analysis',
      description: 'Calculate nucleotide composition and statistical summaries of your genomic sequences.'
    },
    {
      name: 'Quality Scores (FASTQ)',
      description: 'Examine phred quality scores per position and per sequence to identify low-quality regions.'
    },
    {
      name: 'Base Frequency',
      description: 'Visualize A, T, G, C distribution across sequence windows with heatmaps.'
    },
    {
      name: 'Open Reading Frames',
      description: 'Detect potential protein-coding regions by identifying start and stop codons.'
    },
    {
      name: 'Translation',
      description: 'Convert DNA sequences to protein sequences using the standard genetic code.'
    },
    {
      name: 'Dinucleotides',
      description: 'Analyze frequency patterns of 2-mer and 3-mer sequences for bias detection.'
    },
    {
      name: 'Repeat Detection',
      description: 'Find tandem and interspersed repetitive sequences in your genomic data.'
    },
    {
      name: 'Alignment',
      description: 'Perform pairwise and multiple sequence alignments to compare sequences.'
    }
  ];

  const workflows = [
    {
      name: 'Full Genomic Profile',
      description: 'Run quality control → sequence analysis → translation for comprehensive overview',
      steps: ['Quality Control', 'Sequence Analysis', 'DNA to Protein Translation']
    },
    {
      name: 'Quality Check Only',
      description: 'Quick assessment of data quality without detailed analysis',
      steps: ['Quality Control']
    },
    {
      name: 'Coding Region Discovery',
      description: 'Find and analyze potential protein-coding regions',
      steps: ['Open Reading Frames', 'DNA to Protein Translation']
    },
    {
      name: 'Sequence Comparison',
      description: 'Compare multiple sequences and identify differences',
      steps: ['Multiple Sequence Alignment', 'Dinucleotides']
    },
    {
      name: 'Complete Analysis Suite',
      description: 'Run all available analyses for comprehensive genomic profiling',
      steps: ['Quality Control', 'Base Frequency', 'ORFs', 'Translation', 'Dinucleotides', 'Repeats']
    }
  ];

  const faqItems = [
    {
      q: 'What is GC Content?',
      a: 'GC content is the percentage of guanine (G) and cytosine (C) bases in a DNA sequence. It affects melting temperature and is important for PCR primer design.'
    },
    {
      q: 'What are Open Reading Frames (ORFs)?',
      a: 'ORFs are stretches of DNA starting with a start codon (ATG) and ending with a stop codon (TAA, TAG, TGA). They represent potential protein-coding regions.'
    },
    {
      q: 'What do quality scores mean?',
      a: 'Phred quality scores (Q) represent the confidence in base calling. Q30 = 99.9% accuracy, Q20 = 99% accuracy. Higher is better.'
    },
    {
      q: 'What is a codon?',
      a: 'A codon is a sequence of 3 nucleotides that encodes a single amino acid. There are 64 possible codons, specifying 20 amino acids plus stop signals.'
    },
    {
      q: 'What are dinucleotides?',
      a: 'Dinucleotides are pairs of adjacent nucleotides (e.g., AT, GC). Their frequency can indicate evolutionary pressure or mutational bias.'
    },
    {
      q: 'How does sequence alignment work?',
      a: 'Alignment compares sequences to find similarities and differences. It matches bases/codons and identifies insertions, deletions, and substitutions.'
    },
    {
      q: 'What is FASTA format?',
      a: 'FASTA is a text format for biological sequences. It starts with ">" followed by a description, then the sequence on following lines.'
    },
    {
      q: 'What is FASTQ format?',
      a: 'FASTQ is like FASTA but includes quality scores for each base. Common in next-generation sequencing (NGS) data.'
    }
  ];

  return (
    <div className="app-container">
      <header className="header">
        <h1>Bioinformatics Analysis Suite</h1>
        <p>Computational Genomics Platform</p>
      </header>

      <div className="tabs">
        <button 
          className={`tab ${activeTab === 'guide' ? 'active' : ''}`}
          onClick={() => setActiveTab('guide')}
        >
          Analysis Guide
        </button>
        <button 
          className={`tab ${activeTab === 'upload' ? 'active' : ''}`}
          onClick={() => setActiveTab('upload')}
        >
          Upload & Analyze
        </button>
        <button 
          className={`tab ${activeTab === 'results' ? 'active' : ''}`}
          onClick={() => setActiveTab('results')}
        >
          Results Dashboard
        </button>
        <button 
          className={`tab ${activeTab === 'recent' ? 'active' : ''}`}
          onClick={() => { setActiveTab('recent'); loadHistory(); }}
        >
          Recent Analyses
        </button>
        <button 
          className={`tab ${activeTab === 'workflows' ? 'active' : ''}`}
          onClick={() => setActiveTab('workflows')}
        >
          Workflows
        </button>
        <button 
          className={`tab ${activeTab === 'overview' ? 'active' : ''}`}
          onClick={() => setActiveTab('overview')}
        >
          📊 Overview
        </button>
        <button 
          className={`tab ${activeTab === 'analytics' ? 'active' : ''}`}
          onClick={() => { setActiveTab('analytics'); loadHistory(); }}
        >
          Analytics
        </button>
        <button 
          className={`tab ${activeTab === 'help' ? 'active' : ''}`}
          onClick={() => setActiveTab('help')}
        >
          Help & FAQ
        </button>
        <button 
          className={`tab ${activeTab === 'contact' ? 'active' : ''}`}
          onClick={() => setActiveTab('contact')}
        >
          📧 Contact
        </button>
        <button 
          className={`tab ${activeTab === 'history' ? 'active' : ''}`}
          onClick={() => { setActiveTab('history'); loadHistory(); }}
        >
          History ({history.length})
        </button>
      </div>

      <main className="main-content">
        {/* Overview Tab - Statistics Only */}
        {activeTab === 'overview' && (
          <section className="overview-section">
            <h2>📊 Overview</h2>
            <div className="dashboard-stats">
              <div className="stat-card">
                <h4>Total Analyses</h4>
                <p className="stat-number">{calculateStatistics().totalAnalyses}</p>
              </div>
              <div className="stat-card">
                <h4>Sequences Processed</h4>
                <p className="stat-number">{calculateStatistics().totalSequences.toLocaleString()}</p>
              </div>
              <div className="stat-card">
                <h4>Average GC Content</h4>
                <p className="stat-number">{calculateStatistics().averageGC}%</p>
              </div>
              <div className="stat-card">
                <h4>Analysis Types Used</h4>
                <p className="stat-number">{Object.keys(calculateStatistics().analysisTypes).length}</p>
              </div>
            </div>
          </section>
        )}

        {/* Guide Tab - Quick Start & Analysis Guide */}
        {activeTab === 'guide' && (
          <section className="guide-section">
            <h2>🚀 Quick Start Guide</h2>
            <div className="quick-start">
              <div className="step">
                <div className="step-number">1</div>
                <div className="step-content">
                  <h4>Upload File</h4>
                  <p>Go to "Upload & Analyze" tab and select a FASTA or FASTQ file from your computer.</p>
                </div>
              </div>
              <div className="step">
                <div className="step-number">2</div>
                <div className="step-content">
                  <h4>Choose Analysis</h4>
                  <p>Select from basic analyses (Quality Control, Sequence Analysis) or advanced (ORFs, Translation, etc.)</p>
                </div>
              </div>
              <div className="step">
                <div className="step-number">3</div>
                <div className="step-content">
                  <h4>View Results</h4>
                  <p>Results appear in the "Results Dashboard" tab with interactive charts and exportable data (CSV, JSON, PDF).</p>
                </div>
              </div>
            </div>

            <h2 style={{ marginTop: '50px' }}>📖 Analysis Types Guide</h2>
            <div className="analysis-guide-grid">
              {analysisGuides.map((guide, idx) => (
                <div key={idx} className="guide-card">
                  <h5>{guide.name}</h5>
                  <p>{guide.description}</p>
                </div>
              ))}
            </div>
          </section>
        )}

        {/* Recent Analyses Tab */}
        {activeTab === 'recent' && (
          <section className="recent-section">
            <h2>📋 Recent Analyses</h2>
            {history.length === 0 ? (
              <p className="no-history">No analyses yet. Start by uploading a file!</p>
            ) : (
              <div className="recent-analyses-grid-large">
                {history.slice(0, 12).map((item) => (
                  <div key={item.id} className="recent-card-large">
                    <div className="recent-type">{item.analysis_type.replace('_', ' ')}</div>
                    <h5>{item.filename}</h5>
                    <div className="recent-details">
                      <p><strong>Sequences:</strong> {item.total_sequences}</p>
                      <p><strong>Length:</strong> {item.total_length?.toLocaleString() || 'N/A'} bp</p>
                      {item.average_gc_content && <p><strong>GC Content:</strong> {item.average_gc_content}%</p>}
                    </div>
                    <p className="recent-date">{new Date(item.timestamp).toLocaleString()}</p>
                    <button 
                      onClick={() => viewResultFromHistory(item.id)}
                      className="btn-view-small"
                    >
                      View Results
                    </button>
                  </div>
                ))}
              </div>
            )}
          </section>
        )}

        {/* Workflows Tab */}
        {activeTab === 'workflows' && (
          <section className="workflows-section">
            <h2>⚙️ Workflow Templates</h2>
            <p className="workflows-intro">Choose a pre-designed workflow or combine analyses to create your own pipeline:</p>
            <div className="workflows-grid-large">
              {workflows.map((workflow, idx) => (
                <div key={idx} className="workflow-card-large">
                  <h5>{workflow.name}</h5>
                  <p>{workflow.description}</p>
                  <div className="workflow-steps-large">
                    {workflow.steps.map((step, i) => (
                      <div key={i} className="workflow-step-item">
                        <span className="step-number-small">{i + 1}</span>
                        <span className="step-name">{step}</span>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </section>
        )}

        {/* Analytics Tab */}
        {activeTab === 'analytics' && (
          <section className="analytics-section">
            <h2>📈 Analytics & Performance</h2>
            {history.length === 0 ? (
              <p className="no-history">No data yet. Run some analyses to see trends!</p>
            ) : (
              <div className="charts-row-full">
                <div className="chart-full">
                  <h3>Analyses Over Time</h3>
                  <ResponsiveContainer width="100%" height={350}>
                    <LineChart data={getPerformanceData()}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="date" angle={-45} textAnchor="end" height={70} />
                      <YAxis />
                      <Tooltip />
                      <Legend />
                      <Line type="monotone" dataKey="count" stroke="#667eea" strokeWidth={2} name="Analyses" />
                      <Line type="monotone" dataKey="totalSeqs" stroke="#764ba2" strokeWidth={2} name="Sequences" />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
                <div className="chart-full">
                  <h3>Analysis Type Distribution</h3>
                  <ResponsiveContainer width="100%" height={350}>
                    <PieChart>
                      <Pie data={getAnalysisTypeData()} cx="50%" cy="50%" labelLine={false} label>
                        {getAnalysisTypeData().map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                        ))}
                      </Pie>
                      <Tooltip />
                      <Legend />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
              </div>
            )}
          </section>
        )}

        {/* Help & FAQ Tab */}
        {activeTab === 'help' && (
          <section className="help-section">
            <h2>❓ Help & FAQ</h2>
            <p className="faq-intro">Find answers to common questions about bioinformatics and this platform:</p>
            <div className="faq-list-full">
              {faqItems.map((item, idx) => (
                <details key={idx} className="faq-item-large">
                  <summary>{item.q}</summary>
                  <p>{item.a}</p>
                </details>
              ))}
            </div>
          </section>
        )}

        {/* Upload Tab */}
        {activeTab === 'upload' && (
          <section className="upload-section">
            <h2>Upload and Analyze Genomic Data</h2>
            
            <form onSubmit={handleSubmit} className="form">
              <div className="form-group">
                <label htmlFor="file">Select FASTA/FASTQ file:</label>
                <input
                  id="file"
                  type="file"
                  onChange={handleFileChange}
                  accept=".fasta,.fastq,.fa,.fq"
                />
              </div>

              <div className="form-group">
                <label htmlFor="analysis">Analysis Type:</label>
                <select 
                  id="analysis"
                  value={analysisType}
                  onChange={(e) => setAnalysisType(e.target.value)}
                >
                  <optgroup label="Basic Analyses">
                    <option value="quality_control">Quality Control</option>
                    <option value="sequence">Sequence Analysis</option>
                  </optgroup>
                  <optgroup label="Advanced Analyses">
                    <option value="quality_scores">Quality Scores (FASTQ)</option>
                    <option value="base_frequency">Base Frequency Heatmap</option>
                    <option value="orfs">Open Reading Frames</option>
                    <option value="translation">DNA to Protein Translation</option>
                    <option value="dinucleotides">Dinucleotide Analysis</option>
                    <option value="repeats">Repeat Detection</option>
                    <option value="alignment">Multiple Sequence Alignment</option>
                  </optgroup>
                </select>
              </div>

              <div className="button-group">
                <button 
                  type="button"
                  onClick={handlePreview}
                  disabled={!file || previewLoading}
                  className="btn-secondary"
                >
                  {previewLoading ? 'Previewing...' : 'Preview File'}
                </button>
                <button type="submit" disabled={loading || !file} className="btn-submit">
                  {loading ? 'Analyzing...' : 'Run Analysis'}
                </button>
              </div>
            </form>

            {error && <div className="error-message">{error}</div>}

            {/* File Preview */}
            {preview && (
              <section className="preview-section">
                <h3>File Preview</h3>
                <div className="preview-info">
                  <p><strong>File:</strong> {preview.filename}</p>
                  <p><strong>Sequences found:</strong> {preview.total_found}</p>
                </div>
                <div className="sequences-list">
                  {preview.sequences.map((seq, idx) => (
                    <div key={idx} className="sequence-item">
                      <strong>{seq.id}</strong>
                      <p>Length: {seq.length} bp</p>
                      <code>{seq.preview}</code>
                    </div>
                  ))}
                </div>
              </section>
            )}
          </section>
        )}

        {/* Results Dashboard Tab */}
        {activeTab === 'results' && results && (
          <section className="results-section">
            <h2>Analysis Results Dashboard</h2>
            
            {/* Analysis Sub-tabs */}
            {(results.analysis_type === 'base_frequency' || results.analysis_type === 'orfs' || 
              results.analysis_type === 'translation' || results.analysis_type === 'dinucleotides' ||
              results.analysis_type === 'repeats' || results.analysis_type === 'alignment' ||
              results.analysis_type === 'quality_scores') && (
              <div className="analysis-tabs">
                <button 
                  className={`tab ${activeAnalysisTab === 'overview' ? 'active' : ''}`}
                  onClick={() => setActiveAnalysisTab('overview')}
                >
                  Overview
                </button>
                <button 
                  className={`tab ${activeAnalysisTab === 'details' ? 'active' : ''}`}
                  onClick={() => setActiveAnalysisTab('details')}
                >
                  Details
                </button>
              </div>
            )}
            
            {/* Summary Cards - only for basic analyses */}
            {!['base_frequency', 'orfs', 'translation', 'dinucleotides', 'repeats', 'alignment', 'quality_scores'].includes(results.analysis_type) && results.summary && (
              <div className="summary-cards">
                <div className="card">
                  <h4>Total Sequences</h4>
                  <p className="card-value">{results.summary.total_sequences}</p>
                  <p className="card-description">Total number of DNA/protein sequences in your file</p>
                </div>
                <div className="card">
                  <h4>Total Length</h4>
                  <p className="card-value">{results.summary.total_length?.toLocaleString() || 'N/A'} bp</p>
                  <p className="card-description">Combined length of all sequences (base pairs)</p>
                </div>
                {results.summary.average_length && (
                  <div className="card">
                    <h4>Average Length</h4>
                    <p className="card-value">{results.summary.average_length} bp</p>
                    <p className="card-description">Mean length per sequence - indicates sequence size consistency</p>
                  </div>
                )}
                {results.summary.average_gc_content !== undefined && (
                  <div className="card">
                    <h4>Average GC Content</h4>
                    <p className="card-value">{results.summary.average_gc_content}%</p>
                    <p className="card-description">Percentage of G and C nucleotides - affects DNA properties</p>
                  </div>
                )}
              </div>
            )}

            {/* Charts - Overview Tab */}
            {activeAnalysisTab === 'overview' && (
              <div className="charts-section">
                {renderGCContentChart()}
                {renderNucleotideChart()}
                {renderSequenceLengthChart()}
                {renderBaseFrequencyHeatmap()}
                {renderORFsAnalysis()}
                {renderTranslation()}
                {renderDinucleotides()}
                {renderRepeats()}
                {renderAlignment()}
              </div>
            )}

            {/* Export Buttons */}
            {(results.analysis_type === 'quality_control' || results.analysis_type === 'sequence_analysis') && (
              <div className="export-section">
                <h4>Export Results</h4>
                <div className="export-buttons">
                  <button onClick={() => handleExport(results.id, 'csv')} className="btn-export">
                    Download CSV
                  </button>
                  <button onClick={() => handleExport(results.id, 'json')} className="btn-export">
                    Download JSON
                  </button>
                  <button onClick={() => handleExport(results.id, 'pdf')} className="btn-export">
                    Download PDF
                  </button>
                </div>
              </div>
            )}

            {/* Detailed Results */}
            {activeAnalysisTab === 'details' && (
              <div className="detailed-results">
                <h3>Detailed Analysis Data</h3>
                
                {/* Analysis Type Explanations */}
                {results.analysis_type === 'dinucleotides' && (
                  <div className="analysis-explanation">
                    <h4>📊 Dinucleotide Analysis</h4>
                    <p><strong>What are dinucleotides?</strong> Dinucleotides are pairs of adjacent nucleotides (e.g., AT, GC, TT, AA). Analyzing their frequency reveals patterns in DNA sequences that can indicate evolutionary pressure, codon bias, or mutational patterns.</p>
                    <p><strong>Key data:</strong></p>
                    <ul>
                      <li><strong>sequences:</strong> Individual sequence analysis with dinucleotide counts for each</li>
                      <li><strong>global_dinucleotides:</strong> Total counts of all dinucleotide pairs across all sequences</li>
                      <li><strong>total_pairs:</strong> Total number of dinucleotide pairs analyzed</li>
                    </ul>
                  </div>
                )}
                
                {results.analysis_type === 'base_frequency' && (
                  <div className="analysis-explanation">
                    <h4>📊 Base Frequency Analysis</h4>
                    <p><strong>What is it?</strong> Analyzes the frequency of each nucleotide base (A, T, G, C, N) across your sequences.</p>
                    <p><strong>Key data:</strong></p>
                    <ul>
                      <li><strong>A/T/G/C counts:</strong> Number of each base type</li>
                      <li><strong>Percentages:</strong> Proportion of each base relative to total</li>
                      <li><strong>N count:</strong> Unknown/ambiguous nucleotides</li>
                    </ul>
                  </div>
                )}
                
                {results.analysis_type === 'repeats' && (
                  <div className="analysis-explanation">
                    <h4>📊 Repeat Sequences Analysis</h4>
                    <p><strong>What is it?</strong> Identifies and analyzes repetitive DNA elements like tandem repeats, microsatellites, and other repeated motifs.</p>
                    <p><strong>Key data:</strong></p>
                    <ul>
                      <li><strong>unit:</strong> The repeating DNA sequence motif</li>
                      <li><strong>repeat_count:</strong> How many times the unit repeats</li>
                      <li><strong>total_length:</strong> Total length of the repeat region in base pairs</li>
                    </ul>
                  </div>
                )}
                
                {results.analysis_type === 'orfs' && (
                  <div className="analysis-explanation">
                    <h4>📊 Open Reading Frames (ORFs) Analysis</h4>
                    <p><strong>What are ORFs?</strong> Open Reading Frames are sequences between start and stop codons that could potentially code for proteins.</p>
                    <p><strong>Key data:</strong></p>
                    <ul>
                      <li><strong>start_pos:</strong> Position where the ORF begins</li>
                      <li><strong>end_pos:</strong> Position where the ORF ends</li>
                      <li><strong>frame:</strong> Reading frame (0, 1, or 2)</li>
                      <li><strong>length:</strong> Length of the ORF in base pairs</li>
                    </ul>
                  </div>
                )}
                
                {results.analysis_type === 'translation' && (
                  <div className="analysis-explanation">
                    <h4>📊 Translation Analysis</h4>
                    <p><strong>What is it?</strong> Converts DNA sequences into protein sequences using the genetic code. Shows the amino acid sequence that would be produced.</p>
                    <p><strong>Key data:</strong></p>
                    <ul>
                      <li><strong>protein_sequence:</strong> Amino acids translated from DNA</li>
                      <li><strong>length:</strong> Number of amino acids</li>
                      <li><strong>frame:</strong> Which reading frame was used</li>
                    </ul>
                  </div>
                )}
                
                {results.analysis_type === 'alignment' && (
                  <div className="analysis-explanation">
                    <h4>📊 Sequence Alignment</h4>
                    <p><strong>What is it?</strong> Compares multiple sequences to find similarities, differences, and conserved regions. Useful for understanding evolutionary relationships.</p>
                    <p><strong>Key data:</strong></p>
                    <ul>
                      <li><strong>aligned_sequences:</strong> Sequences arranged for comparison</li>
                      <li><strong>identity:</strong> Percentage of matching positions</li>
                      <li><strong>gaps:</strong> Insertions/deletions between sequences</li>
                    </ul>
                  </div>
                )}
              </div>
            )}
          </section>
        )}

        {/* Contact Tab */}
        {activeTab === 'contact' && (
          <section className="contact-section">
            <h2>📧 Contact Information</h2>
            
            <div className="contact-container">
              {/* Mentor/Guide Section */}
              <div className="contact-group">
                <h3>👨‍🏫 Mentor / Guide</h3>
                <div className="contact-card mentor-card">
                  <h4>Dr. A H Manjunatha Reddy</h4>
                  <p><strong>Title:</strong> Professor</p>
                  <p><strong>Department:</strong> Department of Biotechnology</p>
                  <p><strong>Organization:</strong> R V College of Engineering</p>
                  <p><strong>Center:</strong> Center of Excellence in Computational Genomics</p>
                  <p><strong>Phone:</strong> <a href="tel:+919844573697">+91 9844573697</a></p>
                  <p><strong>Email:</strong> <a href="mailto:ahmanjunathareddy@rvce.edu.in">ahmanjunathareddy@rvce.edu.in</a></p>
                </div>
              </div>

              {/* Team Members Section */}
              <div className="contact-group">
                <h3>👥 Project Team</h3>
                
                <div className="contact-card">
                  <h4>Greeshma S</h4>
                  <p><strong>Department:</strong> Department of Computer Science and Engineering</p>
                  <p><strong>Organization:</strong> R V College of Engineering</p>
                  <p><strong>Email:</strong> <a href="mailto:greeshmas.cs23@rvce.edu.in">greeshmas.cs23@rvce.edu.in</a></p>
                </div>

                <div className="contact-card">
                  <h4>Bhuvan V Sirigeri</h4>
                  <p><strong>Department:</strong> Department of Civil Engineering</p>
                  <p><strong>Organization:</strong> R V College of Engineering</p>
                  <p><strong>Email:</strong> <a href="mailto:bhuvanvsirigeri.cv23@rvce.edu.in">bhuvanvsirigeri.cv23@rvce.edu.in</a></p>
                </div>

                <div className="contact-card">
                  <h4>Dhanush Gowda C</h4>
                  <p><strong>Department:</strong> Department of Civil Engineering</p>
                  <p><strong>Organization:</strong> R V College of Engineering</p>
                  <p><strong>Email:</strong> <a href="mailto:dhanushgowdac.cv23@rvce.edu.in">dhanushgowdac.cv23@rvce.edu.in</a></p>
                </div>
              </div>
            </div>
          </section>
        )}

        {/* History Tab */}
        {activeTab === 'history' && (
          <section className="history-section">
            <h2>Analysis History</h2>
            {history.length === 0 ? (
              <p className="no-history">No analyses yet. Start by uploading a file!</p>
            ) : (
              <div className="history-list">
                {history.map((item) => (
                  <div key={item.id} className="history-item">
                    <div className="history-info">
                      <h4>{item.filename}</h4>
                      <p><strong>Type:</strong> {item.analysis_type.replace('_', ' ')}</p>
                      <p><strong>Date:</strong> {new Date(item.timestamp).toLocaleString()}</p>
                      <p><strong>Sequences:</strong> {item.total_sequences}</p>
                    </div>
                    <button 
                      onClick={() => viewResultFromHistory(item.id)}
                      className="btn-view"
                    >
                      View Results
                    </button>
                  </div>
                ))}
              </div>
            )}
          </section>
        )}
      </main>

      {/* Chatbot Component */}
      <Chatbot analysisContext={results} />
    </div>
  );
}

export default App;

