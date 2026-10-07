import React, { useState, useEffect, useMemo, useRef } from 'react';
import { 
  ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer,
  BarChart, Bar, PieChart, Pie, Cell, Legend
} from 'recharts';
import { 
  LayoutDashboard, Database, Bot, Search, Filter, Send, ChevronRight, 
  Menu, X, Loader2, Info
} from 'lucide-react';

// Helper to generate realistic but mock dataset
const generateDemoData = () => {
  const sources = ['Reddit', 'App Store Review', 'Google Play', 'Google Photos Community', 'Twitter', 'User Interview'];
  const baseProblems = [
    'Forgotten date', 
    'Keyword mismatch', 
    'Too many similar photos', 
    'Cannot remember location',
    'Cannot remember filename',
    'Event name ambiguous'
  ];
  const possibleCues = ['People', 'Place', 'Event', 'Emotion', 'Weather', 'Time of Year', 'Object', 'Clothing'];
  const possibleForgotten = ['Exact Date', 'Filename', 'Exact Location', 'Search Keywords', 'Names'];
  const searchBehaviors = ['Exact', 'Approximate', 'Descriptive', 'Emotion-based', 'Visual', 'Event-based'];
  const segments = ['The Exact Searcher', 'The Story Searcher', 'The Contextual Searcher', 'The Emotion Searcher'];
  
  const templates = [
    "I was trying to find a picture from a [EVENT]. I remember feeling [EMOTION] and it was [WEATHER], but I couldn't remember the [FORGOTTEN]. Searching for it was a nightmare.",
    "Why can't I just search by [CUE]? I have thousands of photos and trying to guess the [FORGOTTEN] is impossible.",
    "I know I took a photo of [CUE] at the [CUE], but because I don't know the [FORGOTTEN], it's lost in my camera roll forever.",
    "Searching by [FORGOTTEN] is useless when you have 10 years of photos. I just want to find that [EMOTION] memory from the [EVENT].",
    "It's so frustrating. I searched '[SEARCH_TERM]' but because the AI didn't tag it exactly like that, it failed. I just remember the [CUE].",
    "I'm looking for a photo with my friend. I remember the [CUE] and it was a [EMOTION] day, but I have no idea about the [FORGOTTEN].",
    "My memory is so vague. I know the [EVENT] happened roughly in summer, but finding it without the [FORGOTTEN] took me 30 minutes of scrolling.",
    "I wish the search understood context better. I typed a [SEARCH_BEHAVIOR] query and it completely misunderstood what I wanted."
  ];

  const randomItem = (arr) => arr[Math.floor(Math.random() * arr.length)];
  const randomItems = (arr, max) => {
    const count = Math.floor(Math.random() * max) + 1;
    const shuffled = [...arr].sort(() => 0.5 - Math.random());
    return shuffled.slice(0, count);
  };

  const data = [];
  for (let i = 1; i <= 100; i++) {
    const cue1 = randomItem(possibleCues);
    const cue2 = randomItem(possibleCues);
    const forgotten = randomItem(possibleForgotten);
    const event = randomItem(['birthday', 'college trip', 'wedding', 'vacation', 'concert']);
    const emotion = randomItem(['happy', 'nostalgic', 'excited', 'relaxed']);
    const weather = randomItem(['sunny', 'raining', 'snowing']);
    const behavior = randomItem(searchBehaviors);
    
    let text = randomItem(templates)
      .replace(/\[EVENT\]/g, event)
      .replace(/\[EMOTION\]/g, emotion)
      .replace(/\[WEATHER\]/g, weather)
      .replace(/\[CUE\]/g, cue1.toLowerCase())
      .replace(/\[CUE\]/g, cue2.toLowerCase())
      .replace(/\[FORGOTTEN\]/g, forgotten.toLowerCase())
      .replace(/\[SEARCH_TERM\]/g, `my ${event}`)
      .replace(/\[SEARCH_BEHAVIOR\]/g, behavior.toLowerCase());

    data.push({
      id: `EV-${1000 + i}`,
      source: randomItem(sources),
      text: text,
      retrieval_problem: randomItem(baseProblems),
      memory_cues: randomItems(possibleCues, 3),
      forgotten_info: [forgotten, ...randomItems(possibleForgotten, 1).filter(f => f !== forgotten)],
      search_behavior: behavior,
      segment: randomItem(segments),
      intensity: Math.floor(Math.random() * 5) + 6, // 6 to 10
      date: new Date(Date.now() - Math.floor(Math.random() * 10000000000)).toISOString().split('T')[0]
    });
  }
  return data;
};

