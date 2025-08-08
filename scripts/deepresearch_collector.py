#!/usr/bin/env python3
"""
DeepResearch School Data Collector

This script collects school data from all prefectures in Japan using the DeepResearch API.
For each prefecture, it searches for all high schools and collects:
- 偏差値 (Hensachi/Deviation Value)
- 学是 (School Philosophy)
- 進学実績 (Academic Achievement Records)
- 入試情報 (Entrance Exam Information)
- オープンキャンパス情報 (Open Campus Information)
- 公式画像URL (Official Image URLs)

The collected data is saved to JSON files under db/schools/ directory.
"""

import os
import json
import time
import logging
from datetime import datetime
from typing import Dict, List, Optional
import requests
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('deepresearch_collector.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class DeepResearchCollector:
    """Collects school data using DeepResearch API"""
    
    def __init__(self):
        self.api_key = os.getenv('DEEPRESEARCH_API_KEY')
        self.base_url = os.getenv('DEEPRESEARCH_BASE_URL', 'https://api.deepresearch.com/v1')
        self.output_dir = Path('db/schools')
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.prefectures = [
            "北海道", "青森県", "岩手県", "宮城県", "秋田県", "山形県", "福島県",
            "茨城県", "栃木県", "群馬県", "埼玉県", "千葉県", "東京都", "神奈川県",
            "新潟県", "富山県", "石川県", "福井県", "山梨県", "長野県", "岐阜県",
            "静岡県", "愛知県", "三重県", "滋賀県", "京都府", "大阪府", "兵庫県",
            "奈良県", "和歌山県", "鳥取県", "島根県", "岡山県", "広島県", "山口県",
            "徳島県", "香川県", "愛媛県", "高知県", "福岡県", "佐賀県", "長崎県",
            "熊本県", "大分県", "宮崎県", "鹿児島県", "沖縄県"
        ]
        
    def _make_api_request(self, endpoint: str, params: Dict) -> Optional[Dict]:
        """Make API request to DeepResearch"""
        if not self.api_key:
            logger.warning("DeepResearch API key not found. Using placeholder data.")
            return self._generate_placeholder_data(params)
        
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            response = requests.get(
                f"{self.base_url}/{endpoint}",
                headers=headers,
                params=params,
                timeout=30
            )
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            return None
    
    def _generate_placeholder_data(self, params: Dict) -> Dict:
        """Generate placeholder data when API is not available"""
        prefecture = params.get('prefecture', '東京都')
        
        schools = []
        school_types = ['県立', '私立', '国立']
        
        for i in range(5):  # Generate 5 sample schools per prefecture
            school_name = f"{prefecture.replace('県', '').replace('都', '').replace('府', '')}{school_types[i % 3]}{chr(65 + i)}高等学校"
            
            school_data = {
                "name": school_name,
                "prefecture": prefecture,
                "type": school_types[i % 3],
                "hensachi": 50 + (i * 5) + (hash(school_name) % 20),
                "philosophy": f"{school_name}は、生徒一人ひとりの個性を大切にし、確かな学力と豊かな人間性を育む教育を実践しています。",
                "academic_records": {
                    "university_advancement_rate": 85 + (i * 2),
                    "notable_universities": ["東京大学", "早稲田大学", "慶應義塾大学", "明治大学"],
                    "recent_achievements": f"令和{4+i}年度大学合格実績: 国公立大学{20+i*3}名、私立大学{50+i*10}名"
                },
                "entrance_exam_info": {
                    "exam_date": f"令和6年{2+i}月{10+i}日",
                    "subjects": ["国語", "数学", "英語", "理科", "社会"],
                    "application_period": f"令和5年12月{1+i}日～12月{15+i}日",
                    "capacity": 200 + (i * 40)
                },
                "open_campus": {
                    "dates": [f"令和5年{7+i}月{15+i*2}日", f"令和5年{8+i}月{20+i*3}日"],
                    "programs": ["学校説明会", "授業体験", "部活動見学", "個別相談"],
                    "registration_required": True
                },
                "official_images": [
                    f"https://example.com/schools/{prefecture}/{school_name}/main.jpg",
                    f"https://example.com/schools/{prefecture}/{school_name}/campus.jpg",
                    f"https://example.com/schools/{prefecture}/{school_name}/facilities.jpg"
                ],
                "contact_info": {
                    "address": f"{prefecture}○○市○○町1-2-3",
                    "phone": f"0{3+i}-{1000+i*100}-{2000+i*200}",
                    "website": f"https://www.{school_name.replace('高等学校', '')}.ed.jp",
                    "email": f"info@{school_name.replace('高等学校', '')}.ed.jp"
                },
                "last_updated": datetime.now().isoformat()
            }
            schools.append(school_data)
        
        return {
            "prefecture": prefecture,
            "total_schools": len(schools),
            "schools": schools,
            "collection_date": datetime.now().isoformat(),
            "data_source": "placeholder" if not self.api_key else "deepresearch_api"
        }
    
    def collect_prefecture_data(self, prefecture: str) -> Optional[Dict]:
        """Collect all high school data for a specific prefecture"""
        logger.info(f"Collecting data for {prefecture}...")
        
        params = {
            'prefecture': prefecture,
            'school_type': 'high_school',
            'include_details': True
        }
        
        data = self._make_api_request('schools/search', params)
        
        if data:
            logger.info(f"Successfully collected data for {prefecture}: {data.get('total_schools', 0)} schools")
        else:
            logger.error(f"Failed to collect data for {prefecture}")
        
        return data
    
    def save_prefecture_data(self, prefecture: str, data: Dict) -> bool:
        """Save prefecture data to JSON file"""
        try:
            filename = f"{prefecture.replace('県', '').replace('都', '').replace('府', '')}_schools.json"
            filepath = self.output_dir / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Saved data for {prefecture} to {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save data for {prefecture}: {e}")
            return False
    
    def collect_all_prefectures(self) -> Dict[str, bool]:
        """Collect data for all prefectures"""
        results = {}
        total_prefectures = len(self.prefectures)
        
        logger.info(f"Starting data collection for {total_prefectures} prefectures...")
        
        for i, prefecture in enumerate(self.prefectures, 1):
            logger.info(f"Processing {prefecture} ({i}/{total_prefectures})")
            
            try:
                data = self.collect_prefecture_data(prefecture)
                
                if data:
                    success = self.save_prefecture_data(prefecture, data)
                    results[prefecture] = success
                else:
                    results[prefecture] = False
                
                if i < total_prefectures:
                    time.sleep(1)
                    
            except Exception as e:
                logger.error(f"Error processing {prefecture}: {e}")
                results[prefecture] = False
        
        return results
    
    def generate_summary_report(self, results: Dict[str, bool]) -> None:
        """Generate summary report of collection results"""
        successful = sum(1 for success in results.values() if success)
        total = len(results)
        
        summary = {
            "collection_date": datetime.now().isoformat(),
            "total_prefectures": total,
            "successful_collections": successful,
            "failed_collections": total - successful,
            "success_rate": f"{(successful/total)*100:.1f}%",
            "results": results,
            "output_directory": str(self.output_dir),
            "api_status": "connected" if self.api_key else "placeholder_mode"
        }
        
        summary_path = self.output_dir / "collection_summary.json"
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Collection Summary:")
        logger.info(f"  Total prefectures: {total}")
        logger.info(f"  Successful: {successful}")
        logger.info(f"  Failed: {total - successful}")
        logger.info(f"  Success rate: {summary['success_rate']}")
        logger.info(f"  Summary saved to: {summary_path}")

def main():
    """Main execution function"""
    logger.info("Starting DeepResearch School Data Collection")
    
    collector = DeepResearchCollector()
    
    if not collector.api_key:
        logger.warning("DEEPRESEARCH_API_KEY environment variable not set.")
        logger.warning("Running in placeholder mode - generating sample data.")
    
    results = collector.collect_all_prefectures()
    
    collector.generate_summary_report(results)
    
    logger.info("Data collection completed!")
    
    return results

if __name__ == "__main__":
    main()
