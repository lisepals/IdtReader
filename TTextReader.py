# -*- coding: cp1252 -*-
# ------------------------------------------------------------------------
# Date   : 2017-11-27
# Auteur : Lise Palacios
# Objet  : Initialization by AutoProg
# ------------------------------------------------------------------------
# ------------------------------------------------------------------------
# Imports
# ------------------------------------------------------------------------
import sys ;
import re  ;
import collections as col ;

# --- My imports
import LiseUtils as lu ;
import TTable    as tt ;
import TRecord   as tr ;

import TTextCursor    as txc ;
import TTextLexem     as ttlx;
import TLexemAnalyzer as tla ;
import TTextRule      as trl ;

import TLogProcessor  as tlp ;

from LiseUtils import xmsg, xerr, dmsg ;
# ------------------------------------------------------------------------
#   * Three tightly coupled classes
# ------------------------------------------------------------------------


# ========================================================================
#   * A text lexical analyzer
# ========================================================================

class TTextLexer (object) :

    # --------------------------------------------------------------------
    # * Protected
    # --------------------------------------------------------------------
    def join (self) :
        sWord = ''.join (self.pBuf) ;
        self.pBuf = [] ;
        return (sWord) ;
 
    def emit_one_char_lexem (self, pCh) :
        # --- Emit a one char lexem. can be only a PUNCT ou SPACE Type
        self.pLexReg = ttlx.TTextLexem (pCh['TYPE'], pCh['CHAR'], 1) ;
        
    def emit_word_lexem (self) :
        # --- Emit a one char lexem. can be only a PUNCT ou SPACE Type
        self.pLexReg = ttlx.TTextLexem ('TWORD', 
                                        self.join (), self.pLengthReg) ;
        self.pLengthReg = 0 ;
        
    def emit_eof_lexem (self) :
        # --- Emit the EoF lexem.
        return ttlx.TTextLexem ('EOF', 'EOF', 0) ;

    def init_state (self, pCh) :
        # --- Processing while in S_INIT state
        if pCh['TYPE'] in ['COM', 'FRENCH'] :
            self.sState = 'S_WORD' ;
            self.pBuf.append (pCh['CHAR']) ;
            self.pLengthReg += 1 ;
        else :
            # --- Emit a 1 char lexem
            self.emit_one_char_lexem (pCh) ;

    def word_state (self, pCh) :
        # --- Processing while in S_WORD state
        if pCh['TYPE'] in ['COM', 'FRENCH'] :
            self.pBuf.append (pCh['CHAR']) ;
            self.pLengthReg += 1 ;
        elif pCh['TYPE'] in ['PUNCT', 'SPACE'] :
            self.pCursor.ungetch () ;
            self.sState = 'S_INIT' ;
            self.emit_word_lexem () ;

    # --------------------------------------------------------------------
    # * Interface
    # --------------------------------------------------------------------

    def init_stream (self, pText) :
        # --- returns a generator over a stream of lexems
        self.pCursor.init_cursor (pText) ;
        self.sState = 'S_INIT' ;
        # --- bDone is True if EoF has been reached, otherwise it's False
        self.bDone = False ;
        self.pBuf  = [] ;

    def next_lexem (self) :
        while not self.bDone :
            ch = self.pCursor.getch () ;
            if ch :
                pCh = self.pCharsTable[ord(ch)] ;
                assert (pCh) ;
                if self.sState == 'S_INIT' :
                    self.init_state (pCh) ;
                elif self.sState == 'S_WORD' :
                    self.word_state (pCh) ;
                else :
                    sMsg = "Bad State in TextLexer." ;
                    lu.xerr (lu.ERFATAL, sMsg) ;
                if self.pLexReg :
                    pLexem = self.pLexReg ;
                    self.pLexReg = None ;
                    return pLexem ;
            else :
                # --- ch == None : EoF has been reached.
                if self.sState == 'S_WORD' :
                    # --- A word (the last one) was being accumulated
                    self.sState = 'S_END' ;
                    self.bDone = True ;
                    self.emit_word_lexem () ;
                    pLexem = self.pLexReg ;
                    self.pLexReg = None ;
                    return pLexem ;
                else :
                    self.bDone = True ;
                    self.sState = 'S_END' ;
        # --- If EOF or bDone == True
        return self.emit_eof_lexem () ;

    def get_lexem (self) :
        pLex = self.next_lexem () ;
        # --- Discard TSPACE lexems
        while pLex.type() == 'TSPACE' :
            pLex = self.next_lexem () ;
        return pLex ;

    # --------------------------------------------------------------------
    # * Initialization
    # --------------------------------------------------------------------

    def load_chars_table (self) :
        # --- Open a table of records
        # >>> To modify later
        sPath = "/usr/local/python/TextReader/Ress" ;
        sName = "chars_1.csv" ;
        pTable  = tt.TTable.create_table (lu.mk_url (sPath, sName)) ;
        pFields = pTable.get_fields_list () ;
        for pRec in pTable :
            pNewObj = tr.TRecord.from_record (pFields, pRec) ;
            iKey = lu.atoi (pNewObj['CHAR_ID']) ;
            pNewObj['ID']   = iKey ;
            pNewObj['CHAR'] = chr(iKey) ;
            self.pCharsTable[iKey] = pNewObj ;
        # --- Here, table has been created
        tlp.ixmsg (6, 45, ". Chars table created.") ;

    def __init__ (self) :
        # - Declarations
        # --- table of characters
        self.pCharsTable = {} ;
        # --- Open a table of records and convert it to a table of records
        self.load_chars_table () ;
        # --- Reference to a TTextCursor instance
        self.pCursor = txc.TTextCursor () ;
        # --- A buffer to store words and other cumulative lexems
        self.pBuf = [] ;
        # --- The Lexem register
        self.pLexReg = None ;
        # --- The Lexem length register
        self.pLengthReg = 0 ;
        # --- EoF marker
        self.bDone = False ;
        
