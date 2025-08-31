import hashlib
import json
import re
import os
import webbrowser
import requests
import time
import base64
from rsa import core, PublicKey, transform
from colorama import init, Fore, Back, Style
# 额外功能，自行取消注释
# import msyk_message
# import msyk_learning_circle

# 课件下载转PDF功能，需要pillow
try:
    from PIL import Image
    PILLOW_AVAILABLE = True
except ImportError:
    PILLOW_AVAILABLE = False
    Image = None

# 科目代码映射字典
# 科目代码映射字典
SUBJECT_CODE_MAP = {
    "0621": "问卷调查",
    "099": "其它",
    "3001": "政治",
    "3002": "历史",
    "3003": "地理",
    "3004": "思想品德",
    "3006": "物理",
    "3007": "语文",
    "3008": "数学",
    "3009": "英语",
    "3011": "化学",
    "3012": "音乐",
    "3013": "美术",
    "3014": "体育与健康",
    "3015": "通用技术",
    "3016": "艺术",
    "3017": "艺术欣赏音乐",
    "3018": "艺术欣赏美术",
    "3019": "公共卫生教育",
    "3020": "生物",
    "3021": "心理健康教育",
    "3022": "社会",
    "3023": "劳动技术",
    "3024": "科学",
    "3025": "综合实践",
    "3026": "汉语",
    "3029": "德育",
    "3037": "技术",
    "3088": "信息技术",
    "3099": "公共卫生科学",
    "3101": "文综",
    "3102": "理综",
    "3109": "高中综合",
    "3110": "通用(选考)",
    "3111": "通用(学考)",
    "3113": "信息(选考)",
    "3114": "信息(学考)",
    "3324": "物理竞赛",
    "3325": "扫除",
    "3326": "班会",
    "3327": "自习",
    "3328": "化学竞赛",
    "3567": "俄语",
    "3779": "班会",
    "3BX11": "世界文明史",
    "9834": "语音",
    "99999": "生物竞赛",
    "s926": "数学竞赛"
}

SUBJECT_NAME_TO_CODE = {v: k for k, v in SUBJECT_CODE_MAP.items()}

# 定义科目颜色映射
SUBJECT_COLORS = {
    '政治': Fore.YELLOW,
    '历史': Fore.CYAN,
    '语文': Fore.LIGHTWHITE_EX,
    '数学': Fore.LIGHTRED_EX,
    '英语': Fore.LIGHTGREEN_EX,
    '语音': Fore.LIGHTGREEN_EX,
    '物理': Fore.LIGHTMAGENTA_EX,
    '化学': Fore.LIGHTBLUE_EX,
    '生物': Fore.LIGHTCYAN_EX,
    '地理': Fore.LIGHTYELLOW_EX,
    '体育与健康': Fore.LIGHTRED_EX,
    '通用(选考)': Fore.BLUE,
    '通用(学考)': Fore.LIGHTBLUE_EX,
    '信息(选考)': Fore.MAGENTA,
    '信息(学考)': Fore.LIGHTMAGENTA_EX,
    # 默认颜色
    '其他': Fore.LIGHTYELLOW_EX
}

init(autoreset=True)  # 文字颜色自动恢复
roll = 1  # 循环
serialNumbers, answers, serialNumbersa, answersa = "", "", "", ""
msyk_sign_pubkey = "MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAj7YWxpOwulFyf+zQU77Y2cd9chZUMfiwokgUaigyeD8ac5E8LQpVHWzkm+1CuzH0GxTCWvAUVHWfefOEe4AThk4AbFBNCXqB+MqofroED6Uec1jrLGNcql9IWX3CN2J6mqJQ8QLB/xPg/7FUTmd8KtGPrtOrKKP64BM5cqaB1xCc4xmQTuWvtK9fRei6LVTHZyH0Ui7nP/TSF3PJV3ywMlkkQxKi8JBkz1fx1ZO5TVLYRKxzMQdeD6whq+kOsSXhlLIiC/Y8skdBJmsBWDMfQXxtMr5CyFbVMrG+lip/V5n22EdigHcLOmFW9nnB+sgiifLHeXx951lcTmaGy4uChQIDAQAB"

msyk_key = "DxlE8wwbZt8Y2ULQfgGywAgZfJl82G9S"
headers = {'user-agent': "okhttp/3.12.1"}
sign = ""


def getAccountInform():
    ReturnInform = ""
    ProfileImport = ""
    try:
        with open("ProfileCache.txt", "r", encoding='utf-8') as f:
            for line in f.readlines():
                line = line.strip('\n')  # 去掉列表中每一个元素的换行符
                ReturnInform = ReturnInform + line
        print("检测到 ProfileCache，尝试缓存登录中。（如失败自动执行登录流程）")
        setAccountInform(ReturnInform)
    except BaseException:
        print("未检测到 ProfileCache，执行登录流程。")
        ProfileImport = input(Fore.CYAN + "可提供未缓存的登录信息(失败则自动执行账号密码登录):")
        try:
            setAccountInform(ProfileImport)
        except BaseException:
            print(Fore.RED + "错误：登录信息有误或已经失效。")
            print(Fore.WHITE)
            login()


