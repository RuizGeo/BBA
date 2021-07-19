#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May  3 19:33:00 2021

@author: root
"""
import os
import streamlit as st
import pandas as pd
import base64
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import geopandas as gpd
import folium
from streamlit_folium import folium_static
import altair as alt
import rasterio as rio
import plotly.express as px


#Expand page
st.set_page_config(layout="wide")
st.title('Sistema de Monitaramento Ambiental - Itaú BBA')

st.markdown("""Itaú BBA o maior corporate & investment bank da Améria Latina""")

st.sidebar.header('Setup')
selected_values_UF = st.sidebar.radio('UF', ['GO','MT'])
#Load GeoData Frame from shapefile
f_csv_areas = os.getcwd()+'/CSV/taxa_areas_bba.csv'
#Read DataFrame
df_areas_car = pd.read_csv(f_csv_areas,sep=',')
#Rename CAR numbes
CAR_numbers = df_areas_car.matriculas.to_list()
CAR_numbers = [v[:13]for v in CAR_numbers]
#Rename DataFrame
df_areas_car.loc[:,'matriculas'] = CAR_numbers
#CAR numbers selected
CAR_numbers_selected = df_areas_car[df_areas_car.UF == selected_values_UF].matriculas.to_list()

selected_values_CAR = st.sidebar.multiselect('Matrículas', CAR_numbers_selected,CAR_numbers_selected[:3])
#Select CARs
df_selec_CAR = df_areas_car[df_areas_car.matriculas.isin(selected_values_CAR)]
#Plot dataframe
#st.dataframe(df_selec_CAR)
#Area imovel
st.header("Área do imóvel")
#Bar Plot
area_imovel = df_selec_CAR.loc[:,['matriculas','area_imov_vn', 'area_imov_an']]#.plot(kind='bar',rot=0)

fig_area_imov = px.bar(area_imovel, x="matriculas", y=['area_imov_vn', 'area_imov_an'],labels={
                     "value": "Área(%)" ,
                     "matriculas": "Matrículas",
                     'variable':'Uso do solo'},)
var_name= iter(['Vegetação Nativa','Antropizado'])
fig_area_imov.for_each_trace(lambda t: t.update(name=next(var_name)))
colors= iter(['green','#F7E1A0'])
fig_area_imov.for_each_trace(lambda t: t.update(marker_color=next(colors)))
st.plotly_chart(fig_area_imov,use_container_width=True)
#APP
st.header("Área de Preservação Permanente")
#Bar Plot
area_app = df_selec_CAR.loc[:,['matriculas','app_vn', 'app_an']]#.plot(kind='bar',rot=0)
#st.bar_chart(area_app)

#Plotly Reserva legal
fig_app = px.bar(area_app, x="matriculas", y=['app_vn', 'app_an'],labels={
                     "value": "Área(%)" ,
                     "matriculas": "Matrículas",
                     'variable':'Uso do solo'},)
var_name= iter(['Vegetação Nativa','Antropizado'])
fig_app.for_each_trace(lambda t: t.update(name=next(var_name)))
colors= iter(['green','#F7E1A0'])
fig_app.for_each_trace(lambda t: t.update(marker_color=next(colors)))
st.plotly_chart(fig_app,use_container_width=True)

#Reserva Legal
st.header('Reserva Legal')
#Bar Plot
area_rl = df_selec_CAR.loc[:,['matriculas','rl_vn', 'rl_an']]#.plot(kind='bar',rot=0)
#Plotly Reserva legal
fig_rl = px.bar(area_rl, x="matriculas", y=['rl_vn', 'rl_an'],labels={
                     "value": "Área(%)",
                     "matriculas": "Matrículas",
                     'variable':'Uso do solo'},)
var_name= iter(['Vegetação Nativa','Antropizado'])
fig_rl.for_each_trace(lambda t: t.update(name=next(var_name)))
colors= iter(['green','#F7E1A0'])
fig_rl.for_each_trace(lambda t: t.update(marker_color=next(colors)))
st.plotly_chart(fig_rl,use_container_width=True)


####################################
############# MAPs #################
####################################
#Read BR UFs
geo_uf=gpd.read_file(os.getcwd()+'/GeoJson/'+selected_values_UF+'.geojson')
#Get bounds
bounds = geo_uf.bounds.values[0]
long = bounds[0]-((bounds[0]-bounds[2])/2)
lat = bounds[1]-((bounds[1]-bounds[3])/2)
#Init map
#Get TIF files
m = folium.Map(location=[lat,long],zoom_start=6)

#Set UF
folium.GeoJson(geo_uf, name=selected_values_UF).add_to(m)


#List DIr
names_imgs = [f for f in os.listdir(os.getcwd()+'/GeoRaster/'+selected_values_UF) if f.endswith('.tif')]

#Loop images
for name_img in names_imgs:
    #path img
    in_path=os.getcwd()+'/GeoRaster/'+selected_values_UF+os.sep+name_img
    #Get name layer 13 caracter
    
    with rio.open(in_path) as src: 
        img = src.read()       
        src_crs = src.crs['init'].upper()
        min_lon, min_lat, max_lon, max_lat = src.bounds
    #Remove nodata
    #nodata = src.nodata  
    #img[img==nodata] = np.nan
        
    ## Get bounds
    bounds_orig = [[min_lat, min_lon], [max_lat, max_lon]]
    # Finding the centre latitude & longitude    
    centre_lon = bounds_orig[0][1] + (bounds_orig[1][1] - bounds_orig[0][1])/2
    centre_lat = bounds_orig[0][0] + (bounds_orig[1][0] - bounds_orig[0][0])/2
    #CReate Marker
    folium.Marker( [centre_lat, centre_lon],popup=name_img[:13]).add_to(m)
    
    
    
    # Overlay raster using add_child() function
    m.add_child(folium.raster_layers.ImageOverlay(img.transpose(1, 2, 0), opacity=.7, name=name_img[:13],
                                     bounds = bounds_orig))
    
#Set Google Sattelite    
basemaps = {
    'Google Satellite Hybrid': folium.TileLayer(
        tiles = 'https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}',
        attr = 'Google',
        name = 'Google Satellite',
        overlay = True,
        control = True
    )}

# Display map 
basemaps['Google Satellite Hybrid'].add_to(m)
folium.LayerControl().add_to(m)

folium_static(m,width=1200, height=500)




        