# ========================================================================
#   * A text reader
# ========================================================================

class TTextReader (object) :

    # --------------------------------------------------------------------
    # * Protected
    # --------------------------------------------------------------------

    # --- This method call repeteadly le lexer and discard all TSPACES
    #     type lexems
    def get_lexem (self) :
        return self.pLexer.get_lexem () ;

    def add_lexem_to_deque (self) :
        pNewLex = self.get_lexem () ;
        if self.bEoF == False :
            if pNewLex.type() == 'EOF' :
                self.pDq.append (pNewLex) ;
                self.bEoF = True ;
            else :
                if pNewLex.type() == 'TWORD' :
                    self.pAnalyser.analyze (pNewLex) ;
                # >>>> lu.msg (sys.stdout, 65, "pt1 : %r", pNewLex) ;
                self.pDq.append (pNewLex) ;

    def test_prefix (self) :
        sPrefix = self.pDq[0].type() ;
        if self.pRules.has_key (sPrefix) :
            pRules = self.pRules[sPrefix] ;
            for pRule in pRules :
                if pRule.apply (self.pDq) == True :
                    return ;

    def get_front_lexem (self) :
        self.test_prefix () ;
        # --- Get the first lexem
        pLex = self.pDq.popleft () ;
        # --- Add lexem to queue
        self.add_lexem_to_deque () ;
        return pLex ;

    # --- Initializes a deque to allow the multi-lexems analyzis
    def init_deque (self) :
        self.pDq = col.deque() ;
        for i in range (0, 10) :
            pLex = self.get_lexem () ;
            if pLex.type() == 'TWORD' :
                self.pAnalyser.analyze (pLex) ;
            # --- lu.msg (sys.stdout, 65, "pt0 : %r", pLex) ;
            self.pDq.append (pLex) ;
            if pLex.type() == 'EOF' :
                return ;

    def get_syntagm (self) :
        # --- This method returns a stream of analyzed lexems (pre-syntagms)
        try :
            return self.get_front_lexem () ;
        except IndexError :
            return None ;

    # --- Initialization of the Rules table
    def add_rule (self, pRulesTable, sPrefix, pRule) :
        try :
            pRulesTable[sPrefix].append (pRule) ;
        except KeyError :
            pRulesTable[sPrefix] = [] ;
            pRulesTable[sPrefix].append (pRule) ;

    def init_rules (self) :
        pRules = {} ;
        # --- The Paragraph mark
        pR1Nexts = ['TNL'] ;
        pR1 = trl.TParg_Rule (self.pLexer, self.pAnalyser, 'TNL', pR1Nexts) ;
        self.add_rule (pRules, 'TNL', pR1) ;

        pRf1Nexts = ['TTG', 'TNUM', 'TBG'] ;
        pRf1 = trl.TRf1_Rule (self.pLexer, self.pAnalyser, 'TNUM', pRf1Nexts) ;
        self.add_rule (pRules,'TNUM', pRf1) ;

        pRf2Nexts = ['TNUM', 'TBG'] ;
        pRf2 = trl.TRf2_Rule (self.pLexer, self.pAnalyser, 'TNUM', pRf2Nexts) ;
        self.add_rule (pRules,'TTG', pRf2) ;

        pRf3Nexts = ['TSPECIAL'] ;
        pRf3 = trl.TRf3_Rule (self.pLexer, self.pAnalyser, 'TTG', pRf3Nexts) ;
        self.add_rule (pRules,'TTG', pRf3) ;

        pApNexts = ['TAP'] ;
        pAp = trl.TAp_Rule (self.pLexer, self.pAnalyser, 'TAPPWORD', pApNexts) ;
        self.add_rule (pRules,'TAPPWORD', pAp) ;

        pPapsNexts = ['TNN'] ;
        pPaps = trl.TPaps_Rule (self.pLexer, self.pAnalyser, 'TAUXAV', pPapsNexts) ;
        self.add_rule (pRules, 'TAUXAV', pPaps) ;

        pPapsNexts = ['TNN'] ;
        pPaps = trl.TPaps_Rule (self.pLexer, self.pAnalyser, 'TAUXET', pPapsNexts) ;
        self.add_rule (pRules, 'TAUXET', pPaps) ;

        pVerb1Nexts = ['TNN'] ;
        pVerb1 = trl.TVerb1_Rule (self.pLexer, self.pAnalyser, 'TPP', pVerb1Nexts) ;
        self.add_rule (pRules, 'TPP', pVerb1) ;

        return pRules ;

    # --------------------------------------------------------------------
    # * Interface
    # --------------------------------------------------------------------

    def get_stream_from_file (self, sFileName) :
        # --- This function returns a generator object to a stream of
        #     lexems
        # Args :
        #      sFileName (str) : Full URL of the input file
        # RetV :
        #      a generator object to a stream of lexems
        sOpMsg = "  + File %s opened, reading mode." ;
        sClMsg = "  + File %s closed." ;
        hIn = lu.open_file (sFileName, 'r') ;
        lu.xmsg (65, sOpMsg, sFileName) ;
        self.pLexer.init_stream (hIn.readlines()) ;
        hIn.close () ;
        self.init_deque () ;
        # --- The rules to apply
        self.pRules = self.init_rules () ;
        while True :
            pLex = self.get_syntagm () ;
            if pLex :
                # --- lu.msg (sys.stdout, 45, "%r", pLex) ;
                yield pLex ;
            else :
                raise (StopIteration) ;

    def get_stream_from_string (self, pText) :
        # --- This function returns a generator object to a stream of
        #     lexems
        # Args :
        #      pText : The text to analyze
        # RetV :
        #      a generator object to a stream of lexems
        self.pLexer.init_stream (pText) ;
        self.init_deque () ;
        # --- The rules to apply
        self.bEoF = False ;
        while True :
            pLex = self.get_syntagm () ;
            # --- lu.msg (sys.stdout, 45, "%r", pLex) ;
            if pLex :
                yield pLex ;
            else :
                raise (StopIteration) ;

    # --------------------------------------------------------------------
    # * Initialization
    # --------------------------------------------------------------------

    def __init__ (self) :
        # --- Declarations
        self.pLexer = TTextLexer () ;
        tlp.ixmsg (6, 75, ". TextLexer created.") ;
        # --- On initialize un TTextLexemAnalyzer
        # >>> import pdb; pdb.set_trace () ;
        self.pAnalyser = tla.TTextLexemAnalyzer () ;
        # --- Une deque pour l'analyse multi-lexeme
        self.bEoF = False ;
        self.pDq  = None ;
        # --- The rules to apply
        self.pRules = self.init_rules () ;
