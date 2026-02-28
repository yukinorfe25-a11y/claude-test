/** マニフェスト全体 */
export interface MangaManifest {
  version: number;
  generatedAt: string;
  novels: Novel[];
}

/** 作品 */
export interface Novel {
  id: string;
  title: string;
  author: string;
  coverImage: string; // 相対URL（例: "ningen_shikkaku/page_001.png"）
  chapters: Chapter[];
}

/** 章 */
export interface Chapter {
  id: string;
  title: string;
  pages: string[]; // ページ画像の相対URL配列
}

/** 読書位置 */
export interface ReadingPosition {
  novelId: string;
  chapterId: string;
  pageIndex: number;
  updatedAt: string;
}
