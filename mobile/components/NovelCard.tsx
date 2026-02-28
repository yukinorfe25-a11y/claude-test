import { Image } from "expo-image";
import { Pressable, StyleSheet, Text, View } from "react-native";
import { COLORS, IMAGE_SERVER_URL } from "@/lib/constants";
import type { Novel } from "@/lib/types";

interface Props {
  novel: Novel;
  onPress: () => void;
}

export function NovelCard({ novel, onPress }: Props) {
  return (
    <Pressable
      style={({ pressed }) => [styles.card, pressed && styles.pressed]}
      onPress={onPress}
    >
      <Image
        source={{ uri: `${IMAGE_SERVER_URL}/${novel.coverImage}` }}
        style={styles.cover}
        contentFit="cover"
        transition={200}
        placeholder={{ blurhash: "L6PZfSi_.AyE_3t7t7R**0o#DgR4" }}
      />
      <View style={styles.info}>
        <Text style={styles.title} numberOfLines={2}>
          {novel.title}
        </Text>
        <Text style={styles.author}>{novel.author}</Text>
        <Text style={styles.meta}>
          {novel.chapters.length}章 /{" "}
          {novel.chapters.reduce((sum, ch) => sum + ch.pages.length, 0)}P
        </Text>
      </View>
    </Pressable>
  );
}

const styles = StyleSheet.create({
  card: {
    flex: 1,
    margin: 8,
    backgroundColor: COLORS.surface,
    borderRadius: 12,
    overflow: "hidden",
  },
  pressed: { opacity: 0.7 },
  cover: {
    width: "100%",
    aspectRatio: 1080 / 1528,
    backgroundColor: COLORS.border,
  },
  info: { padding: 10 },
  title: { color: COLORS.text, fontSize: 15, fontWeight: "700" },
  author: { color: COLORS.textSecondary, fontSize: 12, marginTop: 2 },
  meta: { color: COLORS.textSecondary, fontSize: 11, marginTop: 4 },
});
