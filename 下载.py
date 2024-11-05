import os
import requests
import time
import random
import urllib.parse
import re

def get_images(keyword, num_images=10):
    """获取图片搜索结果"""
    keyword_encoded = urllib.parse.quote(keyword)
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
    }
    
    # 使用百度图片搜索页面
    url = f'https://image.baidu.com/search/flip?tn=baiduimage&word={keyword_encoded}&pn=0'
    
    img_urls = []
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # 使用正则表达式提取图片URL
        img_urls_raw = re.findall('"objURL":"(.*?)",', response.text)
        
        # 限制数量并构造结果
        for i, url in enumerate(img_urls_raw):
            if i >= num_images:
                break
            if url.startswith('http'):
                img_urls.append({
                    'url': url,
                    'title': f'{keyword}_{i+1}'
                })
                
    except Exception as e:
        print(f"获取图片列表出错: {e}")
        # 备用方案
        try:
            # 使用另一个URL格式
            url = f'https://image.baidu.com/search/index?tn=baiduimage&word={keyword_encoded}'
            response = requests.get(url, headers=headers, timeout=10)
            img_urls_raw = re.findall('"thumbURL":"(.*?)",', response.text)
            
            for i, url in enumerate(img_urls_raw):
                if i >= num_images:
                    break
                if url.startswith('http'):
                    img_urls.append({
                        'url': url,
                        'title': f'{keyword}_{i+1}'
                    })
        except Exception as e2:
            print(f"备用方案也失败了: {e2}")
    
    return img_urls

def download_images(img_urls, save_dir, keyword):
    """下载图片"""
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
        print(f"创建目录: {save_dir}")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'image/webp,*/*',
        'Referer': 'https://image.baidu.com/'
    }
    
    downloaded = 0
    for idx, img_info in enumerate(img_urls):
        img_url = img_info['url']
        try:
            print(f"\n正在下载第 {idx + 1} 张图片:")
            print(f"URL: {img_url}")
            
            # 添加重试机制
            max_retries = 3
            retry_count = 0
            while retry_count < max_retries:
                try:
                    response = requests.get(img_url, headers=headers, timeout=15)
                    response.raise_for_status()
                    break
                except requests.RequestException as e:
                    retry_count += 1
                    if retry_count == max_retries:
                        raise e
                    print(f"重试第 {retry_count} 次...")
                    time.sleep(1)
            
            # 检查响应内容类型和大小
            content_type = response.headers.get('content-type', '').lower()
            content_length = len(response.content)
            
            if content_length < 1024:  # 小于1KB可能是错误图片
                print(f"跳过: 图片太小 ({content_length} bytes)")
                continue
                
            # 确定文件扩展名
            if 'jpeg' in content_type or 'jpg' in content_type:
                ext = 'jpg'
            elif 'png' in content_type:
                ext = 'png'
            elif 'gif' in content_type:
                ext = 'gif'
            else:
                # 从URL尝试获取扩展名
                url_ext = img_url.split('.')[-1].lower()
                if url_ext in ['jpg', 'jpeg', 'png', 'gif']:
                    ext = url_ext
                else:
                    ext = 'jpg'
            
            # 保存图片
            file_name = f"{keyword}_{idx + 1}.{ext}"
            save_path = os.path.join(save_dir, file_name)
            
            with open(save_path, 'wb') as f:
                f.write(response.content)
            
            print(f"成功下载: {file_name}")
            downloaded += 1
            
            # 随机延迟
            time.sleep(random.uniform(1.0, 2.0))
            
        except Exception as e:
            print(f"下载失败: {e}")
            continue
            
    return downloaded

def main():
    # 设置参数
    keywords = [
        "白背景板",
         "白色光滑墙壁",
    ]
    
    save_directory = "C:/Users/lenovo/Desktop/photo"
    images_per_breed = 50
    
    print("程序开始运行...")
    print(f"保存目录: {save_directory}")
    
    total_downloaded = 0
    
    for keyword in keywords:
        print(f"\n搜索关键词: {keyword}")
        img_urls = get_images(keyword, images_per_breed)
        print(f"找到 {len(img_urls)} 个图片链接")
        
        if img_urls:
            downloaded = download_images(img_urls, save_directory, keyword)
            total_downloaded += downloaded
            print(f"成功下载 {downloaded} 张 {keyword} 的图片")
        else:
            print(f"未找到 {keyword} 的图片")
    
    print(f"\n下载完成! 总共成功下载 {total_downloaded} 张图片")
    input("\n按回车键退出...")

if __name__ == "__main__":
    main()
