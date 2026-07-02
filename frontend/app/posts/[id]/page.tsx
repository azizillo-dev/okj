import React from 'react';
import { Metadata } from 'next';
import { postsApi } from '@/lib/api/posts';
import { Post, Comment } from '@/lib/api/types';
import { PostDetailView } from '@/components/features/post-detail/PostDetailView';

// Generate dynamic metadata for OpenGraph and SEO
export async function generateMetadata({ params }: { params: Promise<{ id: string }> }): Promise<Metadata> {
  const { id } = await params;
  try {
    const post = await postsApi.getPostById(id);
    return {
      title: `${post.title || post.user.first_name + ' posti'} — OKJ Platformasi`,
      description: post.content.substring(0, 160),
      openGraph: {
        title: post.title || 'OKJ Jonli Muhokama',
        description: post.content.substring(0, 160),
        images: post.media?.[0]?.file_url ? [post.media[0].file_url] : [],
      },
    };
  } catch {
    return {
      title: "Kitobxon post detali — OKJ Platformasi",
      description: "O'zbekiston Kitobxonlari Jamiyati platformasida jonli kitobxonlik muhokamalari.",
    };
  }
}

export default async function PostDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;

  let post: Post;
  let comments: Comment[] = [];

  try {
    post = await postsApi.getPostById(id);
    comments = await postsApi.getPostComments(id);
  } catch {
    return (
      <div className="max-w-4xl mx-auto p-12 text-center">
        <div className="p-8 rounded-3xl bg-okj-card/80 border border-white/10 backdrop-blur-xl max-w-md mx-auto space-y-4 shadow-2xl">
          <h2 className="font-display font-bold text-xl text-okj-text-primary">Post topilmadi</h2>
          <p className="text-xs text-okj-text-secondary">
            Siz qidirayotgan post mavjud emas yoki o&apos;chirib yuborilgan.
          </p>
        </div>
      </div>
    );
  }

  return <PostDetailView post={post} initialComments={comments} />;
}
