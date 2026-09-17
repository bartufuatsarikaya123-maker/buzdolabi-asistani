import { useEffect, useState } from "react";
import {
  ActivityIndicator,
  SafeAreaView,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  TouchableOpacity,
  View,
} from "react-native";

export default function App() {
  const [categories, setCategories] = useState<Record<string, any>>({});
  const [searchQuery, setSearchQuery] = useState("");
  const [myFridge, setMyFridge] = useState<string[]>([]);
  const [selectedForRecipe, setSelectedForRecipe] = useState<string[]>([]);
  const [recipeResult, setRecipeResult] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isFetchingData, setIsFetchingData] = useState(true);

  const API_URL = "http://192.168.1.3:8000";

  useEffect(() => {
    fetchFoods();
  }, []);

  const fetchFoods = async () => {
    try {
      const response = await fetch(`${API_URL}/foods`);
      const data = await response.json();
      setCategories(data.categories);
    } catch (error) {
      console.error("Veriler alınırken hata:", error);
    } finally {
      setIsFetchingData(false);
    }
  };

  const getSearchResults = () => {
    if (!searchQuery.trim()) return [];
    let results: { key: string; name: string }[] = [];
    Object.keys(categories).forEach((cat) => {
      Object.keys(categories[cat]).forEach((key) => {
        const item = categories[cat][key];
        if (item.name.toLowerCase().includes(searchQuery.toLowerCase())) {
          results.push({ key, name: item.name });
        }
      });
    });
    return results;
  };

  const getItemName = (searchKey: string) => {
    for (const cat of Object.keys(categories)) {
      if (categories[cat][searchKey]) {
        return categories[cat][searchKey].name.split(" (")[0];
      }
    }
    return searchKey;
  };

  const addToFridge = (key: string) => {
    if (!myFridge.includes(key)) {
      setMyFridge([...myFridge, key]);
    }
    setSearchQuery("");
  };

  const removeFromFridge = (key: string) => {
    setMyFridge(myFridge.filter((item) => item !== key));
    if (selectedForRecipe.includes(key)) {
      setSelectedForRecipe(selectedForRecipe.filter((item) => item !== key));
    }
  };

  const toggleForRecipe = (key: string) => {
    if (selectedForRecipe.includes(key)) {
      setSelectedForRecipe(selectedForRecipe.filter((item) => item !== key));
    } else {
      setSelectedForRecipe([...selectedForRecipe, key]);
    }
  };

  const getRecipe = async () => {
    if (selectedForRecipe.length === 0) return;
    setIsLoading(true);
    try {
      const response = await fetch(`${API_URL}/get-recipe`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ingredients: selectedForRecipe }),
      });
      const data = await response.json();
      setRecipeResult(data);
    } catch (error) {
      console.error("Tarif alınırken hata:", error);
    } finally {
      setIsLoading(false);
    }
  };

  // YENİ EKLENEN RASTGELE TARİF FONKSİYONU
  const getRandomRecipe = async () => {
    if (myFridge.length === 0) {
      alert(
        "Önce dolabına birkaç malzeme eklemelisin ki sana onlardan bir şeyler önerebileyim!",
      );
      return;
    }

    setIsLoading(true);
    try {
      const response = await fetch(`${API_URL}/random-recipe`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ingredients: myFridge }), // Sadece dolaptakiler gönderiliyor
      });
      const data = await response.json();
      setRecipeResult(data);
    } catch (error) {
      console.error("Rastgele tarif alınırken hata:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const searchResults = getSearchResults();

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Buzdolabı Asistanı</Text>
        <Text style={styles.headerSubtitle}>
          Önce malzemelerini dolaba ekle, sonra seç
        </Text>
      </View>

      <View style={styles.searchContainer}>
        <TextInput
          style={styles.searchInput}
          placeholder="Malzeme ara (örn: Domates, Tavuk...)"
          placeholderTextColor="#ADB5BD"
          value={searchQuery}
          onChangeText={setSearchQuery}
        />
      </View>

      <ScrollView style={styles.content} showsVerticalScrollIndicator={false}>
        {isFetchingData ? (
          <ActivityIndicator
            size="large"
            color="#4CAF50"
            style={{ marginTop: 50 }}
          />
        ) : searchQuery.length > 0 ? (
          <View>
            <Text style={styles.sectionTitle}>Arama Sonuçları</Text>
            {searchResults.length > 0 ? (
              searchResults.map((item) => (
                <View key={item.key} style={styles.searchItemCard}>
                  <Text style={styles.searchItemText}>{item.name}</Text>
                  <TouchableOpacity
                    style={[
                      styles.addButton,
                      myFridge.includes(item.key) && styles.addButtonDisabled,
                    ]}
                    onPress={() => addToFridge(item.key)}
                    disabled={myFridge.includes(item.key)}
                  >
                    <Text style={styles.addButtonText}>
                      {myFridge.includes(item.key) ? "Dolapta" : "+ Ekle"}
                    </Text>
                  </TouchableOpacity>
                </View>
              ))
            ) : (
              <Text style={styles.emptyText}>Malzeme bulunamadı.</Text>
            )}
          </View>
        ) : (
          <View>
            <Text style={styles.sectionTitle}>
              Benim Dolabım ({myFridge.length})
            </Text>
            {myFridge.length === 0 ? (
              <Text style={styles.emptyText}>
                Dolabın şu an boş. Yukarıdan arama yaparak malzeme eklemeye
                başla!
              </Text>
            ) : (
              <View style={styles.itemsWrapper}>
                {myFridge.map((key) => {
                  const isSelected = selectedForRecipe.includes(key);
                  return (
                    <View key={key} style={styles.fridgeItemContainer}>
                      <TouchableOpacity
                        style={[
                          styles.itemButton,
                          isSelected && styles.itemButtonSelected,
                        ]}
                        onPress={() => toggleForRecipe(key)}
                      >
                        <Text
                          style={[
                            styles.itemText,
                            isSelected && styles.itemTextSelected,
                          ]}
                        >
                          {getItemName(key)}
                        </Text>
                      </TouchableOpacity>
                      <TouchableOpacity
                        onPress={() => removeFromFridge(key)}
                        style={styles.removeIcon}
                      >
                        <Text style={styles.removeIconText}>✕</Text>
                      </TouchableOpacity>
                    </View>
                  );
                })}
              </View>
            )}

            {/* Sonuç Kartı */}
            {recipeResult && (
              <View style={styles.resultCard}>
                <Text style={styles.resultTitle}>
                  Seçili Öğünün Besin Değerleri
                </Text>
                <View style={styles.macroRow}>
                  <View style={styles.macroBox}>
                    <Text style={styles.macroValue}>
                      {recipeResult?.nutrients?.calories}
                    </Text>
                    <Text style={styles.macroLabel}>kcal</Text>
                  </View>
                  <View style={styles.macroBox}>
                    <Text style={styles.macroValue}>
                      {recipeResult?.nutrients?.protein}g
                    </Text>
                    <Text style={styles.macroLabel}>Protein</Text>
                  </View>
                  <View style={styles.macroBox}>
                    <Text style={styles.macroValue}>
                      {recipeResult?.nutrients?.carbs}g
                    </Text>
                    <Text style={styles.macroLabel}>Karb.</Text>
                  </View>
                  <View style={styles.macroBox}>
                    <Text style={styles.macroValue}>
                      {recipeResult?.nutrients?.fat}g
                    </Text>
                    <Text style={styles.macroLabel}>Yağ</Text>
                  </View>
                </View>
                <Text style={styles.recipeText}>
                  {recipeResult.recipe_suggestion}
                </Text>
              </View>
            )}
          </View>
        )}
      </ScrollView>

      {/* FOOTER: BUTONLARIN OLDUĞU KISIM */}
      <View style={styles.footer}>
        <TouchableOpacity
          style={[
            styles.actionButton,
            selectedForRecipe.length === 0 && styles.actionButtonDisabled,
          ]}
          onPress={getRecipe}
          disabled={selectedForRecipe.length === 0 || isLoading}
        >
          {isLoading ? (
            <ActivityIndicator color="#fff" />
          ) : (
            <Text style={styles.actionButtonText}>
              {selectedForRecipe.length > 0
                ? `Tarif İste (${selectedForRecipe.length} Seçili)`
                : "Tarif İçin Malzeme Seç"}
            </Text>
          )}
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.randomButton}
          onPress={getRandomRecipe}
          disabled={isLoading}
        >
          <Text style={styles.randomButtonText}>
            🎲 Kararsızım, Sürpriz Tarif Öner
          </Text>
        </TouchableOpacity>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#F8F9FA" },
  header: { padding: 20, paddingTop: 40, backgroundColor: "#fff" },
  headerTitle: { fontSize: 24, fontWeight: "bold", color: "#212529" },
  headerSubtitle: { fontSize: 14, color: "#6C757D", marginTop: 4 },
  searchContainer: {
    paddingHorizontal: 20,
    paddingBottom: 15,
    backgroundColor: "#fff",
    borderBottomWidth: 1,
    borderColor: "#E9ECEF",
  },
  searchInput: {
    backgroundColor: "#F1F3F5",
    height: 46,
    borderRadius: 12,
    paddingHorizontal: 16,
    fontSize: 15,
    color: "#212529",
  },
  content: { flex: 1, padding: 20 },
  sectionTitle: {
    fontSize: 18,
    fontWeight: "bold",
    color: "#343A40",
    marginBottom: 15,
  },
  searchItemCard: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    backgroundColor: "#fff",
    padding: 16,
    borderRadius: 12,
    marginBottom: 10,
    borderWidth: 1,
    borderColor: "#E9ECEF",
  },
  searchItemText: {
    fontSize: 15,
    color: "#495057",
    fontWeight: "500",
    flex: 1,
  },
  addButton: {
    backgroundColor: "#E7F5FF",
    paddingVertical: 8,
    paddingHorizontal: 14,
    borderRadius: 8,
  },
  addButtonDisabled: { backgroundColor: "#F1F3F5" },
  addButtonText: { color: "#1C7ED6", fontWeight: "bold", fontSize: 13 },
  emptyText: {
    color: "#ADB5BD",
    fontStyle: "italic",
    lineHeight: 22,
    textAlign: "center",
    marginTop: 20,
  },
  itemsWrapper: { flexDirection: "row", flexWrap: "wrap", gap: 12 },
  fridgeItemContainer: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: "#fff",
    borderRadius: 20,
    borderWidth: 1,
    borderColor: "#DEE2E6",
  },
  itemButton: { paddingVertical: 10, paddingHorizontal: 16, borderRadius: 20 },
  itemButtonSelected: { backgroundColor: "#E8F5E9" },
  itemText: { color: "#495057", fontSize: 14, fontWeight: "600" },
  itemTextSelected: { color: "#2E7D32" },
  removeIcon: { padding: 10, borderLeftWidth: 1, borderColor: "#F1F3F5" },
  removeIconText: { color: "#FA5252", fontSize: 14, fontWeight: "bold" },
  resultCard: {
    backgroundColor: "#fff",
    padding: 20,
    borderRadius: 16,
    marginTop: 25,
    marginBottom: 40,
    shadowColor: "#000",
    shadowOpacity: 0.05,
    shadowRadius: 10,
    elevation: 3,
  },
  resultTitle: {
    fontSize: 16,
    fontWeight: "bold",
    color: "#212529",
    marginBottom: 15,
  },
  macroRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    marginBottom: 15,
  },
  macroBox: { alignItems: "center" },
  macroValue: { fontSize: 18, fontWeight: "bold", color: "#4CAF50" },
  macroLabel: { fontSize: 12, color: "#6C757D", marginTop: 4 },
  recipeText: {
    fontSize: 14,
    color: "#495057",
    lineHeight: 22,
    fontStyle: "italic",
  },
  footer: {
    padding: 20,
    backgroundColor: "#fff",
    borderTopWidth: 1,
    borderColor: "#E9ECEF",
  },
  actionButton: {
    backgroundColor: "#4CAF50",
    padding: 16,
    borderRadius: 12,
    alignItems: "center",
  },
  actionButtonDisabled: { backgroundColor: "#A5D6A7" },
  actionButtonText: { color: "#fff", fontSize: 16, fontWeight: "bold" },
  randomButton: {
    marginTop: 12,
    padding: 16,
    borderRadius: 12,
    alignItems: "center",
    backgroundColor: "#F8F9FA",
    borderWidth: 1,
    borderColor: "#DEE2E6",
  },
  randomButtonText: { color: "#495057", fontSize: 15, fontWeight: "600" },
});
