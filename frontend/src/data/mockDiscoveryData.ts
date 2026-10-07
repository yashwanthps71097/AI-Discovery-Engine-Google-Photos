// Complete Mock and Fallback Dataset grounded in SQLite seed records & research design

export const SUMMARY_METRICS = {
  totalConvos: "24,592",
  platforms: 5,
  dateRange: "Jan 2022 - Aug 2026",
  failureRate: "42.8%",
  epistemicAuditRate: "100%",
  activeClusters: 4,
  opportunityAreas: 4
};

export const PLATFORM_DATA = [
  { name: 'Reddit (r/googlephotos)', value: 45, count: 11066, color: '#6366f1' },
  { name: 'Google Help Community', value: 25, count: 6148, color: '#14b8a6' },
  { name: 'Play Store Reviews', value: 15, count: 3688, color: '#f59e0b' },
  { name: 'Apple App Store', value: 10, count: 2459, color: '#ec4899' },
  { name: 'YouTube Comments', value: 5, count: 1231, color: '#8b5cf6' },
];

export const TIMELINE_DATA = [
  { date: '2023 Q1', ingestion: 2400, failure_spike: 38 },
  { date: '2023 Q2', ingestion: 3100, failure_spike: 41 },
  { date: '2023 Q3', ingestion: 2800, failure_spike: 39 },
  { date: '2023 Q4', ingestion: 4500, failure_spike: 46 },
  { date: '2024 Q1', ingestion: 3800, failure_spike: 40 },
  { date: '2024 Q2', ingestion: 5200, failure_spike: 44 },
  { date: '2024 Q3', ingestion: 6100, failure_spike: 47 },
  { date: '2025 Q1', ingestion: 7200, failure_spike: 49 },
  { date: '2025 Q3', ingestion: 8400, failure_spike: 51 },
];

export const SCENARIO_DATA = [
  { category: 'Old Family', success: 38, abandoned: 45, highEffort: 17, total: 420 },
  { category: 'Documents & IDs', success: 65, abandoned: 15, highEffort: 20, total: 310 },
  { category: 'Travel & Vacations', success: 75, abandoned: 15, highEffort: 10, total: 540 },
  { category: 'Childhood Memories', success: 28, abandoned: 52, highEffort: 20, total: 290 },
  { category: 'Screenshots & Receipts', success: 48, abandoned: 32, highEffort: 20, total: 380 },
  { category: 'Food & Dining', success: 72, abandoned: 18, highEffort: 10, total: 190 },
  { category: 'Nature & Scenery', success: 60, abandoned: 28, highEffort: 12, total: 160 },
  { category: 'Milestones & Events', success: 55, abandoned: 30, highEffort: 15, total: 240 },
];

export const MEMORY_VS_SYSTEM_DATA = [
  { trait: 'Exact Year / Date', remembered: 15, indexed: 95, delta: -80 },
  { trait: 'Exact Geolocation / GPS', remembered: 22, indexed: 88, delta: -66 },
  { trait: 'People / Companions', remembered: 89, indexed: 72, delta: +17 },
  { trait: 'Emotional State / Mood', remembered: 84, indexed: 4, delta: +80 },
  { trait: 'Activity / Event Story', remembered: 81, indexed: 28, delta: +53 },
  { trait: 'Atmospheric / Setting', remembered: 76, indexed: 12, delta: +64 },
  { trait: 'Exact Camera Filename', remembered: 2, indexed: 100, delta: -98 },
];

export const SEARCH_TACTICS_DATA = [
  { tactic: 'Keyword Search (Single noun)', count: 48, successRate: 35 },
  { tactic: 'Date & Range Filter', count: 32, successRate: 28 },
  { tactic: 'Facial Tag / People Filter', count: 26, successRate: 62 },
  { tactic: 'Chronological Endless Scroll', count: 68, successRate: 18 },
  { tactic: 'Album / Folder Browsing', count: 22, successRate: 44 },
  { tactic: 'Search with Multi-Word Story', count: 19, successRate: 12 },
  { tactic: 'External App AirDrop / Messaging Ask', count: 29, successRate: 74 },
];

export const BEHAVIOR_FLOWS = [
  { from: 'Keyword Search', to: 'Chronological Scroll', count: 58, rate: '58% of failed queries' },
  { from: 'Chronological Scroll', to: 'Date Filter Guess', count: 42, rate: '42% transition' },
  { from: 'Date Filter Guess', to: 'External Messenger / Cloud Workaround', count: 34, rate: '34% workaround rate' },
  { from: 'External Workaround', to: 'Permanent Abandonment', count: 24, rate: '24% complete dropout' }
];