// Markdown parser for AI responses
const MarkdownRenderer = ({ content }) => {
  const createMarkup = (text) => {
    let html = text
      // Headers
      .replace(/^### (.*$)/gim, '<h3 class="text-lg font-semibold text-slate-800 mt-6 mb-2 border-b pb-1">$1</h3>')
      .replace(/^## (.*$)/gim, '<h2 class="text-xl font-bold text-indigo-700 mt-8 mb-3 border-b border-indigo-100 pb-2">$1</h2>')
      .replace(/^# (.*$)/gim, '<h1 class="text-2xl font-bold text-slate-900 mt-8 mb-4">$1</h1>')
      // Bold & Italic
      .replace(/\*\*(.*?)\*\*/gim, '<strong class="font-bold text-slate-900">$1</strong>')
      .replace(/\*(.*?)\*/gim, '<em class="italic text-slate-700">$1</em>')
      // Lists
      .replace(/^\* (.*$)/gim, '<li class="ml-4 list-disc mb-1">$1</li>')
      .replace(/^- (.*$)/gim, '<li class="ml-4 list-disc mb-1">$1</li>')
      // Newlines
      .replace(/\n(?!\<li\>)/gim, '<br />')
      // Clean up standalone brs after block elements
      .replace(/<\/h2><br \/>/gim, '</h2>')
      .replace(/<\/h3><br \/>/gim, '</h3>');
    return { __html: html };
  };

  return (
    <div 
      className="prose prose-sm max-w-none text-slate-600 leading-relaxed"
      dangerouslySetInnerHTML={createMarkup(content)} 
    />
  );
};

const COLORS = ['#6366f1', '#8b5cf6', '#ec4899', '#f43f5e', '#f97316', '#eab308', '#22c55e', '#06b6d4'];

export default function PhotoRetrievalEngine() {
  // State
  const [activeTab, setActiveTab] = useState('dashboard');
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [dataset, setDataset] = useState([]);
  const [loading, setLoading] = useState(true);

  // Initialize Data
  useEffect(() => {
    // Simulate loading time for data generation
    setTimeout(() => {
      setDataset(generateDemoData());
      setLoading(false);
    }, 800);
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen w-screen bg-slate-50 text-indigo-600">
        <div className="flex flex-col items-center gap-4">
          <Loader2 className="w-12 h-12 animate-spin" />
          <h2 className="text-xl font-semibold">Initializing Discovery Engine...</h2>
          <p className="text-sm text-slate-500">Generating demo research data</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex h-screen w-full bg-slate-50 overflow-hidden font-sans text-slate-900">
      
      {/* Sidebar Navigation */}
      <aside className={`fixed inset-y-0 left-0 z-50 w-64 bg-slate-900 text-white transform transition-transform duration-300 ease-in-out ${isMobileMenuOpen ? 'translate-x-0' : '-translate-x-full'} md:relative md:translate-x-0 flex flex-col`}>
        <div className="p-6 border-b border-slate-800 flex justify-between items-center">
          <div>
            <h1 className="text-xl font-bold leading-tight">Photo Retrieval</h1>
            <p className="text-indigo-400 text-xs font-medium uppercase tracking-wider mt-1">Discovery Engine</p>
          </div>
          <button className="md:hidden text-slate-400 hover:text-white" onClick={() => setIsMobileMenuOpen(false)}>
            <X className="w-6 h-6" />
          </button>
        </div>
        
        <nav className="flex-1 px-4 py-6 space-y-2">
          {[
            { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
            { id: 'evidence', label: 'Evidence Explorer', icon: Database },
            { id: 'ai', label: 'AI Research Assistant', icon: Bot },
          ].map((item) => (
            <button
              key={item.id}
              onClick={() => { setActiveTab(item.id); setIsMobileMenuOpen(false); }}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-colors text-left ${
                activeTab === item.id 
                  ? 'bg-indigo-600 text-white shadow-md shadow-indigo-900/20' 
                  : 'text-slate-300 hover:bg-slate-800 hover:text-white'
              }`}
            >
              <item.icon className="w-5 h-5" />
              <span className="font-medium">{item.label}</span>
            </button>
          ))}
        </nav>
        
        <div className="p-4 m-4 bg-slate-800 rounded-xl text-xs text-slate-400 border border-slate-700">
          <p className="flex items-center gap-2 font-medium text-slate-300 mb-1">
            <Info className="w-4 h-4" /> Demo Mode
          </p>
          <p>Running on synthetic dataset ({dataset.length} records) for demonstration.</p>
        </div>
      </aside>

      {/* Main Content Area */}
      <main className="flex-1 flex flex-col h-full overflow-hidden relative">
        <header className="bg-white border-b border-slate-200 px-6 py-4 flex items-center justify-between shadow-sm z-10">
          <div className="flex items-center gap-4">
            <button className="md:hidden text-slate-600 p-1" onClick={() => setIsMobileMenuOpen(true)}>
              <Menu className="w-6 h-6" />
            </button>
            <h2 className="text-xl font-semibold text-slate-800 capitalize flex items-center gap-2">
              {activeTab === 'dashboard' && <LayoutDashboard className="w-5 h-5 text-indigo-500"/>}
              {activeTab === 'evidence' && <Database className="w-5 h-5 text-indigo-500"/>}
              {activeTab === 'ai' && <Bot className="w-5 h-5 text-indigo-500"/>}
              {activeTab.replace('-', ' ')}
            </h2>
          </div>
        </header>
        
        <div className="flex-1 overflow-y-auto p-4 md:p-8">
          {activeTab === 'dashboard' && <DashboardView dataset={dataset} />}
          {activeTab === 'evidence' && <EvidenceExplorer dataset={dataset} />}
          {activeTab === 'ai' && <AIResearchAssistant dataset={dataset} />}
        </div>
      </main>
    </div>
  );
}

function DashboardView({ dataset }) {
  // Aggregate Data for Charts
  const metrics = useMemo(() => {
    const problemsMap = {};
    const cuesMap = {};
    const forgottenMap = {};
    const behaviorMap = {};

    dataset.forEach(d => {
      // Problems
      if (!problemsMap[d.retrieval_problem]) {
        problemsMap[d.retrieval_problem] = { name: d.retrieval_problem, count: 0, totalIntensity: 0 };
      }
      problemsMap[d.retrieval_problem].count += 1;
      problemsMap[d.retrieval_problem].totalIntensity += d.intensity;

      // Cues
      d.memory_cues.forEach(cue => {
        cuesMap[cue] = (cuesMap[cue] || 0) + 1;
      });

      // Forgotten
      d.forgotten_info.forEach(info => {
        forgottenMap[info] = (forgottenMap[info] || 0) + 1;
      });

      // Behaviors
      behaviorMap[d.search_behavior] = (behaviorMap[d.search_behavior] || 0) + 1;
    });

    const opportunityMapData = Object.values(problemsMap).map(p => ({
      name: p.name,
      frequency: p.count,
      intensity: parseFloat((p.totalIntensity / p.count).toFixed(1)),
      volume: p.count * 10 // scale for bubble size
    }));

    const cuesData = Object.keys(cuesMap).map(k => ({ name: k, count: cuesMap[k] })).sort((a,b) => b.count - a.count).slice(0, 5);
    const forgottenData = Object.keys(forgottenMap).map(k => ({ name: k, count: forgottenMap[k] })).sort((a,b) => b.count - a.count).slice(0, 5);
    const behaviorData = Object.keys(behaviorMap).map(k => ({ name: k, value: behaviorMap[k] }));

    return { opportunityMapData, cuesData, forgottenData, behaviorData, total: dataset.length, topCue: cuesData[0]?.name };
  }, [dataset]);

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-sm flex items-center gap-4">
          <div className="p-3 bg-indigo-50 text-indigo-600 rounded-xl"><Database className="w-6 h-6"/></div>
          <div>
            <p className="text-sm font-medium text-slate-500">Total Evidence</p>
            <h3 className="text-2xl font-bold text-slate-800">{metrics.total}</h3>
          </div>
        </div>
        <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-sm flex items-center gap-4">
          <div className="p-3 bg-rose-50 text-rose-600 rounded-xl"><Search className="w-6 h-6"/></div>
          <div>
            <p className="text-sm font-medium text-slate-500">Retrieval Problems</p>
            <h3 className="text-2xl font-bold text-slate-800">{metrics.opportunityMapData.length}</h3>
          </div>
        </div>
        <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-sm flex items-center gap-4">
          <div className="p-3 bg-emerald-50 text-emerald-600 rounded-xl"><Bot className="w-6 h-6"/></div>
          <div>
            <p className="text-sm font-medium text-slate-500">Top Memory Cue</p>
            <h3 className="text-2xl font-bold text-slate-800">{metrics.topCue}</h3>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Opportunity Map */}
        <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-sm lg:col-span-2">
          <div className="mb-4">
            <h3 className="text-lg font-bold text-slate-800">Retrieval Problem Landscape (Opportunity Map)</h3>
            <p className="text-sm text-slate-500">Frequency (X) vs Average Intensity (Y). Larger bubbles indicate higher evidence volume.</p>
          </div>
          <div className="h-80 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis type="number" dataKey="frequency" name="Frequency" unit=" records" stroke="#64748b" />
                <YAxis type="number" dataKey="intensity" name="Intensity" domain={[0, 10]} stroke="#64748b" />
                <RechartsTooltip cursor={{ strokeDasharray: '3 3' }} 
                  content={({ active, payload }) => {
                    if (active && payload && payload.length) {
                      const data = payload[0].payload;
                      return (
                        <div className="bg-slate-900 text-white p-3 rounded-lg shadow-xl text-sm">
                          <p className="font-bold mb-1">{data.name}</p>
                          <p>Frequency: {data.frequency}</p>
                          <p>Intensity: {data.intensity} / 10</p>
                        </div>
                      );
                    }
                    return null;
                  }}
                />
                <Scatter name="Problems" data={metrics.opportunityMapData} fill="#6366f1">
                  {metrics.opportunityMapData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Scatter>
              </ScatterChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Remembered vs Forgotten */}
        <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-sm">
          <h3 className="text-lg font-bold text-slate-800 mb-1">What Users Remember</h3>
          <p className="text-sm text-slate-500 mb-4">Top memory cues mentioned in feedback</p>
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={metrics.cuesData} layout="vertical" margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#e2e8f0"/>
                <XAxis type="number" stroke="#64748b"/>
                <YAxis dataKey="name" type="category" width={100} stroke="#475569" tick={{fontSize: 12}}/>
                <RechartsTooltip cursor={{fill: '#f1f5f9'}} />
                <Bar dataKey="count" fill="#3b82f6" radius={[0, 4, 4, 0]} barSize={24} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-sm">
          <h3 className="text-lg font-bold text-slate-800 mb-1">What Users Forget</h3>
          <p className="text-sm text-slate-500 mb-4">Missing metadata causing retrieval failure</p>
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={metrics.forgottenData} layout="vertical" margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#e2e8f0"/>
                <XAxis type="number" stroke="#64748b"/>
                <YAxis dataKey="name" type="category" width={100} stroke="#475569" tick={{fontSize: 12}}/>
                <RechartsTooltip cursor={{fill: '#f1f5f9'}} />
                <Bar dataKey="count" fill="#f43f5e" radius={[0, 4, 4, 0]} barSize={24} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Search Behavior Pie */}
        <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-sm lg:col-span-2 flex flex-col md:flex-row items-center">
          <div className="md:w-1/3 mb-4 md:mb-0">
             <h3 className="text-lg font-bold text-slate-800 mb-2">Search Behavior Breakdown</h3>
             <p className="text-sm text-slate-600">How users attempt to find photos when their memory is incomplete.</p>
          </div>
          <div className="h-64 w-full md:w-2/3">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={metrics.behaviorData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={90}
                  paddingAngle={5}
                  dataKey="value"
                >
                  {metrics.behaviorData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <RechartsTooltip />
                <Legend verticalAlign="middle" align="right" layout="vertical" iconType="circle"/>
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

      </div>
    </div>
  );
}

function EvidenceExplorer({ dataset }) {
  const [searchTerm, setSearchTerm] = useState('');
  const [filterProblem, setFilterProblem] = useState('All');
  
  const problems = ['All', ...new Set(dataset.map(d => d.retrieval_problem))];

  const filteredData = dataset.filter(d => {
    const matchesSearch = d.text.toLowerCase().includes(searchTerm.toLowerCase()) || 
                          d.memory_cues.some(c => c.toLowerCase().includes(searchTerm.toLowerCase()));
    const matchesProblem = filterProblem === 'All' || d.retrieval_problem === filterProblem;
    return matchesSearch && matchesProblem;
  });

  return (
    <div className="max-w-7xl mx-auto h-full flex flex-col">
      <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm mb-6 flex flex-col md:flex-row gap-4 items-center justify-between">
        <div className="relative w-full md:w-96">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 w-5 h-5" />
          <input 
            type="text" 
            placeholder="Search feedback or cues..."
            className="w-full pl-10 pr-4 py-2 border border-slate-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent text-sm"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
        <div className="flex items-center gap-2 w-full md:w-auto">
          <Filter className="text-slate-400 w-5 h-5" />
          <select 
            className="w-full md:w-auto py-2 px-3 border border-slate-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 text-sm bg-white"
            value={filterProblem}
            onChange={(e) => setFilterProblem(e.target.value)}
          >
            {problems.map(p => <option key={p} value={p}>{p}</option>)}
          </select>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 pb-8">
          {filteredData.map(item => (
            <div key={item.id} className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm hover:shadow-md transition-shadow flex flex-col">
              <div className="flex justify-between items-start mb-3">
                <span className="text-xs font-bold text-indigo-600 bg-indigo-50 px-2 py-1 rounded-md">{item.source}</span>
                <span className="text-xs text-slate-400">{item.date}</span>
              </div>
              <p className="text-sm text-slate-800 italic mb-4 flex-1">"{item.text}"</p>
              
              <div className="space-y-3 mt-auto pt-4 border-t border-slate-100">
                <div>
                  <p className="text-[10px] uppercase font-bold text-slate-400 mb-1 tracking-wider">Problem</p>
                  <p className="text-sm font-medium text-slate-700">{item.retrieval_problem}</p>
                </div>
                <div className="grid grid-cols-2 gap-2">
                  <div>
                     <p className="text-[10px] uppercase font-bold text-slate-400 mb-1 tracking-wider">Remembered</p>
                     <div className="flex flex-wrap gap-1">
                       {item.memory_cues.slice(0,2).map(cue => (
                         <span key={cue} className="text-[11px] bg-emerald-50 text-emerald-700 px-1.5 py-0.5 rounded">{cue}</span>
                       ))}
                     </div>
                  </div>
                  <div>
                     <p className="text-[10px] uppercase font-bold text-slate-400 mb-1 tracking-wider">Forgotten</p>
                     <div className="flex flex-wrap gap-1">
                       {item.forgotten_info.slice(0,2).map(info => (
                         <span key={info} className="text-[11px] bg-rose-50 text-rose-700 px-1.5 py-0.5 rounded">{info}</span>
                       ))}
                     </div>
                  </div>
                </div>
              </div>
            </div>
          ))}
          {filteredData.length === 0 && (
            <div className="col-span-full py-12 text-center text-slate-500">
              No evidence matches your filters.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function AIResearchAssistant({ dataset }) {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: "Hi, I'm your AI Research Assistant. I've analyzed the current dataset of user feedback regarding photo retrieval. Ask me anything, for example:\n\n* *What kinds of old photos do users struggle to retrieve?*\n* *What do users remember when they forget the date?*\n* *Which retrieval problems have the highest intensity?*"
    }
  ]);
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim()) return;
    
    const userMessage = { role: 'user', content: input };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsTyping(true);

    try {
      // Create a compressed version of dataset to fit in prompt easily, though 100 items is small enough
      const dataSummary = dataset.map(d => ({
        text: d.text,
        problem: d.retrieval_problem,
        cues: d.memory_cues,
        forgotten: d.forgotten_info,
        intensity: d.intensity
      }));

      const systemInstruction = `You are a Senior UX Researcher and AI Assistant for the 'Photo Retrieval Discovery Engine'.
Analyze the following dataset of user feedback regarding photo retrieval:
${JSON.stringify(dataSummary)}

Respond to the user's question based STRICTLY and ONLY on this provided dataset. Do not invent external data.
Format your response comprehensively using the following exact Markdown headers:
## Answer
(Direct concise answer)
## Key Findings
(3-5 bullet points)
## Evidence
(Quote directly from the dataset, citing the problem or context)
## Affected Users
(Describe the behavioral segment affected based on the data)
## Opportunity
(What product opportunity emerges from this?)
## Confidence
(High/Medium/Low and why based on dataset size/consistency)
`;

      const payload = {
        contents: [{ parts: [{ text: userMessage.content }] }],
        systemInstruction: { parts: [{ text: systemInstruction }] },
      };

      const apiKey = ""; // Canvas handles this automatically when empty
      const apiUrl = `https://generativelanguage.googleapis.com/v1beta/models/gemini-3-flash-preview:generateContent?key=${apiKey}`;

      const response = await fetch(apiUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      const result = await response.json();
      
      if (result.candidates && result.candidates[0].content?.parts?.[0]?.text) {
        const text = result.candidates[0].content.parts[0].text;
        setMessages(prev => [...prev, { role: 'assistant', content: text }]);
      } else {
         setMessages(prev => [...prev, { role: 'assistant', content: "I'm sorry, I couldn't generate a response based on the current data." }]);
      }
    } catch (error) {
      console.error("AI API Error:", error);
      setMessages(prev => [...prev, { role: 'assistant', content: "An error occurred while connecting to the AI service. Please try again." }]);
    } finally {
      setIsTyping(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="max-w-4xl mx-auto h-[calc(100vh-120px)] flex flex-col bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
      
      {/* Chat Area */}
      <div className="flex-1 overflow-y-auto p-6 space-y-6 bg-slate-50">
        {messages.map((msg, idx) => (
          <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[85%] rounded-2xl p-5 ${
              msg.role === 'user' 
                ? 'bg-indigo-600 text-white rounded-br-sm shadow-md' 
                : 'bg-white border border-slate-200 shadow-sm rounded-bl-sm'
            }`}>
              {msg.role === 'user' ? (
                <p className="whitespace-pre-wrap">{msg.content}</p>
              ) : (
                <MarkdownRenderer content={msg.content} />
              )}
            </div>
          </div>
        ))}
        {isTyping && (
          <div className="flex justify-start">
            <div className="bg-white border border-slate-200 shadow-sm rounded-2xl rounded-bl-sm p-4 flex gap-2">
              <div className="w-2 h-2 bg-indigo-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
              <div className="w-2 h-2 bg-indigo-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
              <div className="w-2 h-2 bg-indigo-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="p-4 bg-white border-t border-slate-200">
        <div className="flex gap-4 items-end max-w-4xl mx-auto relative">
          <textarea
            className="w-full resize-none rounded-xl border border-slate-300 p-4 pr-14 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent min-h-[60px] max-h-32 text-slate-800 text-sm shadow-sm"
            placeholder="Ask about photo retrieval behavior, e.g., 'What happens when users don't remember any exact keywords?'"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            rows={1}
          />
          <button
            onClick={handleSend}
            disabled={!input.trim() || isTyping}
            className="absolute right-2 bottom-2 p-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            <Send className="w-5 h-5" />
          </button>
        </div>
      </div>
    </div>
  );
}