class GrammarAnalyzer:
    def __init__(self, grammar, start_symbol, epsilon="ε", eof="$"):
        self.grammar = grammar
        self.start = start_symbol #نماد شروع گرامر
        self.epsilon = epsilon
        self.eof = eof

        self.non_terminals = set(grammar.keys())
        
        #ساخت مجموعه خالی فرست و فالو برای هر نان_ترمینال
        self.first = {nt: set() for nt in self.non_terminals}
        self.follow = {nt: set() for nt in self.non_terminals}
        
        self.follow[self.start].add(self.eof)

    # -----------------------------------------------------
    # --------------------توایع کمکی----------------
    # ------------------------------------
    
    def is_terminal(self, symbol):
        # terminal = Anything that not epsilon or terminal
        return symbol not in self.non_terminals and symbol != self.epsilon


    def get_first(self, symbol):

        if symbol == self.epsilon:
            return {self.epsilon}
            
        if self.is_terminal(symbol):
            return {symbol}
        
        return self.first[symbol]
    

    def _get_first_of_sequence(self, sequences):
    #محاسبه فرست یک دنباله 
        result = set()
        for symbol in sequences:
            fst = self.get_first(symbol)
            
            # همه را اضافه کن جز اپسیلون
            result.update(fst - {self.epsilon})
            
            if self.epsilon not in fst:
                break
        else:
            result.add(self.epsilon)
        return result
    

    def _find_nonterminal_occurrences(self, production):
        # این تابع تو محاسبه فالو ها لازممون میشه
        # find B and betha in "A --> ...'B' beta"
        result = []
        production_symbols = production.split()
        for i, symbol in enumerate(production_symbols):
            if symbol in self.non_terminals:
                beta = production_symbols[i + 1:]
                result.append((symbol, beta))
        return result

    # ---------------------------------------------------------
    # ---------------------- FIRST SETS --------------
    # -------------------------------------------

    def compute_first_sets(self): 
        
        changed = True
        """ 
    فلگ برای بررسی مجدد فرست تمام
    نان ترمینال ها وقتی که یکیشون تغییر کنه
    """
        while changed:
            changed = False
            for A in self.non_terminals:
                for rule_str in self.grammar[A]:
                    
                    # محاسبه First برای سمت راست قانون
                    rule_symbols = rule_str.split()
                    rule_first = self._get_first_of_sequence(rule_symbols)

                    # اضاف»نه کردن به مجموعه First فعلی A
                    before_count = len(self.first[A])
                    self.first[A].update(rule_first)
                    if len(self.first[A]) > before_count:
                        changed = True

    # ---------------------------------------------------------
    # ---------------- FOLLOW SETS -----------------
    # --------------------------------------

    def _apply_follow_rules(self, A, B, beta):

        """
        اعمال قوانین 
        FOLLOW 
        برای
          A -> ... 'B'beta
        """
        if beta:
            ''' rule1 : Follow(B) += First(beta) - {ε}'''
            first_of_beta_seq = self._get_first_of_sequence(beta)
            self.follow[B].update(first_of_beta_seq - {self.epsilon})


            ''' rule2 : if epsilon be in First(beta) then
                --> Follow (B)=Follow(A)+follow(B)'''
            if self.epsilon in first_of_beta_seq:
                self.follow[B].update(self.follow[A])
        else: # بتا وجود نداشته باشه

            self.follow[B].update(self.follow[A])
            
    def compute_follow_sets(self):
        """اجرای کامل الگوریتم FOLLOW تا تثبیت همشون
          (FIXED-POINT algorithm)
          مسابه بخس محاسبه فرست ها"""
        
        self.compute_first_sets() #محاسبه تمام فرست هی گرامر

        changed = True # مشابه بخش محاسبه فرست ها
        while changed:
            changed = False
            
            for A in self.non_terminals: 
                for production_str in self.grammar[A]: 
                    
                    # پیدا کردن تمام الگوهای بدون نان ترمینال در سمت راست
                    occurrences = self._find_nonterminal_occurrences(production_str)
                    
                    # اجرای قوانین روی تک‌تک موارد B
                    for (nonterminal, beta) in occurrences:
                        before = len(self.follow[nonterminal])
                        self._apply_follow_rules(A, nonterminal, beta)

                        if len(self.follow[nonterminal]) > before:
                            changed = True




    # ---------------------------------------------------------




if __name__ == "__main__":
    test_grammar = { 
        'E': ['T E\''], 
        'E\'': ['+ T E\'', 'ε'], 
        'T': ['F T\''], 
        'T\'': ['* F T\'', 'ε'], 
        'F': ['( E )', 'id'] 
    }

    analyzer = GrammarAnalyzer(test_grammar, start_symbol='E')
    analyzer.run()