export const FUNNEL_DATA = [
  { stage: '1. Memory Recall', stageNum: 1, value: 100, dropoff: 0, count: 24592, description: 'User possesses episodic memory impressions (who, where, feelings)' },
  { stage: '2. Query Intent Formulation', stageNum: 2, value: 85, dropoff: 15, count: 20903, description: 'Translating human memory into machine-acceptable query concepts' },
  { stage: '3. Query Syntax & Input Gap', stageNum: 3, value: 58, dropoff: 27, count: 14263, isBottleneck: true, description: 'PRIMARY BOTTLENECK: Semantic mismatch with inverted index' },
  { stage: '4. Search Result Inspection', stageNum: 4, value: 49, dropoff: 9, count: 12050, description: 'Evaluating first screen of thumbnail matches' },
  { stage: '5. Visual Recognition in High Noise', stageNum: 5, value: 36, dropoff: 13, count: 8853, description: 'Scanning hundreds of similar photos, receipts, or bursts' },
  { stage: '6. Query Refinement & Triage', stageNum: 6, value: 28, dropoff: 8, count: 6885, description: 'Attempting secondary keywords or date constraints' },
  { stage: '7. Final Photo Retrieval', stageNum: 7, value: 19, dropoff: 9, count: 4672, description: 'Locating original artifact and taking desired action' },
];

export const PROBLEM_CLUSTERS = [
  {
    id: 1,
    title: "Episodic Attribute vs Metadata Index Mismatch",
    frequency: "38.2%",
    severity: "High",
    memberCount: 9400,
    workaround: "Scrolling chronologically through 5,000 photos for 45 minutes",
    platforms: ["Reddit", "Google Help", "Play Store"],
    summary: "Users remember ambient states (cloudy, sunset, wooden cabin, red sweater), but retrieval engine prioritizes rigid object nouns or exact EXIF timestamps.",
    evidenceList: [
      {
        layer1: {
          quote: "I know we were at a beach, and my dog was there, and it was cloudy. I typed 'cloudy beach dog' and got nothing but sunny photos from California.",
          url: "https://reddit.com/r/googlephotos/comments/cloudy_beach_dog",
          date: "Oct 12, 2025",
          source: "Reddit"
        },
        layer2: {
          tags: ["Scenario: Travel / Vacation", "Failure: Query Formulation Gap", "Missing: Exact Date, Location"],
          interpretation: "Users anchor memories to ambient weather and relational co-presence, which visual classifiers under-weight relative to standard sunny daytime benchmarks."
        },
        layer3: {
          hypothesis: "Indexing atmospheric states and multi-concept episodic relations will increase natural query precision by at least 28% without requiring date filters."
        }
      },
      {
        layer1: {
          quote: "Trying to find the photo of my daughter wearing the yellow boots jumping into a muddy puddle in 2021. Search shows random boots from web purchases.",
          url: "https://support.google.com/photos/thread/884920",
          date: "Dec 04, 2025",
          source: "Google Help Community"
        },
        layer2: {
          tags: ["Scenario: Childhood photo", "Failure: Multi-concept composition", "Missing: Exact month"],
          interpretation: "Natural compound memory 'jumping into a muddy puddle' fails because action verbs are not recognized as temporal event anchors."
        },
        layer3: {
          hypothesis: "Dynamic activity-and-attire semantic embedding bridges the gap between childhood episodic memory and static object recognition."
        }
      }
    ]
  },
  {
    id: 2,
    title: "Document, Receipt & Functional Clutter Dilution",
    frequency: "26.5%",
    severity: "Medium",
    memberCount: 6510,
    workaround: "Manually building isolated albums and hiding photos",
    platforms: ["Play Store", "App Store"],
    summary: "Utility screenshots, medical records, and utility receipts crowd out emotional memories, causing timeline visual fatigue and search result clutter.",
    evidenceList: [
      {
        layer1: {
          quote: "My timeline is ruined by screenshots of receipts and utility bills. When I try to find a picture of my son's graduation, it's buried in tax documents.",
          url: "https://play.google.com/store/apps/details?id=com.google.android.apps.photos",
          date: "Nov 05, 2025",
          source: "Google Play Store"
        },
        layer2: {
          tags: ["Scenario: Milestone Event", "Failure: Timeline Clutter", "Missing: Auto-triage index"],
          interpretation: "Functional imagery breaks episodic browsing flow, diluting the visual salience of high-value emotional milestones."
        },
        layer3: {
          hypothesis: "A dedicated automatic 'Functional Vault' partitioned from episodic memories will eliminate 40% of visual noise during open-ended browsing."
        }
      }
    ]
  },
  {
    id: 3,
    title: "Chronological Timeline Scroll Exhaustion",
    frequency: "21.4%",
    severity: "High",
    memberCount: 5260,
    workaround: "Abandoning search entirely or asking friends via AirDrop",
    platforms: ["Reddit", "YouTube", "Apple App Store"],
    summary: "Broad temporal queries (e.g. '2019') return thousands of unsorted photos with no contextual sub-grouping, causing choice paralysis and abandonment.",
    evidenceList: [
      {
        layer1: {
          quote: "I know it was roughly 2018 or 2019. I searched '2018' and it's 10,000 photos. My thumb hurts from scrolling and I gave up after 20 minutes.",
          url: "https://youtube.com/watch?v=gphotos_search_tips",
          date: "Jan 18, 2026",
          source: "YouTube"
        },
        layer2: {
          tags: ["Scenario: Broad Date Search", "Failure: High Volume Fatigue", "Missing: Semantic Sub-clustering"],
          interpretation: "Broad temporal queries flood the user with unstructured chronological grids without semantic chapterization."
        },
        layer3: {
          hypothesis: "Semantic sub-clustering of broad date intervals into auto-generated event chapters will reduce chronological scroll abandonment by 35%."
        }
      }
    ]
  },
  {
    id: 4,
    title: "Uncertain Identity & Facial Recognition Drift",
    frequency: "13.9%",
    severity: "Medium",
    memberCount: 3410,
    workaround: "Searching by mutual friends or landmark surroundings",
    platforms: ["Google Help", "Reddit"],
    summary: "Facial grouping struggles across multi-year aging (baby to teenager) or occlusion, failing when users remember a person but face tag yields 0 hits.",
    evidenceList: [
      {
        layer1: {
          quote: "My nephew is now 8. Google Photos doesn't recognize his baby photos as the same person, so searching his name misses all early childhood photos.",
          url: "https://support.google.com/photos/thread/901234",
          date: "Feb 02, 2026",
          source: "Google Help Community"
        },
        layer2: {
          tags: ["Scenario: Childhood / Family", "Failure: Facial Tag Drift", "Missing: Age Progression Graph"],
          interpretation: "Facial clustering treats age progression as separate identity clusters rather than a continuous temporal identity graph."
        },
        layer3: {
          hypothesis: "Temporal identity graphing that connects toddler face clusters to adult profiles will restore 50% of missing childhood retrieval journeys."
        }
      }
    ]
  }
];

