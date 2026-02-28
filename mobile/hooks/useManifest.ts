import { useEffect, useState, useCallback } from "react";
import AsyncStorage from "@react-native-async-storage/async-storage";
import { IMAGE_SERVER_URL, STORAGE_KEYS } from "@/lib/constants";
import type { MangaManifest } from "@/lib/types";

interface UseManifestResult {
  manifest: MangaManifest | null;
  loading: boolean;
  error: string | null;
  refetch: () => Promise<void>;
}

export function useManifest(): UseManifestResult {
  const [manifest, setManifest] = useState<MangaManifest | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchManifest = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const url = `${IMAGE_SERVER_URL}/manga-manifest.json`;
      const res = await fetch(url);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data: MangaManifest = await res.json();
      setManifest(data);
      // キャッシュに保存
      await AsyncStorage.setItem(
        STORAGE_KEYS.MANIFEST_CACHE,
        JSON.stringify(data)
      );
    } catch (e) {
      // ネットワークエラー時はキャッシュを試行
      try {
        const cached = await AsyncStorage.getItem(STORAGE_KEYS.MANIFEST_CACHE);
        if (cached) {
          setManifest(JSON.parse(cached));
          setError(null);
          return;
        }
      } catch {}
      setError(e instanceof Error ? e.message : "マニフェスト取得に失敗");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchManifest();
  }, [fetchManifest]);

  return { manifest, loading, error, refetch: fetchManifest };
}
