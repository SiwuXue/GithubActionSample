import os
import time
import requests
import json
from bs4 import BeautifulSoup
import sendNotify


# 天气预报模板ID
weather_template_id = os.environ.get("TEMPLATE_ID")
# 课表模板ID
timetable_template_id = os.environ.get("TIMETABLE_TEMPLATE_ID")

def get_weather(my_city):
    urls = ["http://www.weather.com.cn/textFC/hb.shtml",
            "http://www.weather.com.cn/textFC/db.shtml",
            "http://www.weather.com.cn/textFC/hd.shtml",
            "http://www.weather.com.cn/textFC/hz.shtml",
            "http://www.weather.com.cn/textFC/hn.shtml",
            "http://www.weather.com.cn/textFC/xb.shtml",
            "http://www.weather.com.cn/textFC/xn.shtml"
            ]
    for url in urls:
        resp = requests.get(url)
        text = resp.content.decode("utf-8")
        soup = BeautifulSoup(text, 'html5lib')
        div_conMidtab = soup.find("div", class_="conMidtab")
        tables = div_conMidtab.find_all("table")
        for table in tables:
            trs = table.find_all("tr")[2:]
            for index, tr in enumerate(trs):
                tds = tr.find_all("td")
                # 这里倒着数，因为每个省会的td结构跟其他不一样
                city_td = tds[-8]
                this_city = list(city_td.stripped_strings)[0]
                if this_city == my_city:

                    high_temp_td = tds[-5]
                    low_temp_td = tds[-2]
                    weather_type_day_td = tds[-7]
                    weather_type_night_td = tds[-4]
                    wind_td_day = tds[-6]
                    wind_td_day_night = tds[-3]

                    high_temp = list(high_temp_td.stripped_strings)[0]
                    low_temp = list(low_temp_td.stripped_strings)[0]
                    weather_typ_day = list(weather_type_day_td.stripped_strings)[0]
                    weather_type_night = list(weather_type_night_td.stripped_strings)[0]

                    wind_day = list(wind_td_day.stripped_strings)[0] + list(wind_td_day.stripped_strings)[1]
                    wind_night = list(wind_td_day_night.stripped_strings)[0] + list(wind_td_day_night.stripped_strings)[1]

                    # 如果没有白天的数据就使用夜间的
                    temp = f"{low_temp}——{high_temp}摄氏度" if high_temp != "-" else f"{low_temp}摄氏度"
                    weather_typ = weather_typ_day if weather_typ_day != "-" else weather_type_night
                    wind = f"{wind_day}" if wind_day != "--" else f"{wind_night}"
                    return this_city, temp, weather_typ, wind


def get_daily_love():
    # 每日一句情话
    url = "https://api.lovelive.tools/api/SweetNothings/Serialization/Json"
    r = requests.get(url)
    all_dict = json.loads(r.text)
    sentence = all_dict['returnObj'][0]
    daily_love = sentence
    return daily_love


def send_weather(weather):
    # touser 就是 openID
    # template_id 就是模板ID
    # url 就是点击模板跳转的url
    # data就按这种格式写，time和text就是之前{{time.DATA}}中的那个time，value就是你要替换DATA的值

    import datetime
    today = datetime.date.today()
    today_str = today.strftime("%Y年%m月%d日")

    data = {
        "date": {
            "value": today_str
        },
        "region": {
            "value": weather[0]
        },
        "weather": {
            "value": weather[2]
        },
        "temp": {
            "value": weather[1]
        },
        "wind_dir": {
            "value": weather[3]
        },
        "today_note": {
            "value": get_daily_love()
        }
    }
    
    sendNotify.send_template_message(weather_template_id, data)


def send_timetable(message):
    if not timetable_template_id:
        print("Error: TIMETABLE_TEMPLATE_ID not set.")
        return

    data = {
        "message": {
            "value": message
        },
    }
    sendNotify.send_template_message(timetable_template_id, data)


def weather_report(city):
    # 1. 获取天气
    weather = get_weather(city)
    if not weather:
        print(f"无法获取到 {city} 的天气信息")
        return
    print(f"天气信息： {weather}")
    # 2. 发送消息
    send_weather(weather)


def timetable(message):
    # 1. 发送消息
    send_timetable(message)


if __name__ == '__main__':
    weather_report("郑州")
    #timetable("第二教学楼十分钟后开始英语课")

    # schedule.every().day.at("18:30").do(weather_report, "南京")
    # schedule.every().monday.at("13:50").do(timetable, "第二教学楼十分钟后开始英语课")
    #while True:
    #    schedule.run_pending()
    #    time.sleep(1)
