'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { AlertTriangle, Trash2, Edit3, Flag, CheckCircle } from 'lucide-react';
import { Post } from '@/lib/api/types';
import { postsApi } from '@/lib/api/posts';
import { GlassModal, GlassButton } from '@/components/ui/glass';

interface PostActionsMenuProps {
  post: Post;
  isAuthor: boolean;
}

export const PostActionsMenu: React.FC<PostActionsMenuProps> = ({ post, isAuthor }) => {
  const router = useRouter();
  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);
  const [isReportModalOpen, setIsReportModalOpen] = useState(false);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);

  const [reportReason, setReportReason] = useState('SPAM');
  const [reportDescription, setReportDescription] = useState('');
  const [isReporting, setIsReporting] = useState(false);
  const [reportSuccess, setReportSuccess] = useState(false);

  const [editTitle, setEditTitle] = useState(post.title || '');
  const [editContent, setEditContent] = useState(post.content);
  const [isEditing, setIsEditing] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);

  const handleDelete = async () => {
    setIsDeleting(true);
    try {
      await postsApi.deletePost(post.id);
      router.push('/feed');
    } finally {
      setIsDeleting(false);
    }
  };

  const handleReportSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsReporting(true);
    try {
      await postsApi.reportPost(post.id, reportReason, reportDescription);
      setReportSuccess(true);
      setTimeout(() => {
        setIsReportModalOpen(false);
        setReportSuccess(false);
      }, 1500);
    } finally {
      setIsReporting(false);
    }
  };

  const handleEditSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsEditing(true);
    try {
      // Simulate post edit saving locally
      post.title = editTitle;
      post.content = editContent;
      setIsEditModalOpen(false);
    } finally {
      setIsEditing(false);
    }
  };

  return (
    <div className="flex items-center gap-2">
      {isAuthor ? (
        <>
          <button
            type="button"
            onClick={() => setIsEditModalOpen(true)}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-white/5 hover:bg-white/10 text-xs font-medium text-okj-text-secondary hover:text-okj-text-primary transition-colors"
          >
            <Edit3 className="w-3.5 h-3.5" />
            <span>Tahrirlash</span>
          </button>
          <button
            type="button"
            onClick={() => setIsDeleteModalOpen(true)}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-rose-500/10 hover:bg-rose-500/20 text-xs font-medium text-rose-400 transition-colors"
          >
            <Trash2 className="w-3.5 h-3.5" />
            <span>O&apos;chirish</span>
          </button>
        </>
      ) : (
        <button
          type="button"
          onClick={() => setIsReportModalOpen(true)}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-white/5 hover:bg-white/10 text-xs font-medium text-okj-text-secondary hover:text-rose-400 transition-colors"
        >
          <Flag className="w-3.5 h-3.5" />
          <span>Shikoyat (Report)</span>
        </button>
      )}

      {/* Delete Confirmation Modal */}
      <GlassModal
        isOpen={isDeleteModalOpen}
        onClose={() => setIsDeleteModalOpen(false)}
        title="Postni O'chirish"
      >
        <div className="space-y-4 pt-2">
          <p className="text-xs text-okj-text-secondary">
            Haqiqatan ham ushbu postni o&apos;chirmoqchimisiz? Bu amalni ortga qaytarib bo&apos;lmaydi va barcha izohlar ham o&apos;chib ketadi.
          </p>
          <div className="flex justify-end gap-3 pt-2">
            <GlassButton variant="secondary" onClick={() => setIsDeleteModalOpen(false)}>
              Bekor qilish
            </GlassButton>
            <button
              type="button"
              onClick={handleDelete}
              disabled={isDeleting}
              className="px-4 py-2 rounded-xl bg-rose-600 hover:bg-rose-700 text-white font-display font-bold text-xs transition-colors disabled:opacity-50"
            >
              {isDeleting ? 'O\'chirilmoqda...' : 'Ha, O\'chirish'}
            </button>
          </div>
        </div>
      </GlassModal>

      {/* Edit Post Modal */}
      <GlassModal
        isOpen={isEditModalOpen}
        onClose={() => setIsEditModalOpen(false)}
        title="Postni Tahrirlash"
      >
        <form onSubmit={handleEditSubmit} className="space-y-4 pt-2">
          <div className="space-y-1">
            <label className="text-xs font-bold text-okj-text-secondary">Sarlavha</label>
            <input
              type="text"
              value={editTitle}
              onChange={(e) => setEditTitle(e.target.value)}
              className="w-full rounded-xl bg-okj-bg-deep border border-okj-card-border p-3 text-sm text-okj-text-primary focus:outline-none focus:border-okj-gold"
            />
          </div>
          <div className="space-y-1">
            <label className="text-xs font-bold text-okj-text-secondary">Matn</label>
            <textarea
              value={editContent}
              onChange={(e) => setEditContent(e.target.value)}
              rows={5}
              className="w-full rounded-xl bg-okj-bg-deep border border-okj-card-border p-3 text-sm text-okj-text-primary focus:outline-none focus:border-okj-gold resize-none"
            />
          </div>
          <div className="flex justify-end gap-3 pt-2">
            <GlassButton variant="secondary" onClick={() => setIsEditModalOpen(false)}>
              Bekor qilish
            </GlassButton>
            <GlassButton variant="gold" onClick={() => {}}>
              {isEditing ? 'Saqlanmoqda...' : 'Saqlash'}
            </GlassButton>
          </div>
        </form>
      </GlassModal>

      {/* Report Post Modal */}
      <GlassModal
        isOpen={isReportModalOpen}
        onClose={() => setIsReportModalOpen(false)}
        title="Shikoyat Yuborish"
      >
        {reportSuccess ? (
          <div className="p-6 text-center space-y-3">
            <CheckCircle className="w-12 h-12 text-emerald-400 mx-auto" />
            <h4 className="font-display font-bold text-sm text-okj-text-primary">Shikoyatingiz qabul qilindi</h4>
            <p className="text-xs text-okj-text-secondary">Moderatorlarimiz tez orada tekshiruv o&apos;tkazishadi.</p>
          </div>
        ) : (
          <form onSubmit={handleReportSubmit} className="space-y-4 pt-2">
            <div className="space-y-2">
              <label className="text-xs font-bold text-okj-text-secondary">Sababni tanlang:</label>
              <select
                value={reportReason}
                onChange={(e) => setReportReason(e.target.value)}
                className="w-full rounded-xl bg-okj-bg-deep border border-okj-card-border p-2.5 text-xs text-okj-text-primary focus:outline-none focus:border-okj-gold"
              >
                <option value="SPAM">Spam yoki reklama</option>
                <option value="HARASSMENT">Hakorat va zo&apos;ravonlik</option>
                <option value="COPYRIGHT">Mualliflik huquqi buzilishi</option>
                <option value="MISLEADING">Yolg&apos;on ma&apos;lumot</option>
              </select>
            </div>
            <div className="space-y-1">
              <label className="text-xs font-bold text-okj-text-secondary">Qo&apos;shimcha izoh (ixtiyoriy):</label>
              <textarea
                value={reportDescription}
                onChange={(e) => setReportDescription(e.target.value)}
                rows={3}
                placeholder="Bu post nima sababdan qoidalarni buzayotganini yozing..."
                className="w-full rounded-xl bg-okj-bg-deep border border-okj-card-border p-2.5 text-xs text-okj-text-primary focus:outline-none focus:border-okj-gold resize-none"
              />
            </div>
            <div className="flex justify-end gap-3 pt-2">
              <GlassButton variant="secondary" onClick={() => setIsReportModalOpen(false)}>
                Bekor qilish
              </GlassButton>
              <button
                type="submit"
                disabled={isReporting}
                className="px-4 py-2 rounded-xl bg-rose-600 hover:bg-rose-700 text-white font-display font-bold text-xs transition-colors disabled:opacity-50 flex items-center gap-1.5"
              >
                <AlertTriangle className="w-3.5 h-3.5" />
                <span>{isReporting ? 'Yuborilmoqda...' : 'Shikoyat qilish'}</span>
              </button>
            </div>
          </form>
        )}
      </GlassModal>
    </div>
  );
};
