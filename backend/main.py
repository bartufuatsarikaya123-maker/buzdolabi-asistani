from fastapi import Request
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import random
import os
from pathlib import Path
from dotenv import load_dotenv
import google.generativeai as genai
import requests
from fastapi import Query
from fastapi.middleware.cors import CORSMiddleware



load_dotenv(dotenv_path=Path(__file__).resolve().parent / ".env")

API_KEY = os.getenv("GEMINI_API_KEY")
print("ANAHTAR DURUMU:", "BAŞARILI (OKUNDU)" if API_KEY else "BULUNAMADI!")

if not API_KEY:
    raise RuntimeError("GEMINI_API_KEY bulunamadı.")

genai.configure(api_key=API_KEY)

available_models = []
for m in genai.list_models():
    if "generateContent" in getattr(m, "supported_generation_methods", []):
        available_models.append(m.name)

print("--- KULLANILABİLİR MODELLER ---")
for name in available_models:
    print(name)
print("-------------------------------")

preferred_models = [
    "models/gemini-3.6-flash",
    "gemini-3.6-flash",
    "models/gemini-2.5-flash",
    "gemini-2.5-flash",
]

MODEL_NAME = next(
    (name for name in preferred_models if name in available_models),
    available_models[0] if available_models else "gemini-3.6-flash",
)

model = genai.GenerativeModel(MODEL_NAME)



app = FastAPI(title="Buzdolabı Asistanı API")


# app = FastAPI(...) satırın zaten var, hemen altına şunu yapıştır:

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Geliştirme aşamasında olduğun için tüm adreslerden gelen isteklere kapıyı açar
    allow_credentials=True,
    allow_methods=["*"],  # GET, POST gibi tüm metodlara izin verir
    allow_headers=["*"],
)

# ...existing code...


# Uygulamadan gelecek malzeme listesinin yapısı
class RecipeRequest(BaseModel):
    ingredients: list[str]

@app.post("/get-recipe")
def generate_recipe(request: RecipeRequest):
    ingredients = request.ingredients
    
    if not ingredients:
        return {"recipe_suggestion": "Dolabında hiç malzeme yok!"}

    # Malzemeleri aralarına virgül koyarak bir metne dönüştür
    ingredients_text = ", ".join(ingredients)
    
    # GÜNCELLENMİŞ KORUMALI PROMPT (Guardrail)
    prompt = f"""
    Sen profesyonel ve kibar bir mutfak asistanısın.
    Kullanıcının dolabında şu malzemeler olduğu belirtilmiş: {ingredients_text}.
    
    ÖNEMLİ GÜVENLİK VE FİLTRE KURALLARI:
    1. Gelen listedeki kelimeleri incele. Yiyecek/içecek olmayan, 'asd', 'qwe' gibi anlamsız harf yığınlarını veya argo/küfür içeren kelimeleri KESİNLİKLE görmezden gel.
    2. Eğer bu saçma veya alakasız kelimeleri elediğinde elinde yemeğe katılabilecek geçerli HİÇBİR malzeme kalmıyorsa, tarif üretme. Sadece şu cümleyi döndür: "Lütfen dolabınızdaki gerçek ve yenilebilir malzemeleri seçtiğinizden emin olun."
    3. Eğer elinde geçerli yiyecekler kalırsa, sadece bu geçerli yiyecekleri (ve tuz, yağ gibi temel kiler ürünlerini) kullanarak pratik 1 adet tarif öner.
    
    Lütfen cevabını tam olarak şu formatta ver (Eğer geçerli malzeme yoksa bu formatı kullanma, sadece yukarıdaki uyarı cümlesini yaz):
    
    TARİF ADI: [Yemeğin Adı]
    
    TAHMİNİ TOPLAM KALORİ: [Örn: 450 kcal]
    TAHMİNİ PROTEİN: [Örn: 25g]
    TAHMİNİ KARBONHİDRAT: [Örn: 15g]
    TAHMİNİ YAĞ: [Örn: 20g]
    
    YAPILIŞI:
    - [Adım 1]
    - [Adım 2]
    ...
    """
    
    try:
        response = model.generate_content(prompt)
        text_response = response.text
        
        # Eğer Gemini sadece uyarı cümlesini döndürdüyse (malzeme bulamadıysa), makro aramadan direkt döndür
        if "gerçek ve yenilebilir malzemeleri" in text_response:
            return {
                "nutrients": {"calories": "-", "protein": "-", "carbs": "-", "fat": "-"},
                "recipe_suggestion": text_response
            }
        
        # Geçerli bir tarif geldiyse makro değerleri parçala
        calories = "0"
        protein = "0"
        carbs = "0"
        fat = "0"
        
        for line in text_response.split('\n'):
            if "TAHMİNİ TOPLAM KALORİ:" in line: calories = line.split(":")[1].strip().replace("kcal","").strip()
            if "TAHMİNİ PROTEİN:" in line: protein = line.split(":")[1].strip().replace("g","").strip()
            if "TAHMİNİ KARBONHİDRAT:" in line: carbs = line.split(":")[1].strip().replace("g","").strip()
            if "TAHMİNİ YAĞ:" in line: fat = line.split(":")[1].strip().replace("g","").strip()
            
        return {
            "nutrients": {
                "calories": calories,
                "protein": protein,
                "carbs": carbs,
                "fat": fat
            },
            "recipe_suggestion": text_response
        }
    except Exception as e:
        print(f"Hata: {e}")
        return {"recipe_suggestion": "Sistemde bir hata oluştu."}

