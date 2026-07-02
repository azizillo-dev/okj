'use client';

import React from 'react';
import dynamic from 'next/dynamic';
import { Navbar } from './Navbar';
import { useUIStore } from '@/lib/store/uiStore';
import { AmbientBackground } from '@/components/ui/glass/AmbientBackground';

// Lazy load heavy modals for bundle optimization
const CreatePostModal = dynamic(() => import('@/components/posts/CreatePostModal'), {
  ssr: false,
});

export const ClientLayoutShell: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isCreateModalOpen, openCreateModal, closeCreateModal } = useUIStore();

  return (
    <div className="min-h-screen flex flex-col bg-okj-bg-deep text-okj-text-primary selection:bg-okj-gold selection:text-okj-bg-deep relative overflow-x-hidden">
      <AmbientBackground />
      <Navbar onOpenCreateModal={openCreateModal} />
      <main className="flex-1 pb-20 md:pb-8 relative z-10 w-full ultrawide-container">{children}</main>
      {isCreateModalOpen && <CreatePostModal isOpen={isCreateModalOpen} onClose={closeCreateModal} />}
    </div>
  );
};
