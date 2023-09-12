import configparser
import os
import config as cf
import process
import privateCrypt
import datetime

config = configparser.ConfigParser()  # 类实例化


def get_credentials_path():
    if cf.CREDENTIALS_PATH is not None:
        return cf.CREDENTIALS_PATH
    else:
        home_path = os.getcwd()
        config_parent_path = os.path.join(home_path, 'myConfig')
        config_path = os.path.join(config_parent_path, 'credentials')
        if not os.path.exists(config_parent_path):
            os.mkdir(config_parent_path)
        return config_path


path = get_credentials_path()
# 这里config需要用encoding，以防跨平台乱码
config.read(path, encoding="utf-8")
sections = config.sections()


if __name__ == '__main__':

    aes_key = privateCrypt.get_aes_key()

    while 1:
        process.init_headers()
        location_select: dict = {
            "province": "浙江省",
            "city": "杭州市",
            "location": "119.992931,30.228964"
        }
        province = location_select['province']
        city = location_select['city']
        location: str = location_select['location']

        mobile = input("输入手机号[13812341234]:").strip()
        process.get_vcode(mobile)
        code = input(f"输入 [{mobile}] 验证码[1234]:").strip()
        token, userId = process.login(mobile, code)

        day_20_later = datetime.datetime.now() + datetime.timedelta(days=20)
        endDate = day_20_later.strftime("%Y%m%d")

        # 为了增加辨识度，这里做了隐私处理，不参与任何业务逻辑
        hide_mobile = mobile.replace(mobile[3:7], '****')
        # 因为加密了手机号和Userid，所以token就不做加密了
        encrypt_mobile = privateCrypt.encrypt_aes_ecb(mobile, aes_key)
        encrypt_userid = privateCrypt.encrypt_aes_ecb(str(userId), aes_key)

        if encrypt_mobile not in sections:
            config.add_section(encrypt_mobile)  # 首先添加一个新的section

        config.set(encrypt_mobile, 'hidemobile', hide_mobile)
        config.set(encrypt_mobile, 'enddate', endDate)
        config.set(encrypt_mobile, 'userid', encrypt_userid)
        config.set(encrypt_mobile, 'province', str(province))
        config.set(encrypt_mobile, 'city', str(city))
        config.set(encrypt_mobile, 'token', str(token))

        config.set(encrypt_mobile, 'lat', location.split(',')[1])
        config.set(encrypt_mobile, 'lng', location.split(',')[0])

        config.write(open(path, 'w+', encoding="utf-8"))  # 保存数据

        condition = input(f"是否继续添加账号[y/n]:").strip()

        if condition.lower() == 'n':
            break