@app.post("/random-recipe")
def generate_random_recipe(request: RecipeRequest):
    import random
    available_keys = request.ingredients
    if not available_keys:
        return {"recipe_suggestion": "Dolabında hiç malzeme yok!"}
    
    sample_size = min(3, len(available_keys))
    random_keys = random.sample(available_keys, sample_size)
    return generate_recipe(RecipeRequest(ingredients=random_keys))

@app.get("/test-gemini")
def test_api():
    try:
        response = model.generate_content("Merhaba, bana sadece 2 kelime ile 'Bağlantı başarılı' yaz.")
        return {"mesaj": response.text}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Gemini API hatası: {exc}")

        
YEREL_VERITABANI = [
    # --- ET, TAVUK VE BALIK ---
    {"key": "loc_1", "name": "Biftek", "calories": 250, "protein": 26, "carbs": 0, "fat": 15},
    {"key": "loc_2", "name": "Tavuk Göğsü", "calories": 165, "protein": 31, "carbs": 0, "fat": 3.6},
    {"key": "loc_3", "name": "Dana Kıyma", "calories": 250, "protein": 26, "carbs": 0, "fat": 15},
    {"key": "loc_4", "name": "Kuzu Kuşbaşı", "calories": 294, "protein": 25, "carbs": 0, "fat": 21},
    {"key": "loc_5", "name": "Sucuk", "calories": 330, "protein": 14, "carbs": 1.5, "fat": 30},
    {"key": "loc_6", "name": "Sosis", "calories": 300, "protein": 12, "carbs": 2, "fat": 27},
    {"key": "loc_7", "name": "Ton Balığı (Konserve)", "calories": 116, "protein": 26, "carbs": 0, "fat": 1},
    
    # --- KAHVALTILIK VE SÜT ÜRÜNLERİ ---
    {"key": "loc_8", "name": "Yumurta (1 Adet)", "calories": 78, "protein": 6, "carbs": 0.6, "fat": 5},
    {"key": "loc_9", "name": "Beyaz Peynir", "calories": 264, "protein": 14, "carbs": 1.2, "fat": 22},
    {"key": "loc_10", "name": "Kaşar Peyniri", "calories": 402, "protein": 25, "carbs": 2, "fat": 33},
    {"key": "loc_11", "name": "Süt", "calories": 45, "protein": 3.4, "carbs": 4.8, "fat": 1.5},
    {"key": "loc_12", "name": "Yoğurt", "calories": 61, "protein": 3.5, "carbs": 4.7, "fat": 3.3},
    {"key": "loc_13", "name": "Tereyağı", "calories": 717, "protein": 0.9, "carbs": 0.1, "fat": 81},
    {"key": "loc_14", "name": "Siyah Zeytin", "calories": 115, "protein": 0.8, "carbs": 6, "fat": 10},
    
    # --- SEBZELER ---
    {"key": "loc_15", "name": "Domates", "calories": 18, "protein": 0.9, "carbs": 3.9, "fat": 0.2},
    {"key": "loc_16", "name": "Salatalık", "calories": 15, "protein": 0.6, "carbs": 3.6, "fat": 0.1},
    {"key": "loc_17", "name": "Kuru Soğan", "calories": 40, "protein": 1.1, "carbs": 9, "fat": 0.1},
    {"key": "loc_18", "name": "Sarımsak", "calories": 149, "protein": 6.4, "carbs": 33, "fat": 0.5},
    {"key": "loc_19", "name": "Patates", "calories": 77, "protein": 2, "carbs": 17, "fat": 0.1},
    {"key": "loc_20", "name": "Yeşil Biber", "calories": 20, "protein": 0.9, "carbs": 4.6, "fat": 0.2},
    {"key": "loc_21", "name": "Kapya Biber", "calories": 26, "protein": 1, "carbs": 6, "fat": 0.3},
    {"key": "loc_22", "name": "Patlıcan", "calories": 25, "protein": 1, "carbs": 6, "fat": 0.2},
    {"key": "loc_23", "name": "Kabak", "calories": 17, "protein": 1.2, "carbs": 3.1, "fat": 0.3},
    {"key": "loc_24", "name": "Havuç", "calories": 41, "protein": 0.9, "carbs": 10, "fat": 0.2},
    {"key": "loc_25", "name": "Limon", "calories": 29, "protein": 1.1, "carbs": 9, "fat": 0.3},
    {"key": "loc_26", "name": "Mantar", "calories": 22, "protein": 3.1, "carbs": 3.3, "fat": 0.3},

    # --- KİLER VE BAKLİYAT ---
    {"key": "loc_27", "name": "Pirinç", "calories": 130, "protein": 2.7, "carbs": 28, "fat": 0.3},
    {"key": "loc_28", "name": "Bulgur", "calories": 342, "protein": 12.3, "carbs": 76, "fat": 1.3},
    {"key": "loc_29", "name": "Makarna", "calories": 131, "protein": 5, "carbs": 25, "fat": 1.1},
    {"key": "loc_30", "name": "Kırmızı Mercimek", "calories": 353, "protein": 25, "carbs": 60, "fat": 1.1},
    {"key": "loc_31", "name": "Nohut", "calories": 364, "protein": 19, "carbs": 61, "fat": 6},
    {"key": "loc_32", "name": "Domates Salçası", "calories": 82, "protein": 4.3, "carbs": 19, "fat": 0.5},
    {"key": "loc_33", "name": "Zeytinyağı (1 Y.Kaşığı)", "calories": 119, "protein": 0, "carbs": 0, "fat": 13.5},
    {"key": "loc_34", "name": "Yulaf Ezmesi", "calories": 389, "protein": 16.9, "carbs": 66, "fat": 6.9},
    
    # --- MEYVELER ---
    {"key": "loc_35", "name": "Elma", "calories": 52, "protein": 0.3, "carbs": 14, "fat": 0.2},
    {"key": "loc_36", "name": "Muz", "calories": 89, "protein": 1.1, "carbs": 23, "fat": 0.3}
]

