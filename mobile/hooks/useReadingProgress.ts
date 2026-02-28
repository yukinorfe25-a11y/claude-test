import { useEffect, useState, useCallback } from "react";
import AsyncStorage from "@react-native-async-storage/async-storage";
import { STORAGE_KEYS } from "@/lib/constants";
import type { ReadingPosition } from "@/lib/types";

type ProgressMap = Record<string, ReadingPosition>;

export function useReadingProgress() {
  const [progress, setProgress] = useState<ProgressMap>({});

  // 起動時に読み込み
  useEffect(() => {
    (async () => {
      try {
        const raw = await AsyncStorage.getItem(STORAGE_KEYS.READING_PROGRESS);
        if (raw) setProgress(JSON.parse(raw));
      } catch {}
    })();
  }, []);

  /** 読書位置を保存 */
  const savePosition = useCallback(
    async (novelId: string, chapterId: string, pageIndex: number) => {
      const key = `${novelId}/${chapterId}`;
      const pos: ReadingPosition = {
        novelId,
        chapterId,
        pageIndex,
        updatedAt: new Date().toISOString(),
      };
      const next = { ...progress, [key]: pos };
      setProgress(next);
      await AsyncStorage.setItem(
        STORAGE_KEYS.READING_PROGRESS,
        JSON.stringify(next)
      );
    },
    [progress]
  );

  /** 読書位置を取得 */
  const getPosition = useCallback(
    (novelId: string, chapterId: string): number => {
      const key = `${novelId}/${chapterId}`;
      return progress[key]?.pageIndex ?? 0;
    },
    [progress]
  );

  /** 作品の最終読書位置を取得 */
  const getLastRead = useCallback(
    (novelId: string): ReadingPosition | null => {
      const entries = Object.values(progress).filter(
        (p) => p.novelId === novelId
      );
      if (entries.length === 0) return null;
      return entries.sort(
        (a, b) =>
          new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime()
      )[0];
    },
    [progress]
  );

  return { savePosition, getPosition, getLastRead };
}
