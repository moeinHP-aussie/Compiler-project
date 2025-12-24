class Lexer:
    
    def __init__(self, code: str):
        self.code = code                # متن کامل فایل ورودی
        self.pos = 0                    # موقعیت فعلی پیمایش در ورودی
        self.len = len(code)            # طول کل کد
        self.line = 1                   # شماره خط فعلی - استفاده شده در جدول توکن‌ها
        self.symbol_table = {}          # جدول شناسه‌ها برای ذخیره متغیرها

        
        self.keywords = {'for', 'if', 'while' , 'print'} #کلمات کلیدی قابل شناسایی
        
        # کاراکترهای مجاز : 
        self._digits = set('0123456789')
        self._letters = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ')
        self._ident_start = self._letters | {'_'}  # کاراکتر شروع  شناسه
        self._ident_part = self._ident_start | self._digits # ادامه ی شناسه
        
        # کاراکترهای فضای خالی که باید نادیده گرفته شوند
        self._whitespace = {' ', '\t', '\n'} 

        # اوپریشن ها
        self._single_ops = {'+', '-', '*', '/', '%'}   
        self._assign_op = {'='}                       
        self._delimiters = {':', ';', '(', ')', '{', '}', '[', ']', ',', '.'} 
        self._relops_two_char = {'>=', '<=', '==', '!='} 
        self._relops_one_char = {'>', '<'}               

        # لیست نهایی توکن‌ها که توسط لکسر پر میشخ
        self._tokens = []



    def _peek(self, offset=0): # offset = فاصله از شروع کاراکتر
        """
        سرکشی از کاراکتر جلوتر 
        """
        i = self.pos + offset
        return self.code[i] if i < self.len else None

    def _advance(self, n=1):
        """
        جلو بردن پوینتر 
        """
        for _ in range(n):
            if self.pos >= self.len:
                return
            ch = self.code[self.pos]
            self.pos += 1
            if ch == '\n':
                self.line += 1 # آپدیت شماره خط

    def _add_token(self, text, tok_type, line):
        self._tokens.append((text, line, tok_type))

    def _is_at_end(self):
        return self.pos >= self.len


    #توابع  پردازش کاراکترها:
    
    def _consume_comment_slash(self, line): # پردازش کامنت های // برای Cpp
        start = self.pos
        self._advance(2) # رد کردن خودِ //
        while self._peek() is not None and self._peek() != '\n':
            self._advance()
        text = self.code[start:self.pos]
        self._add_token(f"comment({text})", 'comment', line)

    def _consume_comment_hash(self, line): # پردازش کامنت های # برای پایتون
        start = self.pos
        self._advance() # رد کردن خودِ علامت هش
        while self._peek() is not None and self._peek() != '\n':
            self._advance()
        text = self.code[start:self.pos]
        self._add_token(f"comment({text})", 'comment', line)

    def _consume_identifier_or_keyword(self, line):
        """
        پردازش و تشخیص کلمات کلیدی و شناسه ها - keyword & identifier
        """
        start = self.pos
        self._advance()  
        # مصرف ادامه شناسه :
        while self._peek() is not None and self._peek() in self._ident_part:
            self._advance()
        value = self.code[start:self.pos]
        
        # بررسی کلمه کلیدی بودن 
        if value in self.keywords:
            self._add_token(f"keyword({value})", 'keyword', line)
        else:
            # بررسی شناسه بودن
            if value not in self.symbol_table:
                self.symbol_table[value] = len(self.symbol_table) + 1
            self._add_token(f"id({value})", 'id', line)

    def _consume_number(self, line):
        """
        پردازش اعداد صحیح، اعشاری و نمایی
        """
        start = self.pos
        
        #  قسمت صحیح
        while self._peek() is not None and self._peek() in self._digits:
            self._advance()
        
        # قسمت اعشاری
        if self._peek() == '.' and self._peek(1) in self._digits:
            self._advance()  # مصرف '.'
            while self._peek() is not None and self._peek() in self._digits:
                self._advance()
        
        #  نمایی (e یا E)
        if self._peek() in ('e', 'E'):
            self._advance() # مصرف 'e'
            if self._peek() in ('+', '-'): 
                self._advance()
            
            # باید حداقل یک عدد بعد از نما بیاید
            if self._peek() is None or self._peek() not in self._digits:
                value = self.code[start:self.pos]
                self._add_token(f"lexical error({value})", 'error', line)
                return
            # مصرف رثم
            while self._peek() is not None and self._peek() in self._digits:
                self._advance()
        
        
        value = self.code[start:self.pos]
        self._add_token(f"num({value})", 'number', line)



    #----> بدنه اصلی کلاس برای پیمایش کل فایل
    
    def tokenize(self):
        
        # ریست کردن وضعیت اولیه برای استفاده های مجدد
        self._tokens = []
        self.pos = 0
        self.line = 1
        self.symbol_table = {}

        while not self._is_at_end():
            ch = self._peek()

            # فضاهای خالی و خطوط جدید را رد می‌کنیم
            if ch in self._whitespace:
                self._advance()
                continue 

            """ اگر کاراکتر، فضای خالی نبود، قطعا شروع یک توکن است
            در نتیجه شماره خط فعلی را برای توکن جدید ذخیره می‌کنیم
            """
            line = self.line 

            # بررسی کامنت //
            if ch == '/' and self._peek(1) == '/':
                self._consume_comment_slash(line)
                continue # کار این دور حلقه تمام شد

            # بررسی کامنت '#'
            if ch == '#':
                self._consume_comment_hash(line)
                continue 

            # بررسی شناسه‌ها و کلمات کلیدی
            if ch in self._ident_start:
                self._consume_identifier_or_keyword(line)
                continue

            # بررسی اعداد
            if ch in self._digits or (ch == '.' and self._peek(1) in self._digits):
                self._consume_number(line)
                continue


            """باید حتما اول عملگر دو کاراکتری بررسی بشه و بعد عملگر تک کاارکتری
            درغیر اینصورت توکن سازی اشتباه رخ میده"""

            # بررسی عملگرهای رابطه‌ای دو کاراکتری
            two_char = ch + (self._peek(1) or '')
            if two_char in self._relops_two_char:
                self._add_token(f"relop({two_char})", 'relop', line)
                self._advance(2) 
                continue

            # بررسی عملگرهای رابطه‌ای تک کاراکتری 
            if ch in self._relops_one_char:
                self._add_token(f"relop({ch})", 'relop', line)
                self._advance()
                continue

            # بررسی عملگر انتساب
            if ch in self._assign_op:
                self._add_token(f"op({ch})", 'op', line)
                self._advance()
                continue

            # بررسی عملگرهای حسابی
            if ch in self._single_ops:
                self._add_token(f"op({ch})", 'op', line)
                self._advance()
                continue

            # بررسی جداکننده‌ها
            if ch in self._delimiters:
                self._add_token(f"delimiter({ch})", 'delimiter', line)
                self._advance()
                continue

            # خطای لغوی
            self._add_token(f"lexical error({ch})", 'error', line)
            self._advance() 




        return self._tokens, self.symbol_table