import regex
import unicodedata


import unicodedata

def get_display_width(s: str) -> int:
    """
    计算字符串在等宽字体下的显示宽度
    """
    width = 0
    for char in s:
        category = unicodedata.category(char)
        """
        Mn : (Mark, nonspacing) 非间距标记，组合标记类型，完全不占用额外空间
        Mc : (Mark, spacing combining) 间距组合标记，基础字符组合，
        组合后看起来是一个字符，未组合则看起来是两个字符，
        例如 க +  ி = கி ,unicode未组合的情况不会标记为Mc
        Me : (Mark, enclosing) 封闭标记，包围/环绕基础字符的标记 例如： 1⃣ = 1 +  ⃣
        """
        # 组合标记不占宽度
        if category in ('Mn', 'Mc', 'Me'):
            continue
        
        # 控制字符不占宽度(转义字符等)
        if category in ('Cc', 'Cf'):
            continue
            
        """
        East Asian Width 属性:
        - W (Wide): 宽字符，宽度 2(中日韩等)
        - F (Fullwidth): 全角字符，宽度 2
        - H (Halfwidth): 半角字符，宽度 1
        - Na (Narrow): 窄字符，宽度 1
        - A (Ambiguous): 模糊宽度，通常算 1
        - N (Neutral): 中性，宽度 1
        """
        ea_width = unicodedata.east_asian_width(char)
        # 宽字符（中日韩+Emoji）或者全角字符 占 2 宽度
        if ea_width in ('W', 'F'):
            width += 2
        else:
            width += 1
    return width


def get_len_chinese(chinese_str) -> int:
	"""获取中文字符串长度"""
	len_str = len(chinese_str)
	len_str_utf8 = len(chinese_str.encode('utf-8'))
	print(f"{len_str=}  {len_str_utf8=}")
	size = int((len_str_utf8 - len_str) / 2 + len_str)
	return size

# s = "المُعاقِب"
# s="中文"
# s="가나"
# s="かな"
# s = "கக ிகி"
s = "1⃣2⃣3⃣"
print("normal len:", len(s))
spilit_char_list = regex.findall(r'\X', s)
print("regex result:", len(spilit_char_list))
print(f"regex result: {spilit_char_list=}")
print(f"chinese result:", get_len_chinese(s))
print(f"'{s}'  显示宽度: {get_display_width(s)=}")  # 9