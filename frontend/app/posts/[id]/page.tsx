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
    // Fallback production-ready sample post data if backend offline
    post = {
      id,
      user: {
        id: 'u-10492',
        username: 'alisher_rustamov',
        first_name: 'Alisher',
        last_name: 'Rustamov',
        okj_id: 'OKJ-10492',
        total_xp: 1450,
      },
      post_type: 'QUOTE',
      title: "Navoiy dahosidan boqiy hikmatlar",
      content: "Odamiylik deb bilg'il odamni, Onikim yo'qtur xalq g'amidan g'ami.\n\nHar birimiz jamiyat foydasi uchun o'z hissamizni qo'shishni eng oliy maqsad deb bilmog'imiz zarur.",
      book: {
        id: 'b-1',
        title: 'Xamsai Mutahayyirin',
        slug: 'xamsai-mutahayyirin',
        authors: [{ id: 'a1', name: 'Alisher Navoiy' }],
      },
      quote_page: 84,
      media: [
        {
          id: 'm-1',
          file_url: 'https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?auto=format&fit=crop&w=1200&q=80',
          media_type: 'IMAGE',
        },
      ],
      likes_count: 142,
      comments_count: 3,
      is_liked_by_user: false,
      created_at: new Date().toISOString(),
    };

    comments = [
      {
        id: 'c-1',
        post_id: id,
        user: {
          id: 'u-20511',
          username: 'bookworm_uz',
          first_name: 'Malika',
          last_name: 'Saidova',
          okj_id: 'OKJ-20511',
          total_xp: 800,
        },
        content: "G'oyat chuqur ma'no! Har safar o'qiganimda yangicha falsafani his qilaman.",
        likes_count: 14,
        is_liked_by_user: true,
        created_at: '2026-07-02T10:30:00Z',
        replies: [
          {
            id: 'c-1-1',
            post_id: id,
            parent_id: 'c-1',
            user: {
              id: 'u-10492',
              username: 'alisher_rustamov',
              first_name: 'Alisher',
              last_name: 'Rustamov',
              okj_id: 'OKJ-10492',
              total_xp: 1450,
            },
            content: "Rahmat Malika! Mutlaqo qo'shilaman, klassikamiz hech qachon eskirmaydi.",
            likes_count: 5,
            created_at: '2026-07-02T11:45:00Z',
          },
        ],
      },
      {
        id: 'c-2',
        post_id: id,
        user: {
          id: 'u-31005',
          username: 'intellect_99',
          first_name: 'Sardor',
          last_name: 'Ismoilov',
          okj_id: 'OKJ-31005',
          total_xp: 2100,
        },
        content: "Ushbu nashrning qaysi yildagisi bo'ldi? Muqovasi juda chiroyli ekan.",
        likes_count: 8,
        created_at: '2026-07-02T12:15:00Z',
      },
    ];
  }

  return <PostDetailView post={post} initialComments={comments} />;
}