def answer_encode(answer):
    answer_code = ""
    if len(answer) == 1:
        return answer
    else:
        if "A" in answer:
            answer_code += "1"
        else:
            answer_code += "0"
        if "B" in answer:
            answer_code += "1"
        else:
            answer_code += "0"
        if "C" in answer:
            answer_code += "1"
        else:
            answer_code += "0"
        if "D" in answer:
            answer_code += "1"
        else:
            answer_code += "0"
        if "E" in answer:
            answer_code += "1"
        else:
            answer_code += "0"
        if "F" in answer:
            answer_code += "1"
        else:
            answer_code += "0"
        if "G" in answer:
            answer_code += "1"
        else:
            answer_code += "0"
        if "H" in answer:
            answer_code += "1"
        else:
            answer_code += "0"
        if "I" in answer:
            answer_code += "1"
        else:
            answer_code += "0"
        if "J" in answer:
            answer_code += "1"
        else:
            answer_code += "0"
        return answer_code


def save_json(data, filename):
    filename += ".json"
    try:
        with open(filename, 'w', encoding='utf-8') as file:
            file.write(data)
        print(Fore.MAGENTA + "保存登录信息成功 " + filename)
    except BaseException:
        print(Fore.RED + "保存登录信息失败")


def public_key_decrypt(publicKey, content):
    qr_code_cipher = base64.b64decode(content)
    public_key = base64.b64decode(publicKey)
    try:
        rsa_public_key = PublicKey.load_pkcs1_openssl_der(public_key)
        cipher_text_bytes = transform.bytes2int(qr_code_cipher)
        decrypted_text = core.decrypt_int(
            cipher_text_bytes, rsa_public_key.e, rsa_public_key.n)
        final_text = transform.int2bytes(decrypted_text)
        final_code = final_text[final_text.index(0) + 1:]
        return final_code.decode()
    except Exception:
        print(Fore.RED + "警告:sign解密失败!")
        return None


def getCurrentTime():
    return int(round(time.time() * 1000))


def TimeToHMS(ts: int):
    # 十三位时间戳
    return time.strftime("%H:%M:%S", time.localtime(ts / 1000))
# 字符计算32位md5


def string_to_md5(string):
    md5_val = hashlib.md5(string.encode('utf8')).hexdigest()
    return md5_val
# 浏览器新窗口打开链接


def open_url(url):
    webbrowser.open_new(url)
# login

# POST方案，目前以弃用


def login1():
    userName = input("用户名:")
    pwd = input("密码:")
    mac = input("mac:").upper()  # mac地址要大写
    api = input("安卓API:")
    sn = input(Fore.RED + "SN(区分大小写):")
    genauth = string_to_md5(userName + pwd + "HHOO")
    dataup = {
    "userName": userName,
    "auth": genauth,
    "macAddress": mac,
    "versionCode": api,
     "sn": sn}
    res = post("https://padapp.msyk.cn/ws/app/padLogin",
               dataup, 1, genauth + mac + sn + userName + api)
    setAccountInform(res)

# 登入已简化为GET方案，感谢 cyhLen 提供方案


def login():
    userName = input("用户名:")
    password = input("密码:")
    pwd = string_to_md5(userName + password + "HHOO")
    loginurl = 'https://padapp.msyk.cn/ws/app/padLogin?userName=' + \
        userName + '&auth=' + pwd
    login_first = requests.get(loginurl).text
    setAccountInform(login_first)


def normalize_url(url):
    """规范化URL"""
    if not url:
        return ""
    url = url.strip()
    if url.lower().startswith('http'):
        return url
    elif url.lower().startswith('//'):
        return "https:" + url
    elif url.lower().startswith('/'):
        return "https://msyk.wpstatic.cn" + url
    else:
        return "https://msyk.wpstatic.cn/" + url


def build_question_url(question, student_id, unit_id):
    """构建问题URL"""
    return f"https://www.msyk.cn/webview/newQuestion/singleDoHomework?studentId={student_id}&homeworkResourceId={question['resourceId']}&orderNum={question['orderNum']}&showAnswer=1&unitId={unit_id}&modifyNum=1"


def safe_filename(filename):
    """确保文件名安全"""
    return re.sub(r'[<>:"/\\|?*]', '_', filename)


