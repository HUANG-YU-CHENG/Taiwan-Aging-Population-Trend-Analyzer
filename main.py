import streamlit as st
import geopandas as gpd
import pandas as pd
import plotly.graph_objects as go
import numpy as np
from statsmodels.tsa.arima.model import ARIMA

# 載入台灣的 GeoJSON 數據
@st.cache_data
def load_geojson():
    return gpd.read_file('twCounty2010.geo.json')

# 載入人口數據
@st.cache_data
def load_population_data():
    return pd.read_csv('processed_data/combined_population_data.csv')

# ARIMA 預測函數
def predict_aging_ratio(city_data, steps=5):
    model = ARIMA(city_data['高齡化比例'], order=(1,1,1))
    results = model.fit()
    forecast = results.forecast(steps=steps)
    return forecast

# 載入數據
taiwan_geojson = load_geojson()
population_data = load_population_data()

st.title('Taiwan 高齡人口占比分析與預測')

# 創建地圖更新函數
def update_map(selected_city=None):
    color_values = np.zeros(len(taiwan_geojson))
    if selected_city:
        selected_index = taiwan_geojson[taiwan_geojson['COUNTYNAME'] == selected_city].index
        if not selected_index.empty:
            color_values[selected_index[0]] = 1

    fig = go.Figure(go.Choroplethmapbox(
        geojson=taiwan_geojson.__geo_interface__,
        locations=taiwan_geojson.index,
        z=color_values,
        colorscale=[[0, 'lightblue'], [1, 'blue']],
        marker_opacity=0.7,
        marker_line_width=0.5,
        showscale=False,
        hovertext=taiwan_geojson['COUNTYNAME'],
        hovertemplate='%{hovertext}<extra></extra>'
    ))

    fig.update_layout(
        mapbox_style="carto-positron",
        mapbox_zoom=6,
        mapbox_center={"lat": 23.5, "lon": 121},
        margin={"r":0,"t":0,"l":0,"b":0}
    )

    return fig

# 添加縣市選擇下拉選單
selected_city = st.selectbox("選擇縣市", [''] + population_data['縣市'].unique().tolist())

# 更新並顯示地圖
fig = update_map(selected_city if selected_city else None)
st.plotly_chart(fig, use_container_width=True)

# 如果選擇了縣市，顯示相關數據和預測
if selected_city:
    st.write(f"您選擇了: {selected_city}")
    
    # 獲取選定城市的數據
    city_data = population_data[population_data['縣市'] == selected_city].sort_values('年份')
    
    # 進行預測
    forecast = predict_aging_ratio(city_data)
    last_year = city_data['年份'].max()
    future_years = list(range(last_year + 1, last_year + 6))

    # 創建預測圖表
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=list(city_data['年份']), y=list(city_data['高齡化比例']),
                             mode='lines+markers', name='實際數據'))
    fig.add_trace(go.Scatter(x=future_years, y=list(forecast),
                             mode='lines+markers', name='預測', line=dict(dash='dash')))

    fig.update_layout(title=f'{selected_city}高齡化比例預測',
                      xaxis_title='年份',
                      yaxis_title='高齡化比例 (%)')

    st.plotly_chart(fig)

    # 顯示預測結果
    st.subheader('未來5年預測結果：')
    for year, value in zip(future_years, forecast):
        st.write(f"{year}年: {value:.2f}%")

else:
    st.write('請選擇一個縣市進行預測。')