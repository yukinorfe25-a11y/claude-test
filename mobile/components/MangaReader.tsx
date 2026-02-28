import { useCallback, useRef, useState } from "react";
import {
  Dimensions,
  StyleSheet,
  View,
} from "react-native";
import PagerView from "react-native-pager-view";
import { Image } from "expo-image";
import { IMAGE_SERVER_URL, COLORS } from "@/lib/constants";
import { ReadingProgress } from "./ReadingProgress";

const { width: SCREEN_W, height: SCREEN_H } = Dimensions.get("window");

interface Props {
  pages: string[];
  initialPage?: number;
  onPageChange?: (index: number) => void;
}

export function MangaReader({ pages, initialPage = 0, onPageChange }: Props) {
  const [currentPage, setCurrentPage] = useState(initialPage);
  const [showUI, setShowUI] = useState(true);
  const pagerRef = useRef<PagerView>(null);

  const handlePageSelected = useCallback(
    (e: { nativeEvent: { position: number } }) => {
      const idx = e.nativeEvent.position;
      setCurrentPage(idx);
      onPageChange?.(idx);
    },
    [onPageChange]
  );

  const toggleUI = useCallback(() => {
    setShowUI((v) => !v);
  }, []);

  // 隣接ページをプリフェッチ
  const prefetchNeighbors = useCallback(
    (idx: number) => {
      const neighbors = [idx - 1, idx + 1].filter(
        (i) => i >= 0 && i < pages.length
      );
      for (const n of neighbors) {
        Image.prefetch(`${IMAGE_SERVER_URL}/${pages[n]}`);
      }
    },
    [pages]
  );

  return (
    <View style={styles.container}>
      <PagerView
        ref={pagerRef}
        style={styles.pager}
        initialPage={initialPage}
        layoutDirection="rtl"
        onPageSelected={(e) => {
          handlePageSelected(e);
          prefetchNeighbors(e.nativeEvent.position);
        }}
        overdrag
      >
        {pages.map((page, idx) => (
          <View key={page} style={styles.page} collapsable={false}>
            <Image
              source={{ uri: `${IMAGE_SERVER_URL}/${page}` }}
              style={styles.image}
              contentFit="contain"
              transition={100}
              onTouchEnd={toggleUI}
            />
          </View>
        ))}
      </PagerView>

      {showUI && <ReadingProgress current={currentPage} total={pages.length} />}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: COLORS.background,
  },
  pager: {
    flex: 1,
  },
  page: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
  },
  image: {
    width: SCREEN_W,
    height: SCREEN_H,
  },
});