def parse_msyk_html(html_doc, count, url, return_empty=False):
    """统一的HTML解析函数"""
    html_doc = html_doc.replace('\n', '')
    index = html_doc.find("var questions = ")
    index1 = html_doc.find("var resource")
    if index != -1 and index1 != -1:
        try:
            json_str = html_doc[index + 16:index1 - 1].strip()
            if json_str.endswith(';'):
                json_str = json_str[:-1]
            data = json.loads(json_str)
            if data and isinstance(data, list) and len(
                    data) > 0 and data[0].get('answer') is not None:
                answer = "".join(
                    data[0].get('answer')).lstrip("[").rstrip("]").replace(
        '"',
        '').replace(
            ',',
                    ' ').strip()
                
                #只有当答案包含数字但不是纯数字时才打开浏览器
                if re.search(r'\d', answer) and not re.match(r'^\d+$', answer):
                    print(Fore.YELLOW + f"检测到复杂答案，打开浏览器查看: \n{url}")
                    open_url(url)
                    print(Fore.GREEN + count + " 在浏览器中打开")
                    return "wtf"
                else:
                    print(Fore.GREEN + count + " " + answer)
                    return answer
            else:
                print(Fore.RED + count + " " + "没有检测到答案,有可能是主观题")
                return " " if return_empty else "wtf"
        except json.JSONDecodeError as e:
            print(Fore.RED + f"JSON解析错误: {e}")
            #  fallback 到原始方法
            return ljlVink_parsemsyk_fallback(
                html_doc, count, url, return_empty)
    return " " if return_empty else "wtf"


def ljlVink_parsemsyk_fallback(html_doc, count, url, return_empty=False):
    """备用的HTML解析函数（原始逻辑）"""
    html_doc = html_doc.replace('\n', "")
    index = html_doc.find("var questions = ")
    index1 = html_doc.find("var resource")
    if index != -1:
        try:
            data = json.loads(html_doc[index + 16:index1 - 7])
            if data[0].get('answer') is not None:
                answer = "".join(
                    data[0].get('answer')).lstrip("[")[
        :-
        1].replace(
            '"',
            '').lstrip(",").replace(
                ',',
                    ' ')
                
                # 同样修改逻辑，作用同上
                if re.search(r'\d', answer) and not re.match(r'^\d+$', answer):
                    open_url(url)
                    print(Fore.GREEN + count + " 在浏览器中打开")
                    return "wtf"
                else:
                    print(Fore.GREEN + count + " " + answer)
                    return answer
            else:
                print(Fore.RED + count + " " + "没有检测到答案,有可能是主观题")
                return " " if return_empty else "wtf"
        except Exception as e:
            print(Fore.RED + f"备用解析也失败: {e}")
            return " " if return_empty else "wtf"
    return " " if return_empty else "wtf"

# 获取账号信息

def setAccountInform(result):
    # 成功登录 获取账号信息
    if json.loads(result).get('code') == "10000":
        # avatar=json.loads(res).get('InfoMap').get('avatarUrl')
        # open_url(avatar)#浏览器打开头像（同时测试能否正常打开浏览器）
        # print(Fore.GREEN + "===============")
        # print(Fore.GREEN + result)
        # print(Fore.GREEN + "===============")
        save_json(result, json.loads(result).get('InfoMap').get('realName'))
        with open("ProfileCache.txt", "w", encoding='utf-8') as f:
            f.write(result)
        print("ProfileCache 登录缓存已更新。(下一次优先自动读取)")
        global unitId, id
        unitId = json.loads(result).get('InfoMap').get('unitId')
        id = json.loads(result).get('InfoMap').get('id')

        sign1 = public_key_decrypt(
    msyk_sign_pubkey,
     json.loads(result).get('sign')).split(':')
        if sign1 != None:
            signdec = ','.join(sign1)
            print(Fore.GREEN + "sign解密成功:" + signdec)
            global sign
            sign = sign1[1] + id

    # 登录失败 打印原因
    else:
        print(Fore.RED + json.loads(result).get('message'))
        exit(1)
# post


def post(url, postdata, type=1, extra=''):
    time = getCurrentTime()
    key = ''
    if type == 1:
        key = string_to_md5(extra + str(time) + sign + msyk_key)
    elif type == 2:
        key = string_to_md5(extra + id + unitId + str(time) + sign + msyk_key)
    elif type == 3:
        key = string_to_md5(extra + unitId + id + str(time) + sign + msyk_key)
    postdata.update({'salt': time, 'sign': sign, 'key': key})
    try:
        req = requests.post(url=url, data=postdata, headers=headers)
        return req.text
    except BaseException:
        print(Fore.RED + str(url) + " " + str(postdata))
        print(Fore.RED + "网络异常 请检查代理设置")
        exit(1)