export const OPPORTUNITY_DATA = [
  { name: 'Ambient & Atmospheric Search', volume: 85, impact: 92, z: 220, category: 'AI Inference', description: 'Enable multi-cue weather, lighting, and ambient descriptors in queries.' },
  { name: 'Functional Vault Partitioning', volume: 96, impact: 78, z: 250, category: 'Information Architecture', description: 'Auto-isolate receipts, invoices, and screenshots into a utility vault.' },
  { name: 'Semantic Chapterization', volume: 74, impact: 86, z: 180, category: 'UX Navigation', description: 'Breakdown massive date ranges into intelligent sub-event chapters.' },
  { name: 'Continuous Age Identity Graph', volume: 58, impact: 70, z: 140, category: 'Face ML', description: 'Link baby, toddler, and teenage face clusters into single person timeline.' },
  { name: 'Natural Language Conversational Dialogue', volume: 68, impact: 88, z: 200, category: 'LLM Agent', description: 'Clarifying conversational follow-ups when initial query yields ambiguous volume.' },
];

export const EXECUTIVE_DOSSIER = {
  title: "Google Photos Retrieval Discovery: Executive Research Dossier",
  datasetSize: "24,592 Public User Discussions & Complaints",
  sourcesMonitored: "Google Play, App Store, Reddit, Google Help, YouTube",
  keyFindings: [
    {
      heading: "The Core Strategic Disconnect",
      body: "The primary point of failure in Google Photos is not image indexing quality, but a fundamental ontological mismatch: Human beings remember photos through episodic narrative impressions (mood, ambient lighting, who was there, personal emotion, activities), whereas modern search architectures expect exact EXIF facts (date stamps, GPS coordinates, camera filenames, or single rigid noun tags)."
    },
    {
      heading: "Primary Failure Bottleneck Identified",
      body: "Quantitative funnel analysis reveals Stage 3 (Search Query Formulation & Syntax Gap) as the dominant drop-off bottleneck, where 27% of all retrieval journeys collapse. When natural phrasing yields either 0 results or 10,000 unranked photos, 68% of users resort to high-friction chronological scrolling."
    },
    {
      heading: "The 'Functional Clutter' Tax",
      body: "Over 26% of complaints stem from screenshots, tax receipts, and work documents diluting emotional milestones. Users feel cognitive exhaustion when a search for a child's milestone brings up pharmacy receipts."
    }
  ],
  topResearchQuestions: [
    "How might we index atmospheric, lighting, and mood attributes (e.g. 'rainy cabin', 'sunset silhouette') alongside traditional object tags?",
    "Can we automatically partition 'functional utility imagery' from 'episodic memories' without requiring manual user curation?",
    "How can broad temporal searches (e.g. '2019') be dynamically synthesized into navigable semantic chapters rather than an endless vertical grid?",
    "How can facial recognition maintain continuity across human aging progression from infancy to adulthood?"
  ],
  actionablePMRecommendations: [
    { title: "Immediate (Q1/Q2): Automated Functional Vault", impact: "High", effort: "Medium", rationale: "Triage receipts and documents into a separate vault to immediately reduce visual search noise by ~30%." },
    { title: "Medium-Term (Q2/Q3): Ambient & Multi-Cue Prompting", impact: "Very High", effort: "High", rationale: "Incorporate scene atmosphere and activity verbs into the search embedding space to resolve Stage 3 syntax gap." },
    { title: "Strategic: Semantic Chapter Navigation", impact: "High", effort: "Medium", rationale: "Replace infinite vertical scroll with auto-clustered event milestones when queries span broad date ranges." }
  ]
};

