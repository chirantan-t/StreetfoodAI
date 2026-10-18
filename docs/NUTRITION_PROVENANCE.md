# StreetFoodAI: Nutrition Data Provenance & Methodology

## 1. Scientific Data Source

The nutritional database for StreetFoodAI is established upon:

* **Primary Reference:** *Indian Food Composition Tables (IFCT 2017)*, published by the **National Institute of Nutrition (NIN)**, Indian Council of Medical Research (ICMR), Department of Health Research, Ministry of Health and Family Welfare, Government of India.
* **Supplementary Guidelines:** *Dietary Guidelines for Indians (ICMR-NIN 2024)* and *Food Safety and Standards Authority of India (FSSAI) Eat Right India Cooked Food Database*.

---

## 2. Food Class Nutritional Matrix & NIN IFCT Codes

| Food Name | Serving Type | Est. Mass (g) | Energy (kcal) | Protein (g) | Carbs (g) | Fat (g) | Fiber (g) | Key IFCT Raw Food Codes |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **Vada Pav** | Regular (1 pc) | 135 | 305 | 6.3 | 45.8 | 11.2 | 3.2 | Potato (C001), Wheat bread (B001), Besan (B003) |
| **Pav Bhaji** | Regular (plate) | 320 | 550 | 11.0 | 76.0 | 23.0 | 8.1 | Potato (C001), Tomato (D067), Butter (H001) |
| **Misal Pav** | Regular (plate) | 380 | 520 | 17.5 | 78.0 | 16.5 | 10.2 | Sprouted Moth Beans (B014), Farsan/Sev |
| **Pani Puri** | Regular (6 pcs) | 180 | 210 | 4.5 | 38.5 | 4.8 | 3.4 | Semolina puri (B001), Mint herbs, Tamarind (F026) |
| **Bhel Puri** | Regular (plate) | 190 | 270 | 6.1 | 49.5 | 6.0 | 4.2 | Puffed Rice (A007), Chickpea Sev, Peanuts (D002) |
| **Sev Puri** | Regular (6 pcs) | 200 | 320 | 7.0 | 46.0 | 12.5 | 3.8 | Papdi, Fried Sev, Potatoes, Chutneys |
| **Dabeli** | Regular (1 pc) | 160 | 350 | 7.5 | 54.0 | 12.0 | 4.2 | Pav bread, Potato, Roasted Peanuts (D002) |
| **Samosa** | Regular (1 pc) | 110 | 290 | 5.1 | 34.5 | 15.0 | 2.9 | Maida (B002), Potato (C001), Oil uptake ~14% |
| **Kachori** | Regular (1 pc) | 100 | 310 | 7.0 | 35.0 | 16.5 | 3.2 | Moong Dal (B011), Maida (B002), Vegetable Oil |
| **Dosa** | Regular (1 crepe) | 220 | 300 | 7.5 | 50.0 | 8.0 | 3.5 | Rice (A001), Black gram dal (B009) |
| **Idli** | Regular (2 pcs) | 130 | 170 | 5.8 | 35.5 | 0.8 | 2.3 | Rice (A001), Black gram dal (B009) |
| **Medu Vada** | Regular (2 pcs) | 115 | 270 | 10.2 | 29.5 | 12.8 | 4.2 | Urad Dal (B009), Black Pepper, Deep-fry oil |
| **Poha** | Regular (plate) | 200 | 275 | 6.4 | 47.0 | 7.5 | 3.6 | Rice flakes (A006), Peanut (D002), Turmeric |
| **Upma** | Regular (plate) | 220 | 270 | 6.3 | 48.0 | 6.5 | 3.0 | Semolina/Suji (B003), Ghee/Oil, Mustard |
| **Chole Bhature**| Regular (plate) | 420 | 780 | 22.0 | 102.0 | 33.0 | 11.2 | Kabuli Chana (B006), Maida (B002) |
| **Aloo Tikki** | Regular (2 pcs) | 200 | 310 | 6.2 | 48.0 | 11.0 | 4.0 | Potato (C001), Curd (G001), Tamarind (F026) |
| **Frankie** | Regular (1 roll) | 210 | 350 | 9.5 | 54.0 | 11.2 | 4.8 | Flatbread (B001), Potato/Paneer cutlet |
| **Sandwich** | Regular (Bombay) | 210 | 315 | 7.2 | 49.0 | 10.5 | 4.5 | Bread (B001), Butter (H001), Salad Vegetables |
| **Jalebi** | Regular (100g) | 100 | 350 | 2.8 | 68.0 | 8.0 | 0.5 | Maida, Sucrose sugar syrup (F001), Ghee/Oil |
| **Other / Unknown**| N/A | Withheld | Withheld | Withheld | Withheld | Withheld | Withheld | Values withheld to prevent erroneous dietary logging |

---

## 3. Serving Size Scaling & Proportionality

Nutritional estimates are scaled across three configurations:
* **Small:** Configured reduction factor (typically 0.65x - 0.70x) based on single-piece or half-plate street servings.
* **Regular:** Baseline standardized vendor portion (1.0x).
* **Large:** Extended plate or double-piece portions (typically 1.40x - 1.50x).

When custom gram weights are provided, macronutrients scale proportionally:
$$M_{\text{custom}} = M_{\text{regular}} \times \left(\frac{W_{\text{target}}}{W_{\text{regular}}}\right)$$

---

## 4. Vendor Recipe Variance & Uncertainty Disclaimers

### Deep-Frying Oil Absorption
Oil absorption during deep frying of chickpea batter (besan) in snacks like Vada Pav, Samosa, and Kachori fluctuates between 8% and 18% of total item weight depending on oil frying temperature (optimal 175°C-185°C vs sub-optimal <160°C).

### Table Butter and Finishing Ghee
Street vendors frequently add between 15g to 45g of additional table butter during griddle finishing for dishes like Pav Bhaji and Bombay Sandwiches, introducing a ±25% caloric variance over standardized recipes.

### Direct Pixel Mass Disclaimer
StreetFoodAI explicitly disclaims inferring exact mass or caloric count directly from 2D pixel projections without 3D volumetric reconstruction and fiducial scale markers. All displayed nutritional metrics are documented statistical estimates.
