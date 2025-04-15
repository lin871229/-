
import streamlit as st
import pandas as pd
import random

st.set_page_config(page_title="機構抽籤系統", layout="wide")
st.title("🏠 特約機構抽籤系統")

# 上傳 Excel 檔案
uploaded_file = st.file_uploader("請上傳特約機構名冊 Excel 檔案", type=["xlsx"])

if uploaded_file:
    xls = pd.ExcelFile(uploaded_file)
    sheet_name = "本市113年7月1日起特約居家式長照機構名冊"
    df_raw = xls.parse(sheet_name)

    # 清理資料：跳過前兩列標題與說明，重新命名欄位
    df = df_raw.iloc[2:].copy()
    df.columns = [
        "編號", "備註", "單位名稱", "設立區域", "地址", "電話", "Email",
        "長照服務項目", "居家服務履約區域", "居家喘息服務履約區域",
        "短照喘息履約區域", "服務時段", "承辦人員"
    ]

    # 擷取所有出現過的區域
    area_cols = ["居家喘息服務履約區域", "短照喘息履約區域"]
    all_area_texts = df[area_cols[0]].fillna('') + '\n' + df[area_cols[1]].fillna('')
    split_texts = all_area_texts.str.split('[、，\n()（）]')
    all_areas = set()
    for lst in split_texts:
        all_areas.update([a.strip() for a in lst if a and "區" in a and len(a.strip()) <= 5])
    area_options = sorted(all_areas)

    # 側邊欄選擇區域
    st.sidebar.header("🎯 篩選條件")
    selected_area = st.sidebar.selectbox("選擇區域名稱：", area_options)
    num_to_draw = st.sidebar.number_input("抽出幾間機構：", min_value=1, max_value=20, value=3)

    # 進行篩選（兩欄皆可）
    df_match1 = df[df["居家喘息服務履約區域"].fillna('').str.contains(selected_area)]
    df_match2 = df[df["短照喘息履約區域"].fillna('').str.contains(selected_area)]
    combined_df = pd.concat([df_match1, df_match2]).drop_duplicates(subset="單位名稱")

    st.markdown(f"### ✅ 履約區域包含 `{selected_area}` 的機構，共 {len(combined_df)} 間")

    if len(combined_df) > 0:
        sample_n = min(num_to_draw, len(combined_df))
        sampled_df = combined_df.sample(n=sample_n, random_state=random.randint(1,9999))
        st.dataframe(sampled_df[["單位名稱", "設立區域", "地址", "電話"]].reset_index(drop=True))
    else:
        st.warning("找不到符合條件的機構。")
else:
    st.info("請先上傳 Excel 檔案。")
