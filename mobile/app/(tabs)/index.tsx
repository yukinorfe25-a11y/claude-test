import { ActivityIndicator, FlatList, StyleSheet, Text, View } from "react-native";
import { useRouter } from "expo-router";
import { useManifest } from "@/hooks/useManifest";
import { NovelCard } from "@/components/NovelCard";
import { COLORS } from "@/lib/constants";
import type { Novel } from "@/lib/types";

export default function LibraryScreen() {
  const { manifest, loading, error, refetch } = useManifest();
  const router = useRouter();

  if (loading) {
    return (
      <View style={styles.center}>
        <ActivityIndicator size="large" color={COLORS.primary} />
      </View>
    );
  }

  if (error || !manifest) {
    return (
      <View style={styles.center}>
        <Text style={styles.errorText}>
          {error ?? "マニフェストが見つかりません"}
        </Text>
        <Text style={styles.hintText}>
          output/ で python -m http.server 8080 を起動してください
        </Text>
      </View>
    );
  }

  const handlePress = (novel: Novel) => {
    router.push(`/novel/${novel.id}`);
  };

  return (
    <FlatList
      data={manifest.novels}
      keyExtractor={(item) => item.id}
      numColumns={2}
      contentContainerStyle={styles.grid}
      renderItem={({ item }) => (
        <NovelCard novel={item} onPress={() => handlePress(item)} />
      )}
      onRefresh={refetch}
      refreshing={loading}
    />
  );
}

const styles = StyleSheet.create({
  center: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
    backgroundColor: COLORS.background,
    padding: 20,
  },
  errorText: {
    color: COLORS.primary,
    fontSize: 16,
    fontWeight: "600",
    textAlign: "center",
  },
  hintText: {
    color: COLORS.textSecondary,
    fontSize: 13,
    marginTop: 8,
    textAlign: "center",
  },
  grid: {
    padding: 8,
    backgroundColor: COLORS.background,
  },
});
