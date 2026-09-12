import React, { useEffect, useRef } from 'react';
import { motion } from 'framer-motion';
import { ContextMessage } from '../types';
import { getExportPdfUrl, getExportImageUrl } from '../api';
import { X, MessageSquare, ShieldCheck, Clock, FileText, Image as ImageIcon, Download } from 'lucide-react';

interface ConversationModalProps {
  title?: string;
  messages: ContextMessage[];
  targetMessageId?: string;
  threadId?: string;
  query?: string;
  directAnswer?: string;
  onClose: () => void;
  isLoading?: boolean;
}

export const ConversationModal: React.FC<ConversationModalProps> = ({
  title = 'Conversation Context',
  messages,
  targetMessageId,
  threadId,
  query,
  directAnswer,
  onClose,
  isLoading = false,
}) => {
  const targetRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    if (targetRef.current) {
      targetRef.current.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
  }, [messages, targetMessageId]);

  const effectiveThreadId = threadId || messages[0]?.thread_id;

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.15 }}
      className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 backdrop-blur-xs p-4"
    >
      <motion.div
        initial={{ opacity: 0, scale: 0.95, y: 16 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        exit={{ opacity: 0, scale: 0.95, y: 16 }}
        transition={{ type: 'spring', duration: 0.25, bounce: 0.1 }}
        className="relative flex flex-col w-full max-w-3xl h-[85vh] rounded-2xl bg-white shadow-2xl border border-slate-200 overflow-hidden text-slate-800"
      >
        {/* Modal Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-200 bg-white">
          <div className="flex items-center space-x-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-indigo-50 border border-indigo-100 text-indigo-600">
              <MessageSquare className="h-4 w-4" />
            </div>
            <div>
              <h3 className="text-base font-bold text-slate-900">{title}</h3>
              <p className="text-xs text-slate-500">
                {messages.length} messages in chronological order (context window)
              </p>
            </div>
          </div>

          <div className="flex items-center space-x-2">
            <a
              href={getExportPdfUrl({
                threadId: effectiveThreadId,
                messageId: targetMessageId,
                query,
                directAnswer,
              })}
              download
              target="_blank"
              rel="noreferrer"
              className="hidden sm:inline-flex items-center space-x-1.5 rounded-lg bg-emerald-50 hover:bg-emerald-100 border border-emerald-200 px-3 py-1.5 text-xs font-semibold text-emerald-700 transition-colors shadow-2xs"
              title="Download entire chat as PDF"
            >
              <FileText className="h-3.5 w-3.5" />
              <span>Download PDF</span>
            </a>
            <a
              href={getExportImageUrl({
                threadId: effectiveThreadId,
                messageId: targetMessageId,
                query,
                directAnswer,
              })}
              download
              target="_blank"
              rel="noreferrer"
              className="hidden sm:inline-flex items-center space-x-1.5 rounded-lg bg-sky-50 hover:bg-sky-100 border border-sky-200 px-3 py-1.5 text-xs font-semibold text-sky-700 transition-colors shadow-2xs"
              title="Download entire chat as Picture (PNG)"
            >
              <ImageIcon className="h-3.5 w-3.5" />
              <span>Download Picture</span>
            </a>
            <button
              onClick={onClose}
              className="p-1.5 text-slate-400 hover:text-slate-700 rounded-lg hover:bg-slate-100 transition-colors ml-1"
            >
              <X className="h-5 w-5" />
            </button>
          </div>
        </div>

        {/* Message Feed */}
        <div className="flex-1 overflow-y-auto p-6 space-y-4 bg-slate-50/50">
          {isLoading ? (
            <div className="flex h-full items-center justify-center text-slate-400 text-sm">
              Loading conversation context...
            </div>
          ) : messages.length === 0 ? (
            <div className="flex h-full items-center justify-center text-slate-400 text-sm">
              No conversation history available.
            </div>
          ) : (
            messages.map((msg) => {
              const isTarget = msg.id === targetMessageId || msg.is_target;
              const formattedTime = new Date(msg.timestamp).toLocaleTimeString('en-US', {
                hour: '2-digit',
                minute: '2-digit',
                month: 'short',
                day: 'numeric',
              });

              return (
                <div
                  key={msg.id}
                  ref={isTarget ? targetRef : undefined}
                  className={`relative transition-all duration-200 ${
                    isTarget
                      ? 'p-4 rounded-xl bg-white border-2 border-emerald-500 shadow-md ring-2 ring-emerald-500/10'
                      : 'p-3.5 rounded-xl bg-white border border-slate-200 shadow-xs hover:border-slate-300'
                  }`}
                >
                  {isTarget && (
                    <div className="absolute -top-3 right-4 inline-flex items-center space-x-1 rounded-md bg-emerald-600 px-2.5 py-0.5 text-[10px] font-mono font-bold tracking-wide text-white uppercase shadow-sm">
                      <ShieldCheck className="h-3 w-3" />
                      <span>Retrieved Search Target</span>
                    </div>
                  )}

                  <div className="flex items-center justify-between mb-1.5">
                    <div className="flex items-center space-x-2">
                      <div className="h-6 w-6 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200 flex items-center justify-center text-[10px] font-bold">
                        {msg.participant_name.charAt(0)}
                      </div>
                      <span className="text-xs font-semibold text-slate-900">
                        {msg.participant_name}
                      </span>
                    </div>
                    <div className="flex items-center space-x-1 text-[11px] text-slate-400 font-mono">
                      <Clock className="h-3 w-3 text-slate-400" />
                      <span>{formattedTime}</span>
                    </div>
                  </div>

                  <p className="text-sm text-slate-800 pl-8 leading-relaxed">
                    "{msg.text}"
                  </p>
                </div>
              );
            })
          )}
        </div>

        {/* Modal Footer */}
        <div className="px-6 py-3 border-t border-slate-200 bg-white flex flex-wrap items-center justify-between gap-3 text-xs text-slate-500">
          <div className="flex items-center space-x-2">
            <span className="h-2 w-2 rounded-full bg-emerald-500" />
            <span>Target message highlighted with green border</span>
          </div>

          <div className="flex items-center space-x-2">
            <motion.a
              whileHover={{ scale: 1.04 }}
              whileTap={{ scale: 0.96 }}
              href={getExportPdfUrl({
                threadId: effectiveThreadId,
                messageId: targetMessageId,
                query,
                directAnswer,
              })}
              download
              target="_blank"
              rel="noreferrer"
              className="inline-flex items-center space-x-1.5 rounded-lg bg-emerald-50 hover:bg-emerald-100 border border-emerald-200 px-3 py-1.5 text-xs font-semibold text-emerald-700 transition-colors cursor-pointer"
            >
              <FileText className="h-3.5 w-3.5" />
              <span>Export PDF</span>
            </motion.a>
            <motion.a
              whileHover={{ scale: 1.04 }}
              whileTap={{ scale: 0.96 }}
              href={getExportImageUrl({
                threadId: effectiveThreadId,
                messageId: targetMessageId,
                query,
                directAnswer,
              })}
              download
              target="_blank"
              rel="noreferrer"
              className="inline-flex items-center space-x-1.5 rounded-lg bg-sky-50 hover:bg-sky-100 border border-sky-200 px-3 py-1.5 text-xs font-semibold text-sky-700 transition-colors cursor-pointer"
            >
              <ImageIcon className="h-3.5 w-3.5" />
              <span>Export Picture</span>
            </motion.a>
            <motion.button
              whileHover={{ scale: 1.04 }}
              whileTap={{ scale: 0.96 }}
              onClick={onClose}
              className="rounded-lg bg-slate-100 hover:bg-slate-200 px-4 py-1.5 text-slate-700 font-semibold transition-colors cursor-pointer"
            >
              Done
            </motion.button>
          </div>
        </div>
      </motion.div>
    </motion.div>
  );
};
