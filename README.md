# AutoSales-Analyzer

**Analyze the Chinese Automotive Market**  
This project scrapes sales rankings and technical specifications of vehicles from [Dongchedi](https://www.dongchedi.com/) to provide deep insights into market trends, brand performance, and price distributions.

---

## Overview
This script automates the collection of vehicle data, combining sales popularity with detailed parameters (Energy Type, Manufacturer, Level). It then performs data analysis to visualize the competitive landscape of the current auto market.

## Features
- ** Web Crawler**: Fetches sales data and detailed car parameters (Price, Energy Type, Manufacturer).
- ** Data Analysis**: Calculates average prices, identifies top-selling models, and analyzes energy type distribution (Gas, EV, Hybrid).
- ** Visualization**:
  - **Pie Chart**: Market share by brand.
  - **Bar Chart**: Top 10 best-selling car models.
  - **Histogram**: Sales volume distribution across different price ranges.
  - **Word Cloud**: Visual representation of car series names based on sales frequency.

##  Data Structure
The script generates two primary datasets:
1. **Sales Data**: Contains Brand, Series, Price, and Sales Volume.
2. **Parameter Info**: Contains Level, Manufacturer, Energy Type, and Launch Date.

##  How to Run

### 1. Prerequisites
Ensure you have Python 3.10/3.8 installed.

### 2. Install Dependencies
```bash
pip install pandas matplotlib requests beautifulsoup4 wordcloud lxml
