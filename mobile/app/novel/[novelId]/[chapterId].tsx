import { useCallback, useEffect } from "react";
import { StyleSheet, View } from "react-native";
import { useLocalSearchParams, useRouter } from "expo-router";
import { StatusBar } from "expo-status-bar";
import * as NavigationBar from "expo-navigation-bar";
import { useManifest } from "@/hooks/useManifest";
import { useReadingProgress } from "@/hooks/useReadingProgress";
import { MangaReader } from "@/components/MangaReader";
import { COLORS } from "@/lib/constants";
import { ActivityIndicator, Platform, Text } from "react-native";

export default function ReaderScreen() {
  const { novelId, chapterId } = useLocalSearchParams<{
    novelId: string;
    chapterId: string;
  }>();
  const { manifest } = useManifest();
  const { savePosition, getPosition } = useReadingProgress();

  // Android ナビゲーションバーを隠す
  useEffect(() => {
    if (Platform.OS === "android") {
      NavigationBar.setVisibilityAsync("hidden").catch(() => {});
    }
    return () => {
      if (Platform.OS === "android") {
        NavigationBar.setVisibilityAsync("visible").catch(() => {});
      }
    };
  }, []);

  const novel = manifest?.novels.find((n) => n.id === novelId);
  const chapter = novel?.chapters.find((c) => c.id === chapterId);

  const initialPage = getPosition(novelId!, chapterId!);

  const handlePageChange = useCallback(
    (pageIndex: number) => {
      if (novelId && chapterId) {
        savePosition(novelId, chapterId, pageIndex);
      }
    },
    [novelId, chapterId, savePosition]
  );

  if (!chapter) {
    return (
      <View style={styles.center}>
        {manifest ? (
          <Text style={{ color: COLORS.text }}>章が見つかりません</Text>
        ) : (
          <ActivityIndicator size="large" color={COLORS.primary} />
        )}
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <StatusBar hidden />
      <MangaReader
        pages={chapter.pages}
        initialPage={initialPage}
        onPageChange={handlePageChange}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#000" },
  center: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
    backgroundColor: COLORS.background,
  },
});