def process_homework_type7(hwid, res, ress, is_retry=False):
    """处理类型7作业的公共函数"""
    global serialNumbers, answers, serialNumbersa, answersa, id, unitId

    materialRelasList, analysistList = json.loads(res).get(
        'materialRelas'), json.loads(res).get('analysistList')
    materialRelasUrls, analysistUrls, materialRelasFiles, analysistFiles = [], [], [], []
    hwname = json.loads(res).get('homeworkName')
    print(Fore.MAGENTA + Back.WHITE + str(hwname))  # 作业名
    res_list = json.loads(res).get('homeworkCardList')  # 题目list

    # 处理材料文件
    if len(materialRelasList) == 0:
        print(Fore.RED + "没有材料文件")
    else:
        print(Fore.MAGENTA + "材料文件:")
        for file in materialRelasList:
            file_url = normalize_url(file['resourceUrl'])
            materialRelasFiles.append(file['title'])
            materialRelasUrls.append(file_url)
            print(Fore.GREEN + "\t" + file['title'] + " " + file_url)

    # 处理答案文件
    if len(analysistList) == 0:
        print(Fore.RED + "没有答案文件")
    else:
        print(Fore.MAGENTA + "答案文件:")
        for file in analysistList:
            file_url = normalize_url(file['resourceUrl'])
            analysistFiles.append(file['title'])
            analysistUrls.append(file_url)
            print(Fore.GREEN + "\t" + file['title'] + " " + file_url)

    # 处理题目
    question_list = []
    for question in res_list:
        serialNumber = str(question['serialNumber'])
        url = build_question_url(question, id, unitId)
        try:
            vink = requests.get(url=url, timeout=10)
            answer = parse_msyk_html(vink.text, (question['orderNum']), url)
        except requests.exceptions.Timeout:
            print(Fore.RED + f"题目 {serialNumber} 请求超时")
            answer = "wtf"
        except Exception as e:
            print(Fore.RED + f"题目 {serialNumber} 处理错误: {e}")
            answer = "wtf"

        question_list.append(question['resourceId'])

        # 处理答案编码 - 修复重复编码问题
        encoded_answer = answer_encode(answer)

        # 添加到主观题答案列表（总是添加）
        if serialNumbersa == "":
            serialNumbersa += serialNumber
            answersa += encoded_answer
        else:
            serialNumbersa += ";" + serialNumber
            answersa += ";" + encoded_answer

        # 只将非wtf答案添加到选择题答案列表
        if answer != "wtf":
            if serialNumbers == "":
                serialNumbers += serialNumber
                answers += encoded_answer
            else:
                serialNumbers += ";" + serialNumber
                answers += ";" + encoded_answer

    # print(question_list)  # 打印题目id列表

    # 用户交互部分
    if not is_retry:
        up = input(Fore.MAGENTA + "是否要提交选择答案 y/N:")
        if up.lower() == "y":
            dataup = {
                "serialNumbers": serialNumbers,
                "answers": answers,
                "studentId": id,
                "homeworkId": int(hwid),
                "unitId": unitId,
                "modifyNum": 0}
            res = post(
                "https://padapp.msyk.cn/ws/teacher/homeworkCard/saveCardAnswerObjectives",
                dataup,
                2,
                answers +
                hwid +
                '0' +
                serialNumbers)
            if json.loads(res).get('code') == "10000":
                print(Fore.GREEN + "自动提交选择答案成功")

        middle = input(Fore.YELLOW + "是否要为主观题提交假图片 y/N:")
        if middle.lower() == "y":
            dataup = {
                "serialNumbers": serialNumbersa,
                "answers": answersa,
                "studentId": id,
                "homeworkId": int(hwid),
                "unitId": unitId,
                "modifyNum": 0}
            res = post(
                "https://padapp.msyk.cn/ws/teacher/homeworkCard/saveCardAnswerObjectives",
                dataup,
                2,
                answers +
                hwid +
                '0' +
                serialNumbers)
            if json.loads(res).get('code') == "10000":
                print(Fore.GREEN + "自动提交主观题提交假图片成功")

        if len(analysistList) != 0 or len(materialRelasList) != 0:
            down = input(Fore.BLUE + "是否要下载文件 y/N:")
            if down.lower() == "y":
                for url, file in zip(materialRelasUrls, materialRelasFiles):
                    safe_file = safe_filename(file)
                    try:
                        with open(safe_file, "wb") as f:
                            response = requests.get(url, timeout=30)
                            f.write(response.content)
                        print(Fore.GREEN + f"已下载: {safe_file}")
                    except Exception as e:
                        print(Fore.RED + f"下载失败 {file}: {e}")
                for url, file in zip(analysistUrls, analysistFiles):
                    safe_file = safe_filename(file)
                    try:
                        with open(safe_file, "wb") as f:
                            response = requests.get(url, timeout=30)
                            f.write(response.content)
                        print(Fore.GREEN + f"已下载: {safe_file}")
                    except Exception as e:
                        print(Fore.RED + f"下载失败 {file}: {e}")
    else:
        print(Fore.YELLOW + "重试模式，跳过用户交互")

    # 重置全局变量
    if not is_retry:
        serialNumbers, answers = "", ""