export const EVIDENCE_DATASET = [
  {
    id: "EV-1001",
    source: "Reddit (r/googlephotos)",
    text: "I know we were at a beach, and my dog was there, and it was cloudy. I typed 'cloudy beach dog' and got nothing but sunny photos from California.",
    retrieval_problem: "Ambient & Setting Mismatch",
    scenario: "Travel / Vacation",
    memory_cues: ["Dog", "Beach", "Cloudy Weather", "Coast"],
    forgotten_info: ["Exact Date", "Exact GPS Location"],
    search_behavior: "Descriptive Compound Query",
    segment: "The Contextual Searcher",
    intensity: 9,
    date: "2025-10-12",
    workaround: "Scrolled manually for 45 minutes until thumb hurt",
    outcome: "Delayed Retrieval with Heavy Effort"
  },
  {
    id: "EV-1002",
    source: "Google Play Store",
    text: "My timeline is ruined by screenshots of receipts and utility bills. When I try to find a picture of my son's graduation, it's buried in tax documents.",
    retrieval_problem: "Receipt & Document Clutter",
    scenario: "Milestones & Events",
    memory_cues: ["Son", "Graduation", "Auditorium", "Blue Gown"],
    forgotten_info: ["Exact Timestamp", "Album Name"],
    search_behavior: "Timeline Browsing",
    segment: "The Exact Searcher",
    intensity: 8,
    date: "2025-11-05",
    workaround: "Created dedicated private manual albums",
    outcome: "High Friction Retrieval"
  },
  {
    id: "EV-1003",
    source: "Google Help Community",
    text: "Trying to find the photo of my daughter wearing the yellow boots jumping into a muddy puddle in 2021. Search shows random boots from web purchases.",
    retrieval_problem: "Action & Attire Parsing Failure",
    scenario: "Childhood Memories",
    memory_cues: ["Daughter", "Yellow Boots", "Muddy Puddle", "Rain"],
    forgotten_info: ["Exact Month", "Filename"],
    search_behavior: "Story & Action Query",
    segment: "The Story Searcher",
    intensity: 9,
    date: "2025-12-04",
    workaround: "Asked spouse on WhatsApp if they saved it",
    outcome: "Retrieved via External Workaround"
  },
  {
    id: "EV-1004",
    source: "YouTube Comments",
    text: "I know it was roughly 2018 or 2019. I searched '2018' and it's 10,000 photos. My thumb hurts from scrolling and I gave up after 20 minutes.",
    retrieval_problem: "Chronological Scroll Fatigue",
    scenario: "Broad Temporal Retrieval",
    memory_cues: ["Approximate Year (2018)", "Summer Vacation"],
    forgotten_info: ["Exact Month", "Exact Day", "Specific Geotag"],
    search_behavior: "Broad Year Filter",
    segment: "The Contextual Searcher",
    intensity: 9,
    date: "2026-01-18",
    workaround: "Abandoned search completely",
    outcome: "Permanent Abandonment"
  },
  {
    id: "EV-1005",
    source: "Google Help Community",
    text: "My nephew is now 8. Google Photos doesn't recognize his baby photos as the same person, so searching his name misses all early childhood photos.",
    retrieval_problem: "Facial Recognition Aging Drift",
    scenario: "Childhood Memories",
    memory_cues: ["Nephew", "Baby Face", "Hospital Blanket"],
    forgotten_info: ["Date Taken", "Exact Camera File"],
    search_behavior: "Person / Face Tag Filter",
    segment: "The Exact Searcher",
    intensity: 7,
    date: "2026-02-02",
    workaround: "Browsed baby album manually",
    outcome: "High Effort Retrieval"
  },
  {
    id: "EV-1006",
    source: "Reddit (r/googlephotos)",
    text: "I tried searching for my old apartment kitchen in 2017 with the teal tile backsplash. It only showed photos of my current apartment.",
    retrieval_problem: "Keyword Mismatch & Concept Collision",
    scenario: "Old Home & Interior",
    memory_cues: ["Teal Tiles", "Old Kitchen", "Apartment"],
    forgotten_info: ["Exact Address", "Exact Year"],
    search_behavior: "Descriptive Query",
    segment: "The Story Searcher",
    intensity: 8,
    date: "2025-08-14",
    workaround: "Scrolled back to 2017 month by month",
    outcome: "Delayed Retrieval with Heavy Effort"
  },
  {
    id: "EV-1007",
    source: "Apple App Store",
    text: "Searching for 'hiking in rain with blue jacket' brought up zero results. Had to scroll back 4 years manually to find it.",
    retrieval_problem: "Multi-Cue Compound Query Failure",
    scenario: "Travel & Vacations",
    memory_cues: ["Hiking", "Rain", "Blue Jacket", "Mountain"],
    forgotten_info: ["Exact Park Name", "Date"],
    search_behavior: "Descriptive Compound Query",
    segment: "The Contextual Searcher",
    intensity: 8,
    date: "2025-09-22",
    workaround: "Endless chronological scrolling",
    outcome: "Delayed Retrieval with Heavy Effort"
  },
  {
    id: "EV-1008",
    source: "Reddit (r/photography)",
    text: "Searching by filename is useless when you have 10 years of photos. I just want to find that hilarious memory from the camping trip.",
    retrieval_problem: "Filename Inaccessible & Emotional Disconnect",
    scenario: "Travel / Friends",
    memory_cues: ["Camping", "Campfire", "Laughing Friends", "Tent"],
    forgotten_info: ["Filename", "Exact Year"],
    search_behavior: "Emotion-based Search",
    segment: "The Emotion Searcher",
    intensity: 8,
    date: "2025-10-30",
    workaround: "Asked friend to re-send on Signal",
    outcome: "Retrieved via External Workaround"
  },
  {
    id: "EV-1009",
    source: "Google Help Community",
    text: "Why can't I search 'photos where everyone is laughing'? The AI recognizes dogs and cars, but has zero concept of group emotion or moment significance.",
    retrieval_problem: "Emotional State Blindness",
    scenario: "Family & Milestone",
    memory_cues: ["Laughing", "Dinner Table", "Family Reunion"],
    forgotten_info: ["Exact Date", "Location Name"],
    search_behavior: "Emotion-based Search",
    segment: "The Emotion Searcher",
    intensity: 7,
    date: "2025-11-19",
    workaround: "Gave up after 10 minutes",
    outcome: "Permanent Abandonment"
  },
  {
    id: "EV-1010",
    source: "Twitter / X Post",
    text: "Spent 40 minutes looking for an insurance paper photo on Google Photos. It kept showing pictures of my dog because the dog was on the couch behind the paper.",
    retrieval_problem: "Subject Priority Inversion",
    scenario: "Documents & Physical Paper",
    memory_cues: ["Insurance Paper", "Living Room", "Document"],
    forgotten_info: ["Date", "Document Title"],
    search_behavior: "Keyword: 'insurance'",
    segment: "The Exact Searcher",
    intensity: 9,
    date: "2026-01-05",
    workaround: "Re-scanned physical document with phone scanner",
    outcome: "Retrieved via External Workaround"
  }
];

