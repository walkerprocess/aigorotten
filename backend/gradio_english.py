import requests
import gradio as gr
from datetime import datetime, timedelta
import pandas as pd
from functools import lru_cache
import concurrent.futures
from typing import Dict, List, Tuple

fruit_count = {}
price_dict = {}
image_read = []

# Global variables for cache
CACHE_TIMEOUT = 3600  # 1 hour
last_cache_refresh = datetime.now()
price_cache = {}

# Translation dictionaries
REGION_TRANSLATIONS = {
    '서울': 'Seoul',
    '부산': 'Busan',
    '대구': 'Daegu',
    '광주': 'Gwangju',
    '대전': 'Daejeon'
}

PRODUCT_TRANSLATIONS = {
    '사과': 'Apple',
    '바나나': 'Banana',
    '당근': 'Carrot',
    '오이': 'Cucumber',
    '망고': 'Mango',
    '파프리카': 'Bell Pepper',
    '오렌지': 'Orange',
    '감자': 'Potato',
    '딸기': 'Strawberry',
    '토마토': 'Tomato'
}

def get_date_range():
    """Calculate date range for reusability"""
    now = datetime.now()
    today = now.strftime("%Y-%m-%d")
    yesterday = (now - timedelta(days=1)).strftime("%Y-%m-%d")
    before_yesterday = (now - timedelta(days=2)).strftime("%Y-%m-%d")
    
    if now.hour > 14:
        return today, yesterday
    return yesterday, before_yesterday

@lru_cache(maxsize=32)
def get_api_configs() -> Dict:
    """Cache API configuration for reuse"""
    return {
        'category_dict': {'apple': '400', 'banana': '400', 'carrot': '200', 'cucumber': '200', 
                         'mango': '400', 'bellpepper': '200', 'orange': '400', 'potato': '100', 
                         'strawberry': '200', 'tomato': '200'},
        'fruit_code_dict': {'apple': '411', 'banana': '418', 'carrot': '232', 'cucumber': '223',
                           'mango': '428', 'bellpepper': '256', 'orange': '421', 'potato': '152',
                           'strawberry': '226', 'tomato': '225'},
        'kind_code_dict': {'apple': '05', 'banana': '02', 'carrot': '01', 'cucumber': '02',
                          'mango': '00', 'bellpepper': '00', 'orange': '03', 'potato': '01',
                          'strawberry': '00', 'tomato': '00'},
        'unit_fruit_dict': {'apple': '10kg', 'banana': '13kg', 'carrot': '20kg', 'cucumber': '100pcs',
                           'mango': '5kg', 'bellpepper': '5kg', 'orange': '18kg', 'potato': '20kg',
                           'strawberry': '2kg', 'tomato': '5kg'}
    }

def fruits_status(prediction: str) -> Tuple[str, str]:
    """Check fruit status"""
    name, status = prediction.split('_')
    return name, status

@lru_cache(maxsize=100)
def get_fruit_price(fruits_name: str, start_date: str, end_date: str) -> requests.Response:
    """Cache API calls to prevent duplicate requests"""
    api_configs = get_api_configs()
    
    api_url = "http://www.kamis.or.kr/service/price/xml.do?action=periodWholesaleProductList"
    api_key = #key
    
    params = {
        'p_cert_key': api_key,
        'p_cert_id': '5318',
        'p_returntype': 'json',
        'p_startday': start_date,
        'p_endday': end_date,
        'p_itemcategorycode': api_configs['category_dict'][fruits_name],
        'p_itemcode': api_configs['fruit_code_dict'][fruits_name],
        'p_kindcode': api_configs['kind_code_dict'][fruits_name],
        'p_productrankcode': '05'
    }
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': api_key
    }
    
    return requests.post(api_url, headers=headers, params=params)

def calculate_prices(price_data: List, fruits_status: str, fruits_name: str) -> pd.DataFrame:
    """Optimize price calculation logic with English translations"""
    api_configs = get_api_configs()
    columns = ['Product', 'Condition', 'Region', 'Wholesale Price', 'Unit']
    df = pd.DataFrame(columns=columns)
    
    for i in range(5):
        price = float(price_data[i]['price'].replace(',', ''))
        if fruits_status == 'low':
            price = float(f"{price * 0.6}")

        formatted_price = f"{price:,.0f}"
        
        # Translate region and product names to English
        region_kr = price_data[i]['countyname']
        region_en = REGION_TRANSLATIONS.get(region_kr, region_kr)  # Fallback to Korean if translation not found
        
        product_kr = price_data[i]['itemname']
        product_en = PRODUCT_TRANSLATIONS.get(product_kr, product_kr)  # Fallback to Korean if translation not found
        
        df.loc[i] = [
            product_en,
            fruits_status.upper(),
            region_en,
            formatted_price,
            api_configs['unit_fruit_dict'][fruits_name]
        ]
        
    return df