#选择答案提交(新方法)
def operation_answerget_new(studentId,unitId,homeworkId):
    serialNumbers,answers="",""
    body=requests.get("https://padapp.msyk.cn/ws/teacher/homeworkCard/getHomeworkCardInfo?homeworkId="+homeworkId+"&studentId=&modifyNum=0&unitId="+unitId).json()
    homeworkCardList=body['homeworkCardList']
    for homeworkCard in homeworkCardList:
        serialNumber=homeworkCard['serialNumber'] #serialNumber是提交使用的题号
        orderNum=homeworkCard['orderNum'] #orderNum是显示的题号
        answer=homeworkCard['answer']
        if answer!="" :
            if serialNumbers=="" :
                serialNumbers=serialNumbers+str(serialNumber)
                answers=answers+str(answer)
            else:
                serialNumbers=serialNumbers+";"+str(serialNumber)
                answers=answers+";"+str(answer)
            answer_Show=answer = (lambda answer: answer if len(answer) != 10 else ''.join("ABCDEFGHIJ"[i] for i in range(10) if answer[i] == '1'))(answer)
            answer_Show=answer
            print(Fore.GREEN+str(orderNum)+" "+answer_Show)
        else:
            print(Fore.RED+str(orderNum)+" "+"未检测到答案，有可能是主观题")
    Mission=input(Fore.BLUE+"是否提交选择答案?[Y/n]")
    if Mission=="y" or Mission=="Y":
        submiturl="https://padapp.msyk.cn/ws/teacher/homeworkCard/saveCardAnswerObjectives?serialNumbers="+serialNumbers+"&answers="+answers+"&studentId="+studentId+"&homeworkId="+homeworkId+"&unitId="+unitId+"&modifyNum=0"
        returntext=requests.get(submiturl).text
        #print(submiturl,returntext)
        print("提交选择答案成功")
    else:
        print("已取消操作")

# PPT下载


def get_ppt_info_post(ppt_resource_id, res_source=1):
    """获取PPT文件的页面信息（POST方式）"""
    salt = getCurrentTime()
    # 生成key
    key_data = f"{ppt_resource_id}{res_source}{salt}{sign}{msyk_key}"
    key = string_to_md5(key_data)

    dataup = {
        "pptResourceId": ppt_resource_id,
        "resSource": res_source,
        "salt": salt,
        "sign": sign,
        "key": key
    }

    res = post(
        "https://padapp.msyk.cn/ws/student/homework/studentHomework/homeworkPPTInfo",
        dataup,
        type=2)

    if res.strip() and json.loads(res).get('code') == "10000":
        return json.loads(res).get('sqPptConvertList', [])
    return []


def download_ppt(ppt_resource_id, res_title):
    """下载PPT页面并提供PDF转换选项"""
    print(Fore.YELLOW + "文件名:", Fore.CYAN + Back.WHITE + res_title)

    # 获取PPT页面信息
    ppt_pages = get_ppt_info_post(ppt_resource_id)
    if not ppt_pages:
        print(Fore.RED + "无法获取PPT页面信息")
        return False

    print(Fore.GREEN + f"找到 {len(ppt_pages)} 页PPT")

    # 创建下载目录
    safe_title = re.sub(r'[<>:"/\\|?*]', '_', res_title)  # 移除文件名中的非法字符
    download_dir = re.sub(r'[^\w\-_\. ]', '_', f"PPT_{ppt_resource_id}_{safe_title}")
    os.makedirs(download_dir, exist_ok=True)

    # 下载所有页面
    success_count = 0
    for page in ppt_pages:
        page_url = "https://msyk.wpstatic.cn/" + page['path']
        page_num = page['displayNum']
        page_filename = f"{download_dir}/第{page_num:02d}页.jpg"

        print(Fore.CYAN + f"下载第 {page_num} 页...")
        try:
            response = requests.get(page_url, stream=True, timeout=30)
            if response.status_code == 200:
                with open(page_filename, 'wb') as f:
                    for chunk in response.iter_content(1024):
                        f.write(chunk)
                print(Fore.GREEN + f"第 {page_num} 页下载成功")
                success_count += 1
            else:
                print(Fore.RED + f"第 {page_num} 页下载失败: HTTP {response.status_code}")
        except Exception as e:
            print(Fore.RED + f"第 {page_num} 页下载失败: {str(e)}")

    if success_count > 0:
        print(Fore.GREEN + f"下载完成！共成功下载 {success_count}/{len(ppt_pages)} 页")
        print(Fore.GREEN + f"文件保存在: {os.path.abspath(download_dir)}/")

        # 如果Pillow可用，提供PDF转换选项
        if PILLOW_AVAILABLE and success_count == len(ppt_pages):
            convert_choice = input(Fore.BLUE + "是否要转换为PDF文件？[Y/n]")
            if convert_choice == 'Y' or convert_choice == 'y':
                pdf_path = convert_ppt_to_pdf(
                    download_dir, f"{safe_title}.pdf")
                if pdf_path:
                    print(Fore.GREEN + f"PDF转换成功: {pdf_path}")
        elif not PILLOW_AVAILABLE:
            print(Fore.YELLOW + "提示: 安装Pillow库后可以自动转换PPT为PDF")
            print(Fore.YELLOW + "命令: pip install Pillow")

        return True
    else:
        print(Fore.RED + "所有页面下载失败")
        return False


