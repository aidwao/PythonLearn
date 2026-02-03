import regex

def check_text_is_in_length_limit(text: str, max_length: int, min_length:int=0, custom_minimum_max_length:int=-1) -> bool:
	"""
	兼容阿拉伯及泰语的文本长度判断，忽略掉音标字符
	custom_minimum_max_length: 自定义保底最大长度，避免玩家非法利用组合字符，如果为-1则采用max_length * 4
	"""
	minimum_max_length = max_length * 4 if custom_minimum_max_length == -1 else custom_minimum_max_length
	minimum_min_length = 0
	origin_length = get_chinese_text_length_old(text)
	if origin_length < minimum_min_length or origin_length > minimum_max_length:
		return False
	display_length = get_display_length(text)
	return display_length >= min_length and display_length <= max_length

def get_specify_len_display_text(text: str, max_length: int, custom_minimum_max_length:int=-1) -> str:
	"""获取指定长度以内的显示文本"""
	temp_str = text
	minimum_max_length = max_length * 4 if custom_minimum_max_length == -1 else custom_minimum_max_length
	origin_length = get_chinese_text_length_old(text)
	if origin_length > minimum_max_length:
		temp_str = text[0:minimum_max_length]
	while(get_display_length(temp_str) > max_length):
		temp_str = temp_str[0:-1]
	return temp_str

def get_chinese_text_length_old(text: str) -> int:
	""" 获取字符串长度，中日韩算两个字符 """
	len_str = len(text)
	len_str_utf8 = len(text.encode('utf-8'))
	size = int((len_str_utf8 - len_str) / 2 + len_str)
	return size

def get_display_length(s: str) -> int:
	"""
	计算字符串在等宽字体下的显示宽度
	"""
	try:
		import unicodedata
	except:
		from unreal_engine import log_warning
		log_warning("unicodedata module not found")
		return get_chinese_text_length_old(s)
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
print(f"chinese result:", get_chinese_text_length_old(s))
print(f"'{s}'  显示宽度: {get_display_length(s)=}")  # 9

# test user