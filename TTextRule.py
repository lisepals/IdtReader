# -*- coding: cp1252 -*-
# ------------------------------------------------------------------------
# Date   : 2017-12-02
# Auteur : Lise Palacios
# Objet  : Initialization by AutoProg
# ------------------------------------------------------------------------
# ------------------------------------------------------------------------
# Imports
# ------------------------------------------------------------------------
import sys ;
import re  ;
import pdb ;

# --- My imports
import LiseUtils  as lu ;
import TTextLexem as tlx ;

from LiseUtils import msg, xmsg, xerr ;
# ------------------------------------------------------------------------
#   * A Rule class to rule them all
# ------------------------------------------------------------------------

class TTextRule (object) :

    # --------------------------------------------------------------------
    # * Protected
    # --------------------------------------------------------------------
    def look_body_ahead (self, iNb) :
        return self.pDeque[iNb].body().lower() ;

    def look_type_ahead (self, iNb) :
        return self.pDeque[iNb].type() ;


    def add_lexem_to_deque (self, iNb) :
        bEoF = False ;
        for i in range (0, iNb) :
            pNewLex = self.pLexer.get_lexem () ;
            if bEoF == False :
                if pNewLex.type() == 'EOF' :
                    self.pDeque.append (pNewLex) ;
                    bEoF = True ;
                else :
                    if pNewLex.type() == 'TWORD' :
                        self.pAnalyzer.analyze (pNewLex) ;
                    self.pDeque.append (pNewLex) ;

    def apply_rule (self) :
        return None ;
    # --------------------------------------------------------------------
    # * Interface
    # --------------------------------------------------------------------

    def apply (self, pDeque) :
        # --- Test if given the current prefix, we have the correct 
        #     continuation
        # --- Current lexel is pDeque[0]
        self.pDeque = pDeque ;
        bTest = True ;
        for i, sType in enumerate (self.pNextTypes) :
            j = i + 1 ;
            if self.pDeque[j].type() != sType :
                bTest = False ;
        if bTest :
            return self.apply_rule () ;

    # --------------------------------------------------------------------
    # * Initialization
    # --------------------------------------------------------------------

    def __init__ (self, pLexer, pAnalyzer, sPrefix, pNextTypes) :
        self.sPrefix    = sPrefix ;
        self.pNextTypes = pNextTypes ;
        self.pLexer     = pLexer ;
        self.pAnalyzer  = pAnalyzer ;

# ------------------------------------------------------------------------
#   * This rule merge two TNL lexems to a TPARG one
#   * Two consecutine TNL are condidered an End of Paragraph
# ------------------------------------------------------------------------

class TParg_Rule (TTextRule) :

    # --------------------------------------------------------------------
    # * Protected : paragraph sign : chr(244)
    # --------------------------------------------------------------------

    def apply_rule (self) :
        self.pDeque.popleft () ;
        self.pDeque.popleft () ;
        pNewLex = tlx.TTextLexem ('TPARG', chr(244), 1) ;
        self.pDeque.appendleft (pNewLex) ;
        self.add_lexem_to_deque (1) ;
        return True ;

    # --------------------------------------------------------------------
    # * Initialization
    # --------------------------------------------------------------------

    def __init__ (self, pLexer, pAnalyzer, sPrefix, pNextTypes) :
        TTextRule.__init__ (self,
                            pLexer, pAnalyzer, sPrefix, pNextTypes);

# ------------------------------------------------------------------------
#   * This rule merge Four lexems to a TRF one
#   * TNUM    TTG     TNUM   TBG
#   * Tranche Trigram Repere Bigram
# ------------------------------------------------------------------------

class TRf1_Rule (TTextRule) :

    # --------------------------------------------------------------------
    # * Protected
    # --------------------------------------------------------------------

    def apply_rule (self) :
        iMaxNb = 4 ;
        pLxms = [self.pDeque.popleft () for i in range (0, iMaxNb)] ;
        pStr  = [pLxm.lower () for pLxm in pLxms] ;
        sStr  = ''.join (pStr) ;
        iLen  = sum ([len(pLxm) for pLxm in pLxms]) ;
        pNewLex = tlx.TTextLexem ('TRF', sStr, iLen) ;
        self.pDeque.appendleft (pNewLex) ;
        self.add_lexem_to_deque (iMaxNb) ;
        return True ;
    # --------------------------------------------------------------------
    # * Initialization
    # --------------------------------------------------------------------

    def __init__ (self, pLexer, pAnalyzer, sPrefix, pNextTypes) :
        TTextRule.__init__ (self,
                            pLexer, pAnalyzer, sPrefix, pNextTypes);

# ------------------------------------------------------------------------
#   * This rule merge 3 lexems to a TRF one
#   * TTG     TNUM   TBG
#   * Trigram Repere Bigram
# ------------------------------------------------------------------------