def convert_ppt_to_pdf(ppt_folder, output_pdf):
    """将PPT图片文件夹转换为PDF"""
    if not PILLOW_AVAILABLE:
        print(Fore.RED + "错误: Pillow库未安装，无法转换PDF")
        print(Fore.YELLOW + "请运行: pip install Pillow")
        return None

    try:
        # 获取所有图片文件
        image_files = []
        for ext in ['.jpg', '.jpeg', '.png']:
            image_files.extend([f for f in os.listdir(
                ppt_folder) if f.lower().endswith(ext)])

        if not image_files:
            print(Fore.RED + f"错误: 在 '{ppt_folder}' 中没有找到图片文件")
            return None

        # 按数字顺序排序
        image_files.sort(
            key=lambda x: [
        int(c) if c.isdigit() else c.lower() for c in re.split(
            r'(\d+)', x)])

        # 转换为PDF
        images = []
        for img_file in image_files:
            img_path = os.path.join(ppt_folder, img_file)
            img = Image.open(img_path)
            if img.mode != 'RGB':
                img = img.convert('RGB')
            images.append(img)
            print(Fore.CYAN + f"已加载: {img_file}")

        if images:
            # 确保输出路径是绝对路径
            if not os.path.isabs(output_pdf):
                output_pdf = os.path.join(os.getcwd(), output_pdf)

            images[0].save(output_pdf, save_all=True, append_images=images[1:])
            return output_pdf

    except Exception as e:
        print(Fore.RED + f"PDF转换失败: {str(e)}")
        return None

    return None


