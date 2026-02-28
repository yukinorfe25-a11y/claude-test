import {
  ActivityIndicator,
  FlatList,
  StyleSheet,
  Text,
  View,
} from "react-native";
import { Image } from "expo-image";
import { useLocalSearchParams, useRouter } from "expo-router";
import { useManifest } from "@/hooks/useManifest";
import { useReadingProgress } from "@/hooks/useReadingProgress";
import { ChapterListItem } from "@/components/ChapterListItem";
import { COLORS, IMAGE_SERVER_URL } from "@/lib/constants";

export default function NovelDetailScreen() {
  const { novelId } = useLocalSearchParams<{ novelId: string }>();
  const { manifest, loading } = useManifest();
  const { getPosition } = useReadingProgress();
  const router = useRouter();

  if (loading || !manifest) {
    return (
      <View style={styles.center}>
        <ActivityIndicator size="large" color={COLORS.primary} />
      </View>
    );
  }

  const novel = manifest.novels.find((n) => n.id === novelId);
  if (!novel) {
    return (
      <View style={styles.center}>
        <Text style={styles.errorText}>作品が見つかりません</Text>
      </View>
    );
  }

  return (
    <FlatList
      data={novel.chapters}
      keyExtractor={(item) => item.id}
      style={styles.list}
      ListHeaderComponent={
        <View style={styles.header}>
          <Image
            source={{ uri: `${IMAGE_SERVER_URL}/${novel.coverImage}` }}
            style={styles.cover}
            contentFit="cover"
          />
          <Text style={styles.title}>{novel.title}</Text>
          <Text style={styles.author}>{novel.author}</Text>
        </View>
      }
      renderItem={({ item, index }) => (
        <ChapterListItem
          chapter={item}
          index={index}
          readPage={getPosition(novel.id, item.id)}
          onPress={() =>
            router.push(`/novel/${novel.id}/${item.id}`)
          }
        />
      )}
    />
  );
}

const styles = StyleSheet.create({
  center: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
    backgroundColor: COLORS.background,
  },
  errorText: { color: COLORS.primary, fontSize: 16 },
  list: { backgroundColor: COLORS.background },
  header: { alignItems: "center", paddingVertical: 24 },
  cover: {
    width: 160,
    height: 160 * (1528 / 1080),
    borderRadius: 8,
    backgroundColor: COLORS.border,
  },
  title: {
    color: COLORS.text,
    fontSize: 22,
    fontWeight: "700",
    marginTop: 16,
  },
  author: {
    color: COLORS.textSecondary,
    fontSize: 14,
    marginTop: 4,
    marginBottom: 8,
  },
});