class TRf2_Rule (TTextRule) :

    # --------------------------------------------------------------------
    # * Protected
    # --------------------------------------------------------------------
    def apply_rule (self) :
        sStr3 = self.look_body_ahead (3) ;
        sStr4 = self.look_type_ahead (4) ;
        if sStr3[0] == 'g' and sStr4 == 'TNUM' :
            # --- Probably the declaration of a STE event
            return False ;
        iMaxNb = 3 ;
        pLxms = [self.pDeque.popleft () for i in range (0, iMaxNb)] ;
        pStr  = [pLxm.lower () for pLxm in pLxms] ;
        sStr  = ''.join (pStr) ;
        iLen  = sum ([len(pLxm) for pLxm in pLxms]) ;
        pNewLex = tlx.TTextLexem ('TRF', sStr, iLen) ;
        self.pDeque.appendleft (pNewLex) ;
        self.add_lexem_to_deque (iMaxNb) ;
        # lu.msg (sys.stdout, 65, "  * In TRf2_Rule.") ;
        return True ;

    # --------------------------------------------------------------------
    # * Initialization
    # --------------------------------------------------------------------

    def __init__ (self, pLexer, pAnalyzer, sPrefix, pNextTypes) :
        TTextRule.__init__ (self,
                            pLexer, pAnalyzer, sPrefix, pNextTypes);

# ------------------------------------------------------------------------
#   * This rule merge 3 lexems to a TRF one
#   * TTG     TNUM   TBG
#   * Trigram Repere Bigram
# ------------------------------------------------------------------------

class TRf3_Rule (TTextRule) :

    # --------------------------------------------------------------------
    # * Protected
    # --------------------------------------------------------------------

    def apply_rule (self) :
        iMaxNb = 2 ;
        pLxms = [self.pDeque.popleft () for i in range (0, iMaxNb)] ;
        pStr  = [pLxm.lower () for pLxm in pLxms] ;
        sStr  = ''.join (pStr) ;
        iLen  = sum ([len(pLxm) for pLxm in pLxms]) ;
        pNewLex = tlx.TTextLexem ('TRF', sStr, iLen) ;
        self.pDeque.appendleft (pNewLex) ;
        self.add_lexem_to_deque (iMaxNb) ;
        # lu.msg (sys.stdout, 65, "  * In TRf3_Rule.") ;
        return True ;

    def apply (self, pDeque) :
        # --- Test if given the current prefix, we a the correct 
        #     continuation
        # --- Current lexel is pDeque[0]
        self.pDeque = pDeque ;
        bTest = True ;
        for i, sType in enumerate (self.pNextTypes) :
            j = i + 1 ;
            if self.pDeque[j].type() != sType :
                bTest = False ;
        if bTest :
            sStr = self.pDeque[0].lower ()[-2:] ;
            if len(sStr) > 5 :
                return False ;
            if re.match ('[0-9]{2}', sStr, re.I) :
                return self.apply_rule () ;
            return False ;
    # --------------------------------------------------------------------
    # * Initialization
    # --------------------------------------------------------------------

    def __init__ (self, pLexer, pAnalyzer, sPrefix, pNextTypes) :
        TTextRule.__init__ (self, 
                            pLexer, pAnalyzer, sPrefix, pNextTypes);

# ------------------------------------------------------------------------
#   * This rule merge a TAPWORD lexem and a TAP one to get reed of TAP lexems
#   * TAPPWORD TAP
# ------------------------------------------------------------------------

class TAp_Rule (TTextRule) :

    # --------------------------------------------------------------------
    # * Protected
    # --------------------------------------------------------------------

    def apply_rule (self) :
        pLex1  = self.pDeque.popleft () ;
        pLex2 = self.pDeque.popleft () ;
        sRes  = "%s'" % pLex1.lower () ;
        pNewLex = tlx.TTextLexem ('TWORD', sRes, len(pLex1)+1) ;
        self.pAnalyzer.analyze (pNewLex) ;
        self.pDeque.appendleft (pNewLex) ;
        self.add_lexem_to_deque (1) ;
        return True ;

    # --------------------------------------------------------------------
    # * Initialization
    # --------------------------------------------------------------------

    def __init__ (self, pLexer, pAnalyzer, sPrefix, pNextTypes) :
        TTextRule.__init__ (self,
                            pLexer, pAnalyzer, sPrefix, pNextTypes);

# ------------------------------------------------------------------------
#   * This rule tries to identify passed particips
# ------------------------------------------------------------------------

class TPaps_Rule (TTextRule) :

    # --------------------------------------------------------------------
    # * Protected
    # --------------------------------------------------------------------

    def apply_rule (self) :
        pLex2 = self.pDeque[1] ;
        sDesc = pLex2.lower ()[-1] ;
        # --- 
        if sDesc in ['é', 'i', 'u'] :
            pLex2.set_type ('TPAPS') ;
            pLex2.set_stem (pLex2.lower ()[:-1]) ;
            return True ;
        return False ;

    # --------------------------------------------------------------------
    # * Initialization
    # --------------------------------------------------------------------

    def __init__ (self, pLexer, pAnalyzer, sPrefix, pNextTypes) :
        TTextRule.__init__ (self,
                            pLexer, pAnalyzer, sPrefix, pNextTypes);

# ------------------------------------------------------------------------
#   * This rule tries to identify simple experessions involving verbs
#     Le mot qui suit un TPP est toujours un verbe
# ------------------------------------------------------------------------

class TVerb1_Rule (TTextRule) :

    # --------------------------------------------------------------------
    # * Protected
    # --------------------------------------------------------------------

    def apply_rule (self) :
        pLex2 = self.pDeque[1] ;
        pLex2.set_type ('TVERB') ;
        return True ;

    # --------------------------------------------------------------------
    # * Initialization
    # --------------------------------------------------------------------

    def __init__ (self, pLexer, pAnalyzer, sPrefix, pNextTypes) :
        TTextRule.__init__ (self,
                            pLexer, pAnalyzer, sPrefix, pNextTypes);