def getAnswer():
    # 增加输入要求提示
    while True:
        hwid_input = input(Fore.YELLOW + "请输入作业id:")
        try:
            hwid = int(hwid_input)
            break
        except ValueError:
            print(Fore.RED + "作业ID必须是数字，请重新输入")
    hwid = str(hwid)

    # 最多重试2次
    retry_count = 0
    max_retries = 2

    while retry_count <= max_retries:
        dataup = {
            "homeworkId": int(hwid),
            "studentId": id,
            "modifyNum": 0,
            "unitId": unitId
        }
        res = post(
            "https://padapp.msyk.cn/ws/teacher/homeworkCard/getHomeworkCardInfo",
            dataup,
            2,
            hwid + '0'
        )
        dataupp = {
            "homeworkId": hwid,
            "modifyNum": 0,
            "userId": id,
            "unitId": unitId
        }
        ress = post(
            "https://padapp.msyk.cn/ws/common/homework/homeworkStatus",
            dataupp,
            3,
            str(hwid) + '0'
        )

        # 判断 ress 是否为空
        if not ress.strip():
            if retry_count == max_retries:
                print(Fore.RED + "ress仍然为空，美师优课是傻逼")
                return
            else:
                choice = input("ress为空，是否重新解析(默认是，否请输入1):")
                if choice.strip() == "1":
                    print("用户取消重试")
                    return
                retry_count += 1
                continue

        # 判断 res 是否为空
        if not res.strip():
            if retry_count == max_retries:
                print(Fore.RED + "res仍然为空，美师优课是傻逼")
                return
            else:
                choice = input("res为空，是否重新解析(默认是，否请输入1):")
                if choice.strip() == "1":
                    print("用户取消重试")
                    return
                retry_count += 1
                continue

        # 获取作业类型
        try:
            hwtp = json.loads(ress).get('homeworkType')
        except:
            hwtp = None

        # 处理不同类型作业
        if str(hwtp) == "7":
            process_homework_type7(hwid, res, ress, is_retry=(retry_count > 0))
            break  # 成功处理，退出重试循环
        elif str(hwtp) == "5":
            # 处理类型5作业
            resourceList = json.loads(ress).get('resourceList', [])
            hwname = json.loads(res).get('homeworkName', "未知作业")
            print(Fore.MAGENTA + Style.BRIGHT + str(hwname))
            print(Fore.MAGENTA + Style.NORMAL + "材料文件:")
            materialRelasFiles, materialRelasUrls = [], []

            for file in resourceList:
                if file.get('resourceType') == 5:
                    ppt_resource_id = file.get('resourceUrl')
                    res_title = file.get('resTitle', "未知标题")
                    print(Fore.YELLOW + "检测到PPT文件:", Fore.CYAN + Back.WHITE + res_title)
                    download_choose = input(Fore.BLUE + "是否要下载该PPT文件？[Y/n]")
                    if download_choose.lower() in ['y', '']:
                        success = download_ppt(ppt_resource_id, res_title)
                        if success:
                            print(Fore.WHITE + "PPT处理完成")
                        else:
                            print(Fore.RED + "PPT处理失败")
                else:
                    file_url = normalize_url(file.get('resourceUrl'))
                    file_title = file.get('resTitle', "未知文件")
                    materialRelasFiles.append(file_title)
                    materialRelasUrls.append(file_url)
                    print(Fore.GREEN + "\t" + file_title + " " + file_url)

            if materialRelasUrls:
                down = input(Fore.BLUE + "是否要下载非PPT文件 y/N:")
                if down.lower() == "y":
                    for url, file in zip(materialRelasUrls, materialRelasFiles):
                        safe_file = safe_filename(file)
                        try:
                            with open(safe_file, "wb") as f:
                                response = requests.get(url, timeout=30)
                                f.write(response.content)
                            print(Fore.GREEN + f"已下载: {safe_file}")
                        except Exception as e:
                            print(Fore.RED + f"下载失败 {file}: {e}")
            break  # 成功处理，退出重试循环
        else:
            # 处理其他类型作业
            resourceList = json.loads(ress).get('resourceList', [])
            materialRelasUrls, materialRelasFiles = [], []
            hwname = json.loads(res).get('homeworkName', "未知作业")
            print(Fore.MAGENTA + Style.BRIGHT + str(hwname))
            print(Fore.MAGENTA + Style.NORMAL + "材料文件:")

            for file in resourceList:
                file_url = normalize_url(file.get('resourceUrl'))
                file_title = file.get('resTitle', "未知文件")
                materialRelasFiles.append(file_title)
                materialRelasUrls.append(file_url)
                print(Fore.GREEN + "\t" + file_title + " " + file_url)

            if materialRelasUrls:
                down = input(Fore.BLUE + "是否要下载文件 y/N:")
                if down.lower() == "y":
                    for url, file in zip(materialRelasUrls, materialRelasFiles):
                        safe_file = safe_filename(file)
                        try:
                            with open(safe_file, "wb") as f:
                                response = requests.get(url, timeout=30)
                                f.write(response.content)
                            print(Fore.GREEN + f"已下载: {safe_file}")
                        except Exception as e:
                            print(Fore.RED + f"下载失败 {file}: {e}")
            break  # 成功处理，退出重试循环


def getUnreleasedHWID():
    EndHWID = 0
    StartHWID = int(input(Fore.YELLOW + "请输入起始作业id:"))
    EndHWID = int(input(Fore.YELLOW + "请输入截止作业id(小于起始则不会停):"))
    hwidplus100 = StartHWID + 100
    while roll == 1:
        if StartHWID == hwidplus100:
            print(Fore.GREEN + "已滚动100项 当前" + str(hwidplus100))
            hwidplus100 += 100

        dataup = {
            "homeworkId": StartHWID,
            "modifyNum": 0,
            "userId": id,
            "unitId": unitId}
        res = post(
            "https://padapp.msyk.cn/ws/common/homework/homeworkStatus",
            dataup,
            3,
            str(StartHWID) +
            '0')
        # print(res)
        if 'isWithdrawal' in res:
            pass
        else:
            if res.strip():
                try:
                    hwname = json.loads(res).get('homeworkName')
                    hwtp = json.loads(res).get('homeworkType')
                    SubCode = json.loads(res).get('subjectCode')
                    subject_name = SUBJECT_CODE_MAP.get(str(SubCode), "其他")
                    color = SUBJECT_COLORS.get(
                        subject_name, SUBJECT_COLORS['其他'])
                    StarttimeArray = time.localtime(
                        json.loads(res).get('startTime') / 1000)
                    StarttimePrint = time.strftime(
                        "%Y-%m-%d %H:%M:%S", StarttimeArray)
                    EndtimeArray = time.localtime(
                        json.loads(res).get('endTime') / 1000)
                    EndtimePrint = time.strftime(
                        "%Y-%m-%d %H:%M:%S", EndtimeArray)
                    print(
                        Style.BRIGHT +
                        Fore.BLUE +
                        str(StartHWID) +
                        " 作业类型:" +
                        str(hwtp) +
                        " " +
                        Style.BRIGHT +
                        color +
                        "[" +
                        subject_name +
                        "]" +
                        " " +
                        Fore.BLUE +
                        hwname +
                        Style.NORMAL +
                        Fore.RED +
                        " 开始时间:" +
                        Fore.BLUE +
                        " " +
                        StarttimePrint +
                        Fore.RED +
                        " 截止时间:" +
                        Fore.BLUE +
                        " " +
                        EndtimePrint)
                except json.JSONDecodeError as e:
                    print("JSON格式错误:", e)
            else:
                print("res为空，跳过解析")

        if StartHWID == EndHWID:
            print(Fore.CYAN + "跑作业id结束 当前作业id为" + str(StartHWID))
            break
        StartHWID += 1


