import requests
import json
import pickle
from bs4 import BeautifulSoup as bs
from tqdm.auto import tqdm

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6)'
                  ' AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'
}


# solved 순위 기준으로 가져오기
def get_user_infos(page):
    user_infos = []
    for n in range(1, page + 1):
        res = requests.get("https://solved.ac/api/v3/ranking/tier", params={"page": n}, headers=headers)
        users = json.loads(res.text)["items"]

        for user in users:
            info = {
                "boj_handle": user["handle"],
                "rating": user["rating"],
            }

            atcoder_rating, cf_handle = get_atcoder_user_rating(user["handle"])  # 엣코더 레이팅
            if atcoder_rating is not None:
                info["atcoder_rating"] = atcoder_rating
                if cf_handle is not None and cf_handle != user["handle"]:  # 앳코더에 cf 아이디가 있으면
                    cf_rating = get_codeforces_user_rating(cf_handle)
                    if cf_rating is not None:
                        info["cf_rating"] = cf_rating

            if cf_handle is None:  # 앳코더에 cf 아이디가 없으면
                cf = get_codeforces_user_rating(user["handle"])
                if cf is not None:
                    info["cf_rating"] = cf

            print(info)
            user_infos.append(info)

    return user_infos


# 코포 레이팅 가져오기
def get_codeforces_user_rating(handle):
    try:
        res = requests.get("https://codeforces.com/api/user.rating", params={"handle": handle}, headers=headers)
        res = json.loads(res.text)
        if res["status"] == "FAILED" or len(res["result"]) <= 6:  # 만약 참여한 대회가 6개 이하
            return None
        return res["result"][-1]["newRating"]
    except:
        return None


# 앳코더 레이팅 가져오기
def get_atcoder_user_rating(handle):
    try:
        res = requests.get(f"https://atcoder.jp/users/{handle}", headers=headers)
        soup = bs(res.text, "html.parser")  # html 파싱
        rating = int(
            soup.select("#main-container > div.row > div.col-sm-12")[2].text.split("Rating")[1].split("\n")[
                0].strip())  # 레이팅 가져오기
        rating = None if \
            soup.select("#main-container > div.row > div.col-sm-12")[2].text.split("Rating")[1].split("\n")[
                1].strip() == "(Provisional)" else rating  # 레이팅이 Provisional이면 None
        try:
            cf_handle = \
                soup.select("#main-container > div.row > div.col-sm-12")[1].text.split("Codeforces ID")[1].split("\n")[
                    0].strip()
            return rating, cf_handle
        except:
            return rating, None
    except:
        return None, None


# 5만명 데이터 수집
# if __name__ == "__main__":
#     # page = int(input("page: "))
#     page=1000
#     users, atcoder_cnt, cf_cnt = get_user_infos(page)
#     print(
#         f"atcoder: {atcoder_cnt}/{len(users)} ({atcoder_cnt / len(users)}), codeforces: {cf_cnt}/{len(users)} ({cf_cnt / len(users)})")
#     pickle.dump(users, open("./user_infos.pkl", "wb")) # 객체를 파일로 덤프


# 데이터 업데이트(코드포스, 앳코더 참여 횟수 기준)
if __name__ == "__main__":
    with open("user_infos.pkl", "rb") as f:
        old_data = pickle.load(f) # 파일을 객체로 로드
        new_data = []
        pbar = tqdm(iterable=old_data, total=len(old_data))
        for u in pbar:
            if "cf_rating" in u:
                cf_rating = get_codeforces_user_rating(u["cf_handle"])
                if cf_rating is not None:
                    u["cf_rating"] = cf_rating
                else:
                    del u["cf_handle"]
                    del u["cf_rating"]
            if "atcoder_rating" in u:
                _, atcoder_rating = get_atcoder_user_rating(u["boj_handle"])
                if atcoder_rating is not None:
                    u["atcoder_rating"] = atcoder_rating
                else:
                    del u["atcoder_rating"]
                    del u["atcoder_handle"]
            if "atcoder_rating" in u or "cf_rating" in u:
                del u["boj_handle"]
                new_data.append(u)

        with open("new_user_infos.pkl", "wb") as ff:
            pickle.dump(new_data, ff)
