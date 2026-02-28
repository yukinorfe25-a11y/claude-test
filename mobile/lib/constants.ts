/** 画像配信サーバーのベースURL（ローカル開発用） */
export const IMAGE_SERVER_URL = "http://10.0.2.2:8080"; // Androidエミュレータからホストへ

/** アプリカラー */
export const COLORS = {
  background: "#1a1a2e",
  surface: "#16213e",
  primary: "#e94560",
  text: "#eee",
  textSecondary: "#aaa",
  border: "#333",
} as const;

/** 読み方向: RTL（漫画標準） */
export const READING_DIRECTION = "rtl" as const;

/** AsyncStorage キー */
export const STORAGE_KEYS = {
  READING_PROGRESS: "reading_progress",
  MANIFEST_CACHE: "manifest_cache",
} as const;