@app.get("/search-food")
def search_food(query: str = Query(..., min_length=2)):
    results = []
    
    # 1. YEREL VERİTABANINDA ARAMA
    search_term = query.lower().replace("ı", "i").replace("i̇", "i").replace("I", "ı").replace("İ", "i")
    
    for item in YEREL_VERITABANI:
        item_name_lower = item["name"].lower().replace("ı", "i").replace("i̇", "i").replace("I", "ı").replace("İ", "i")
        if search_term in item_name_lower:
            results.append(item)

    # 2. AKILLI GEÇİŞ (SMART FALLBACK) 
    if len(results) == 0:
        url = f"https://world.openfoodfacts.org/cgi/search.pl?search_terms={query}&search_simple=1&action=process&json=1&page_size=5"
        headers = {
            "User-Agent": "BuzdolabiAsistaniApp/1.0 (StudentProject - TEKNOFEST)"
        }
        
        try:
            response = requests.get(url, headers=headers, timeout=8)
            data = response.json()
            
            for product in data.get("products", []):
                nutriments = product.get("nutriments", {})
                product_name = product.get("product_name")
                
                if product_name and isinstance(product_name, str) and len(product_name.strip()) > 0:
                    results.append({
                        "key": str(product.get("code", f"ext_{product_name}")), 
                        "name": product_name,
                        "calories": round(nutriments.get("energy-kcal_100g", nutriments.get("energy_100g", 0)), 1),
                        "protein": round(nutriments.get("proteins_100g", 0), 1),
                        "carbs": round(nutriments.get("carbohydrates_100g", 0), 1),
                        "fat": round(nutriments.get("fat_100g", 0), 1)
                    })
        except Exception as e:
            print(f"Dış API Hatası: {e}") 
            
    # BU SATIRIN YERİ ÇOK KRİTİK: if veya try bloğunun içinde DEĞİL, en dışta olmalı!
    return {"success": True, "results": results}
