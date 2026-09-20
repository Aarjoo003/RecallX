import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Navbar, ActiveTab } from './components/Navbar';
import { SearchHero } from './components/SearchHero';
import { SearchPipelineIndicator } from './components/SearchPipelineIndicator';
import { AnswerBox } from './components/AnswerBox';
import { ResultCard } from './components/ResultCard';
import { ResultDataTable } from './components/ResultDataTable';
import { DecisionHub } from './components/DecisionHub';
import { TimelineView } from './components/TimelineView';
import { EvaluationLab } from './components/EvaluationLab';
import { RetrievalExplorer } from './components/RetrievalExplorer';
import { ConversationModal } from './components/ConversationModal';
import { ExplanationModal } from './components/ExplanationModal';
import { LoadingStages } from './components/LoadingStages';
import {
  searchMessages,
  getDecisions,
  getParticipants,
  getEvaluationReport,
  getMessageContext,
  getHealthCheck,
  getExportPdfUrl,
  getExportImageUrl,
} from './api';
import {
  SearchResponse,
  SearchResult,
  DecisionItem,
  Participant,
  EvaluationReport,
  SearchFilterInput,
  ContextMessage,
} from './types';
import {
  AlertTriangle,
  Search,
  CheckCircle2,
  Table,
  LayoutList,
  Code2,
  Download,
  Copy,
  Check,
  X,
  ShieldCheck,
  Cpu,
  FileText,
  Image as ImageIcon,
} from 'lucide-react';

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<ActiveTab>('search');
  const [query, setQuery] = useState<string>(
    'When did we finally settle on the destination?'
  );
  const [searchResponse, setSearchResponse] = useState<SearchResponse | null>(null);
  const [isSearching, setIsSearching] = useState<boolean>(false);
  const [searchError, setSearchError] = useState<string | null>(null);

  // Data view modes: 'cards' or 'table'
  const [viewMode, setViewMode] = useState<'cards' | 'table'>('cards');
  const [isRawDataOpen, setIsRawDataOpen] = useState<boolean>(false);
  const [copiedRawJson, setCopiedRawJson] = useState<boolean>(false);

  const [participants, setParticipants] = useState<Participant[]>([]);
  const [decisions, setDecisions] = useState<DecisionItem[]>([]);
  const [evaluationReport, setEvaluationReport] = useState<EvaluationReport | null>(null);
  const [engineOnline, setEngineOnline] = useState<boolean>(false);
  const [indexedCount, setIndexedCount] = useState<number>(5200);

  const [activeFilters, setActiveFilters] = useState<SearchFilterInput>({
    participant: undefined,
    start_date: undefined,
    end_date: undefined,
    thread_id: undefined,
    is_decision_only: false,
  });

  // Modal states
  const [explanationResult, setExplanationResult] = useState<SearchResult | null>(null);
  const [contextModalOpen, setContextModalOpen] = useState<boolean>(false);
  const [contextMessages, setContextMessages] = useState<ContextMessage[]>([]);
  const [contextTargetId, setContextTargetId] = useState<string>('');
  const [contextThreadId, setContextThreadId] = useState<string>('');
  const [contextTitle, setContextTitle] = useState<string>('Conversation Context');
  const [isLoadingContext, setIsLoadingContext] = useState<boolean>(false);

  // Initialize data on mount
  useEffect(() => {
    async function initData() {
      try {
        const health = await getHealthCheck();
        setEngineOnline(health.index_ready);
        if (health.indexed_messages) {
          setIndexedCount(health.indexed_messages);
        }
      } catch (err) {
        console.warn('Backend not responding yet:', err);
      }

      try {
        const pList = await getParticipants();
        setParticipants(pList);
      } catch (err) {
        console.warn('Failed to load participants:', err);
      }

      try {
        const dList = await getDecisions();
        setDecisions(dList);
      } catch (err) {
        console.warn('Failed to load decisions:', err);
      }

      try {
        const report = await getEvaluationReport();
        setEvaluationReport(report);
      } catch (err) {
        console.warn('Failed to load evaluation report:', err);
      }

      // Automatically execute the primary zero-overlap search query
      executeSearch('When did we finally settle on the destination?', activeFilters);
    }

    initData();
  }, []);

  // Auto-reconnect polling while engine is offline (e.g. cold start on Render)
  useEffect(() => {
    if (engineOnline) return;

    const timer = setInterval(async () => {
      try {
        const health = await getHealthCheck();
        if (health && (health.index_ready || health.status === 'healthy')) {
          setEngineOnline(true);
          if (health.indexed_messages) {
            setIndexedCount(health.indexed_messages);
          }
          const [pList, dList, report] = await Promise.allSettled([
            getParticipants(),
            getDecisions(),
            getEvaluationReport(),
          ]);
          if (pList.status === 'fulfilled') setParticipants(pList.value);
          if (dList.status === 'fulfilled') setDecisions(dList.value);
          if (report.status === 'fulfilled') setEvaluationReport(report.value);
          executeSearch(query, activeFilters);
        }
      } catch {
        // Backend still spinning up
      }
    }, 4000);

    return () => clearInterval(timer);
  }, [engineOnline, query, activeFilters]);

  // Global keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Escape closes modals
      if (e.key === 'Escape') {
        setContextModalOpen(false);
        setExplanationResult(null);
        setIsRawDataOpen(false);
      }

      // If user is not typing in an input
      const targetTag = (e.target as HTMLElement)?.tagName?.toLowerCase();
      if (targetTag !== 'input' && targetTag !== 'textarea' && targetTag !== 'select') {
        if (e.key === '1') setActiveTab('search');
        if (e.key === '2') setActiveTab('decisions');
        if (e.key === '3') setActiveTab('timeline');
        if (e.key === '4') setActiveTab('evaluation');
        if (e.key === '5') setActiveTab('explorer');
        if (e.key === '/') {
          e.preventDefault();
          const searchInput = document.querySelector('input[type="text"]') as HTMLInputElement;
          if (searchInput) searchInput.focus();
        }
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  const executeSearch = async (searchQuery: string, filters?: SearchFilterInput) => {
    if (!searchQuery.trim()) return;
    setIsSearching(true);
    setSearchError(null);
    try {
      const resp = await searchMessages({
        query: searchQuery,
        filters: filters || activeFilters,
        limit: 8,
        include_context: true,
        context_window: 3,
      });
      setSearchResponse(resp);
      setEngineOnline(true);
    } catch (err: any) {
      console.error('Search error:', err);
      setSearchError(
        'Could not complete search. Ensure the RecallX backend is running on port 8001.'
      );
    } finally {
      setIsSearching(false);
    }
  };

  const handleOpenContext = async (messageId: string, threadId?: string) => {
    setContextTargetId(messageId);
    setContextThreadId(threadId || '');
    setContextTitle(
      threadId ? `Thread: #${threadId.replace('thread_', '').replace('_', ' ').toUpperCase()}` : 'Message Context'
    );
    setContextModalOpen(true);
    setIsLoadingContext(true);
    try {
      const ctx = await getMessageContext(messageId, 5);
      setContextMessages(ctx);
    } catch (err) {
      console.error('Failed to load context:', err);
    } finally {
      setIsLoadingContext(false);
    }
  };

  const handleOpenExplanation = (result: SearchResult) => {
    setExplanationResult(result);
  };

  const handleRunQueryInSearch = (q: string) => {
    setQuery(q);
    setActiveTab('search');
    executeSearch(q, activeFilters);
  };

  const handleCopyRawJson = () => {
    if (!searchResponse) return;
    navigator.clipboard.writeText(JSON.stringify(searchResponse, null, 2));
    setCopiedRawJson(true);
    setTimeout(() => setCopiedRawJson(false), 2000);
  };

  const handleDownloadJson = () => {
    if (!searchResponse) return;
    const blob = new Blob([JSON.stringify(searchResponse, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `recallx_search_${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 selection:bg-indigo-600 selection:text-white pb-20 font-sans">
      {/* Top Navigation */}
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        indexedCount={indexedCount}
        engineOnline={engineOnline}
      />

      {/* Main Content Area */}
      {/* Main Content Area with Page Transitions */}
      <main className="mx-auto max-w-7xl px-4 sm:px-6 pt-6">
        <AnimatePresence mode="wait">
          {/* Tab 1: Semantic Search */}
          {activeTab === 'search' && (
            <motion.div
              key="search"
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -8 }}
              transition={{ duration: 0.2 }}
              className="space-y-6"
            >
              {/* Search Hero & Filter Controls */}
              <SearchHero
                query={query}
                setQuery={setQuery}
                onSearch={executeSearch}
                isLoading={isSearching}
                participants={participants}
                activeFilters={activeFilters}
                setActiveFilters={setActiveFilters}
              />

              {/* Error banner if backend not reachable */}
              {searchError && (
                <div className="max-w-3xl mx-auto rounded-2xl bg-rose-50/90 border border-rose-200 p-4 text-xs text-rose-800 flex items-center justify-between shadow-xs">
                  <div className="flex items-center space-x-2.5">
                    <AlertTriangle className="h-4 w-4 text-rose-600 shrink-0" />
                    <span>Backend offline or connecting... Ensure the RecallX API backend service is online.</span>
                  </div>
                  <button
                    onClick={() => executeSearch(query, activeFilters)}
                    className="px-2.5 py-1 rounded-lg bg-white border border-rose-200 text-rose-700 font-semibold hover:bg-rose-100 transition-colors"
                  >
                    Retry
                  </button>
                </div>
              )}

              {/* Section 7: 4-Stage Visual Progress during Search */}
              {isSearching && (
                <div className="max-w-4xl mx-auto">
                  <LoadingStages query={query} />
                </div>
              )}

              {/* Pipeline diagnostic overview */}
              {!isSearching && searchResponse && (
                <div className="max-w-4xl mx-auto">
                  <SearchPipelineIndicator response={searchResponse} />
                </div>
              )}

              {/* DIRECT SYNTHESIZED ANSWER BOX WITH ALL KEY DATA */}
              {!isSearching && searchResponse && searchResponse.synthesized_answer && (
                <div className="max-w-4xl mx-auto">
                  <AnswerBox
                    answer={searchResponse.synthesized_answer}
                    query={searchResponse.query}
                    latencyMs={searchResponse.search_latency_ms}
                    onOpenContext={(id) => handleOpenContext(id)}
                  />
                </div>
              )}

              {/* Search Results Header: Data Controls & View Switcher */}
              {!isSearching && searchResponse && (
                <div className="max-w-4xl mx-auto space-y-4">
                  <div className="flex flex-wrap items-center justify-between gap-3 px-1 text-xs text-slate-500">
                    <div className="flex items-center space-x-3">
                      <span>
                        Retrieved <strong className="text-slate-800 font-mono">{searchResponse.results.length}</strong> ranked candidates from <strong className="text-slate-800 font-mono">{indexedCount.toLocaleString()}</strong> messages
                      </span>
                      <span className="text-slate-300">•</span>
                      <span className="font-mono text-indigo-700 font-medium">
                        Sub-20ms CPU ({searchResponse.search_latency_ms.toFixed(1)}ms)
                      </span>
                    </div>

                    {/* All Data Actions: View Switcher, JSON Inspector, Export */}
                    <div className="flex items-center space-x-1.5">
                      {/* View Switcher: Cards vs Table */}
                      <div className="inline-flex rounded-lg bg-slate-100 border border-slate-200 p-0.5 shadow-2xs">
                        <motion.button
                          whileHover={{ scale: 1.03 }}
                          whileTap={{ scale: 0.97 }}
                          onClick={() => setViewMode('cards')}
                          className={`inline-flex items-center space-x-1 px-2.5 py-1 rounded-md text-xs font-medium transition-colors cursor-pointer ${
                            viewMode === 'cards'
                              ? 'bg-white text-slate-900 shadow-xs border border-slate-200/90 font-semibold'
                              : 'text-slate-600 hover:text-slate-900'
                          }`}
                          title="Conversation Message Stream"
                        >
                          <LayoutList className="h-3.5 w-3.5 text-indigo-600" />
                          <span>Stream</span>
                        </motion.button>

                        <motion.button
                          whileHover={{ scale: 1.03 }}
                          whileTap={{ scale: 0.97 }}
                          onClick={() => setViewMode('table')}
                          className={`inline-flex items-center space-x-1 px-2.5 py-1 rounded-md text-xs font-medium transition-colors cursor-pointer ${
                            viewMode === 'table'
                              ? 'bg-white text-slate-900 shadow-xs border border-slate-200/90 font-semibold'
                              : 'text-slate-600 hover:text-slate-900'
                          }`}
                          title="Structured Data Table"
                        >
                          <Table className="h-3.5 w-3.5 text-indigo-600" />
                          <span>Table Data</span>
                        </motion.button>
                      </div>

                      {/* Download Whole Chat (PDF / Picture) */}
                      {searchResponse.results.length > 0 && (
                        <div className="hidden sm:flex items-center space-x-1">
                          <motion.a
                            whileHover={{ scale: 1.04 }}
                            whileTap={{ scale: 0.96 }}
                            href={getExportPdfUrl({
                              threadId: searchResponse.results[0].thread_id,
                              messageId: searchResponse.results[0].message_id,
                              query: query,
                              directAnswer: searchResponse.synthesized_answer?.direct_answer,
                            })}
                            download
                            target="_blank"
                            rel="noreferrer"
                            className="inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-slate-50 hover:bg-slate-100 border border-slate-200 text-slate-700 transition-colors shadow-2xs text-xs font-medium cursor-pointer"
                            title="Download the entire chat conversation thread as PDF"
                          >
                            <FileText className="h-3.5 w-3.5 text-indigo-600" />
                            <span>PDF</span>
                          </motion.a>

                          <motion.a
                            whileHover={{ scale: 1.04 }}
                            whileTap={{ scale: 0.96 }}
                            href={getExportImageUrl({
                              threadId: searchResponse.results[0].thread_id,
                              messageId: searchResponse.results[0].message_id,
                              query: query,
                              directAnswer: searchResponse.synthesized_answer?.direct_answer,
                            })}
                            download
                            target="_blank"
                            rel="noreferrer"
                            className="inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-slate-50 hover:bg-slate-100 border border-slate-200 text-slate-700 transition-colors shadow-2xs text-xs font-medium cursor-pointer"
                            title="Download the entire chat conversation thread as Picture (PNG)"
                          >
                            <ImageIcon className="h-3.5 w-3.5 text-violet-600" />
                            <span>Picture</span>
                          </motion.a>
                        </div>
                      )}

                      {/* Raw Data JSON Inspector button */}
                      <motion.button
                        whileHover={{ scale: 1.04 }}
                        whileTap={{ scale: 0.96 }}
                        onClick={() => setIsRawDataOpen(true)}
                        className="inline-flex items-center space-x-1 px-2.5 py-1.5 rounded-lg bg-white border border-slate-200 text-slate-700 hover:bg-slate-50 hover:text-slate-900 transition-colors shadow-2xs cursor-pointer"
                        title="Inspect full JSON response"
                      >
                        <Code2 className="h-3.5 w-3.5 text-slate-500" />
                        <span>JSON</span>
                      </motion.button>

                      {/* Export JSON */}
                      <motion.button
                        whileHover={{ scale: 1.04 }}
                        whileTap={{ scale: 0.96 }}
                        onClick={handleDownloadJson}
                        className="inline-flex items-center space-x-1 px-2 py-1.5 rounded-lg bg-white border border-slate-200 text-slate-700 hover:bg-slate-50 hover:text-slate-900 transition-colors shadow-2xs cursor-pointer"
                        title="Export Data payload"
                      >
                        <Download className="h-3.5 w-3.5" />
                      </motion.button>
                    </div>
                  </div>

                  {/* Content: Cards or Data Table or Section 14 Empty state */}
                  {searchResponse.results.length === 0 ? (
                    <div className="rounded-2xl bg-white p-10 text-center border border-slate-200 shadow-2xs">
                      <Search className="h-8 w-8 text-slate-400 mx-auto mb-2" />
                      <h3 className="text-sm font-bold text-slate-800">
                        No matching messages found for &ldquo;{query}&rdquo;
                      </h3>
                      <p className="text-xs text-slate-500 mt-1 max-w-md mx-auto">
                        Try broadening your terms, clearing active filters, or try one of these suggestions:
                      </p>
                      <div className="mt-4 flex flex-wrap justify-center gap-2">
                        {['When did we decide on the trip?', 'What did Priya say about the budget?', 'mera bday kab hai?'].map((suggestion, idx) => (
                          <button
                            key={idx}
                            onClick={() => handleRunQueryInSearch(suggestion)}
                            className="px-3 py-1.5 rounded-xl border border-slate-200 bg-slate-50 text-xs font-medium text-slate-700 hover:bg-indigo-50 hover:border-indigo-200 hover:text-indigo-900 transition-all shadow-2xs"
                          >
                            &ldquo;{suggestion}&rdquo;
                          </button>
                        ))}
                      </div>
                    </div>
                  ) : viewMode === 'table' ? (
                    <ResultDataTable
                      results={searchResponse.results}
                      onOpenContext={handleOpenContext}
                      onOpenExplanation={handleOpenExplanation}
                    />
                  ) : (
                    searchResponse.results.map((res, index) => (
                      <ResultCard
                        key={res.message_id}
                        result={res}
                        rank={index + 1}
                        query={searchResponse.query}
                        onOpenContext={handleOpenContext}
                        onOpenExplanation={handleOpenExplanation}
                        isBestMatch={index === 0}
                      />
                    ))
                  )}
                </div>
              )}
            </motion.div>
          )}

          {/* Tab 2: Decision Hub */}
          {activeTab === 'decisions' && (
            <motion.div
              key="decisions"
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -8 }}
              transition={{ duration: 0.2 }}
            >
              <DecisionHub
                decisions={decisions}
                onOpenContext={handleOpenContext}
                isLoading={decisions.length === 0}
              />
            </motion.div>
          )}

          {/* Tab 3: Archive Timeline */}
          {activeTab === 'timeline' && (
            <motion.div
              key="timeline"
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -8 }}
              transition={{ duration: 0.2 }}
            >
              <TimelineView
                onOpenContext={(id) => handleOpenContext(id)}
                onSearchQuery={handleRunQueryInSearch}
              />
            </motion.div>
          )}

          {/* Tab 4: Evaluation Benchmark Lab */}
          {activeTab === 'evaluation' && (
            <motion.div
              key="evaluation"
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -8 }}
              transition={{ duration: 0.2 }}
            >
              <EvaluationLab
                report={evaluationReport}
                isLoading={!evaluationReport}
                onRunQueryInSearch={handleRunQueryInSearch}
              />
            </motion.div>
          )}

          {/* Tab 5: Architecture Explorer */}
          {activeTab === 'explorer' && (
            <motion.div
              key="explorer"
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -8 }}
              transition={{ duration: 0.2 }}
            >
              <RetrievalExplorer />
            </motion.div>
          )}
        </AnimatePresence>
      </main>

      {/* Raw Data JSON Modal */}
      <AnimatePresence>
        {isRawDataOpen && searchResponse && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.15 }}
            className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 backdrop-blur-xs p-4"
          >
            <motion.div
              initial={{ opacity: 0, scale: 0.95, y: 15 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: 15 }}
              transition={{ duration: 0.2 }}
              className="relative flex flex-col w-full max-w-4xl h-[85vh] rounded-2xl bg-white shadow-2xl border border-slate-200 overflow-hidden text-slate-900"
            >
              <div className="flex items-center justify-between px-6 py-4 border-b border-slate-200 bg-slate-50">
                <div className="flex items-center space-x-2">
                  <Code2 className="h-5 w-5 text-emerald-600" />
                  <h3 className="text-base font-bold text-slate-900">Full Raw Retrieval Data Payload</h3>
                  <span className="rounded-md bg-white border border-slate-200 px-2 py-0.5 text-xs font-mono text-emerald-700">
                    {searchResponse.results.length} records • {searchResponse.search_latency_ms.toFixed(1)}ms
                  </span>
                </div>
                <div className="flex items-center space-x-2">
                  <button
                    onClick={handleCopyRawJson}
                    className="flex items-center space-x-1.5 rounded-lg bg-white hover:bg-slate-50 border border-slate-200 px-3 py-1.5 text-xs font-medium text-slate-700 transition-colors shadow-2xs"
                  >
                    {copiedRawJson ? (
                      <>
                        <Check className="h-3.5 w-3.5 text-emerald-600" />
                        <span className="text-emerald-700 font-medium">Copied</span>
                      </>
                    ) : (
                      <>
                        <Copy className="h-3.5 w-3.5" />
                        <span>Copy JSON</span>
                      </>
                    )}
                  </button>
                  <button
                    onClick={() => setIsRawDataOpen(false)}
                    className="p-1.5 text-slate-400 hover:text-slate-700 rounded-lg hover:bg-slate-100 transition-colors"
                  >
                    <X className="h-5 w-5" />
                  </button>
                </div>
              </div>

              <div className="flex-1 overflow-y-auto p-4 bg-slate-950 font-mono text-xs text-emerald-300/90 leading-relaxed">
                <pre>{JSON.stringify(searchResponse, null, 2)}</pre>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Explanation Drawer Modal */}
      <AnimatePresence>
        {explanationResult && (
          <ExplanationModal
            result={explanationResult}
            query={searchResponse?.query || query}
            onClose={() => setExplanationResult(null)}
          />
        )}
      </AnimatePresence>

      {/* Conversation Thread Window Modal */}
      <AnimatePresence>
        {contextModalOpen && (
          <ConversationModal
            title={contextTitle}
            messages={contextMessages}
            targetMessageId={contextTargetId}
            threadId={contextThreadId}
            query={searchResponse?.query || query}
            directAnswer={searchResponse?.synthesized_answer?.direct_answer}
            onClose={() => setContextModalOpen(false)}
            isLoading={isLoadingContext}
          />
        )}
      </AnimatePresence>
    </div>
  );
};

export default App;