def fruits_price(fruits_name: str, fruits_status: str, start_date: str, end_date: str) -> pd.DataFrame:
    """Optimize price information retrieval"""
    global price_cache, last_cache_refresh
    
    if (datetime.now() - last_cache_refresh).seconds > CACHE_TIMEOUT:
        price_cache.clear()
        last_cache_refresh = datetime.now()
    
    cache_key = f"{fruits_name}_{start_date}_{end_date}"
    if cache_key in price_cache:
        data = price_cache[cache_key]
    else:
        response = get_fruit_price(fruits_name, start_date, end_date)
        data = response.json()
        price_cache[cache_key] = data
    
    price_data = data['data']['item'][5:14:2]
    return calculate_prices(price_data, fruits_status, fruits_name)



def predict_image(image_data):
    """Optimize image prediction function"""
    endpoint = #endpoint
    prediction_key = #key
    project_id = #project_id
    model_name = #model_name
    
    url = f"{endpoint}/customvision/v3.0/Prediction/{project_id}/classify/iterations/{model_name}/image"
    
    headers = {
        'Prediction-Key': prediction_key,
        'Content-Type': 'application/octet-stream'
    }
    
    try:
        with requests.Session() as session:
            response = session.post(url, headers=headers, data=image_data)
            response.raise_for_status()
            predictions = response.json()['predictions']
            top_prediction = max(predictions, key=lambda x: x['probability'])
        
        return top_prediction['tagName']
    
    except Exception as e:
        return f"Error: {str(e)}"

def fruit_detective(image: bytes) -> Tuple[Dict, pd.DataFrame]:
    """Optimize fruit detection function"""
    prediction = predict_image(image)
    fruit_name, fruit_status = fruits_status(prediction)
    
    product_english = {
        'apple': 'Apple', 'banana': 'Banana', 'carrot': 'Carrot', 'cucumber': 'Cucumber',
        'mango': 'Mango', 'bellpepper': 'Bell Pepper', 'orange': 'Orange', 'potato': 'Potato',
        'strawberry': 'Strawberry', 'tomato': 'Tomato'
    }

    condition_icons = {'fr': '🟢 Fresh', 'low': '🟠 Low Quality', 'rot': '🔴 Poor'}

    fruit_count[prediction] = fruit_count.get(prediction, 0) + 1
    count_data = [
        {
            "Product": product_english[k.split('_')[0]],
            "Quality": condition_icons[k.split('_')[1]],
            "Count": v
        }
        for k, v in fruit_count.items()
    ]
    
    if fruit_status.lower() in ('fr', 'low'):
        price_dict[prediction] = True
    
    return price_dict, pd.DataFrame(count_data)

def upload_to_do(image: str, price_dataframes_state: List) -> Tuple:
    """Optimize upload processing function"""
    today_date, yesterday_date = get_date_range()
    
    with open(image, "rb") as img_file:
        image_bytes = img_file.read()
        price_dict, count_df = fruit_detective(image_bytes)
        image_read.append(image)
    
    def process_fruit(key):
        fruit_name, fruit_status = key.split('_')
        return fruits_price(fruit_name, fruit_status, yesterday_date, today_date)
    
    all_dfs = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(process_fruit, key) for key in price_dict]
        all_dfs = [future.result() for future in concurrent.futures.as_completed(futures)]
    
    combined_df = pd.concat(all_dfs, ignore_index=True) if all_dfs else pd.DataFrame()
    
    return image_read, all_dfs, count_df, combined_df

# Gradio interface setup
with gr.Blocks() as demo_en:
    gr.Markdown("# 🍎 Fresh Fruits, Convenient Storage! 🍎")
    gr.Markdown("## Once you upload the picture, it will automatically sort out and print the correlating price data.")

    
    price_dataframes = gr.State([])
    
    with gr.Row(height=350):
        image_upload = gr.Image(type="filepath", height=300)
        count_df = gr.Dataframe()
    
    with gr.Row(height=500):
        combined_price_df = gr.Dataframe()
    
    with gr.Row(height=1000):
        output_img_store = gr.Gallery(label='Fruits/Vegetables that have been inputted', columns=10)
    
    image_upload.upload(
        fn=upload_to_do,
        inputs=[image_upload, price_dataframes],
        outputs=[output_img_store, price_dataframes, count_df, combined_price_df]
    )

# 실행 코드 제거 -> FastAPI에서 import 해서 사용
#   if __name__ == \"__main__\":\n",
#       demo.launch()"