def MainMenu():
    ProfileImport = ""
    print(Fore.MAGENTA + "1.作业获取答案(默认)\n2.跑作业id\n3.切换账号\n4.退出")
    # print(Fore.MAGENTA + "5.消息系统\n6.学习圈系统")  # 取消注释以启用额外功能
    Mission = input(Fore.RED + "请选择要执行的任务:")
    if Mission == "2":
        getUnreleasedHWID()
    elif Mission == "3":
        open("ProfileCache.txt", "w", encoding='utf-8').write("")
        print(Fore.CYAN + "已清空 ProfileCache 登录缓存。")
        ProfileImport = input(Fore.CYAN + "请提供登录信息(如无则执行账号密码登录):")
        try:
            setAccountInform(ProfileImport)
        except BaseException:
            login()
    elif Mission == "4":  # 新增退出选项
        print(Fore.GREEN + "程序已退出")
        exit(0)
    # 取消以下注释以启用消息系统和学习圈系统
    # elif Mission == "5":
    #    msyk_message.message_menu(id, unitId)
    # elif Mission == "6":
    #    msyk_learning_circle.learning_circle_menu(id, unitId)
    else:
        getAnswer()


Start = getAccountInform()

dataup = {
    "studentId": id,
    "subjectCode": None,
    "homeworkType": -1,
    "pageIndex": 1,
    "pageSize": 36,
    "statu": 1,
    "homeworkName": None,
     "unitId": unitId}
res = post(
    "https://padapp.msyk.cn/ws/student/homework/studentHomework/getHomeworkList",
    dataup,
    2,
    "-11361")
if res.strip():
    try:
        reslist = json.loads(res).get('sqHomeworkDtoList')  # 作业list
    except json.JSONDecodeError as e:
        print("JSON格式错误:", e)
else:
    Choice = input("res为空，是否重新解析(默认是，否请输入1):")
    if Choice == "1":
        print("The program will be ended.")
    else:
        dataup = {
            "studentId": id,
            "subjectCode": None,
            "homeworkType": -1,
            "pageIndex": 1,
            "pageSize": 36,
            "statu": 1,
            "homeworkName": None,
            "unitId": unitId}
        res = post(
            "https://padapp.msyk.cn/ws/student/homework/studentHomework/getHomeworkList",
            dataup,
            2,
            "-11361")
        if res.strip():
            try:
                reslist = json.loads(res).get('sqHomeworkDtoList')  # 作业list
            except json.JSONDecodeError as e:
                print("JSON格式错误:", e)
        else:
            print("res仍然为空，美师优课是傻逼")
# print(res)

# 优化后的打印函数


def print_homework_item(item, timePrint):
    """作业项打印函数"""
    subject_name = str(item['subjectName'])
    # 如果科目名称在反向映射中，获取更准确的颜色
    subject_code = SUBJECT_NAME_TO_CODE.get(subject_name, "")
    if subject_code:
        # 如果有科目代码，使用科目代码映射获取科目名称（确保一致性）
        subject_name = SUBJECT_CODE_MAP.get(subject_code, subject_name)
    color = SUBJECT_COLORS.get(subject_name,
                               SUBJECT_COLORS['其他'])  # 使用字典获取颜色，默认为其他颜色
    print(
        Fore.YELLOW + str(item['id']) +
        " 作业类型:" + str(item['homeworkType']) + " " +
        Style.BRIGHT + color + "[" + subject_name + "]" +
        Style.NORMAL + Fore.YELLOW + " " + item['homeworkName'] +
        " 截止时间:" + timePrint
    )


# 打印业类型7的作业
for item in reslist:
    if str(item['homeworkType']) == '7':
        timeArray = time.localtime(item['endTime'] / 1000)
        timePrint = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
        print_homework_item(item, timePrint)

print(Fore.BLUE + "以下为阅读作业及其他作业，可能无答案且不需提交")

# 打印非作业类型7的作业
for item in reslist:
    if str(item['homeworkType']) != '7':
        timeArray = time.localtime(item['endTime'] / 1000)
        timePrint = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
        print_homework_item(item, timePrint)

while roll == 1:
    MainMenu()
