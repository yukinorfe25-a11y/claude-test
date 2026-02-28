import { Pressable, StyleSheet, Text, View } from "react-native";
import { COLORS } from "@/lib/constants";
import type { Chapter } from "@/lib/types";

interface Props {
  chapter: Chapter;
  index: number;
  readPage: number; // 最後に読んだページ（0=未読）
  onPress: () => void;
}

export function ChapterListItem({ chapter, index, readPage, onPress }: Props) {
  const total = chapter.pages.length;
  const isStarted = readPage > 0;
  const isComplete = readPage >= total - 1;

  return (
    <Pressable
      style={({ pressed }) => [styles.item, pressed && styles.pressed]}
      onPress={onPress}
    >
      <View style={styles.row}>
        <View style={styles.left}>
          <Text style={styles.title}>{chapter.title}</Text>
          <Text style={styles.meta}>{total} ページ</Text>
        </View>
        <View style={styles.right}>
          {isComplete ? (
            <Text style={styles.badge}>読了</Text>
          ) : isStarted ? (
            <Text style={styles.progress}>
              {readPage + 1}/{total}
            </Text>
          ) : null}
          <Text style={styles.arrow}>›</Text>
        </View>
      </View>
    </Pressable>
  );
}

const styles = StyleSheet.create({
  item: {
    paddingHorizontal: 16,
    paddingVertical: 14,
    borderBottomWidth: StyleSheet.hairlineWidth,
    borderBottomColor: COLORS.border,
  },
  pressed: { backgroundColor: COLORS.surface },
  row: { flexDirection: "row", alignItems: "center" },
  left: { flex: 1 },
  title: { color: COLORS.text, fontSize: 16, fontWeight: "600" },
  meta: { color: COLORS.textSecondary, fontSize: 12, marginTop: 2 },
  right: { flexDirection: "row", alignItems: "center", gap: 8 },
  badge: {
    color: COLORS.primary,
    fontSize: 12,
    fontWeight: "700",
  },
  progress: { color: COLORS.textSecondary, fontSize: 12 },
  arrow: { color: COLORS.textSecondary, fontSize: 22 },
});
