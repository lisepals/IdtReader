# -*- coding: cp1252 -*-
# ------------------------------------------------------------------------
# Date   : 2011-12-12
# Author : Lise Palacios
# Object : Parsing Firex for machine learning
#        : stemming now !
# ------------------------------------------------------------------------

# ------------------------------------------------------------------------
import sys
import os ;
import string ;
# ------------------------------------------------------------------------
# --- My imports
# ------------------------------------------------------------------------

# ------------------------------------------------------------------------
# Main part of the module
# ------------------------------------------------------------------------

class TFrenchStemmer (object) :

    # --------------------------------------------------------------------
    # * Protected
    # --------------------------------------------------------------------

    def comp_nb_syls (self, sWord) :
        # --- Retourne le nombre de syllabes dans sWord
        if len(sWord) <= 3 :
            return 0 ;
        pWordList = [] ;
        for ch in sWord :
            if ch in self.pVowels :
                pWordList.append ('V') ;
            else :
                pWordList.append ('C') ;
        i = 0 ;
        j = 1 ;
        m = 0 ;
        while j < len(pWordList) :
            if pWordList[i] == 'V' and pWordList[j] == 'C' :
                m += 1 ;
                i += 2 ;
                j += 2 ;
            else :
                i += 1 ;
                j += 1
        return m ;

    def test_suffix (self, iMinSyls, sSuffix, sWord) :
        # --- Test si suffixe possible
        if self.iNbSyls >= iMinSyls :
            iCutLen = len(sSuffix);
            if sWord[-iCutLen:] == sSuffix :
                return iCutLen ;
            return -1 ;
        return -1 ;

    def stem_pass_1 (self, sWord) :
        # --- Retire les pluriels et feminins
        pRules = [(1, 'ees'),
                  (1, 'ee'),
                  (1, 'es'),
                  (1, 's'),
                  (1, 'e')] ;

        iCutIndex = 0 ;
        for tRule in pRules :
            iCutLen = self.test_suffix (tRule[0], tRule[1], sWord) ;
            if iCutLen > iCutIndex :
                iCutIndex = iCutLen ;
        if iCutIndex == 0 :
            return sWord ;
        return sWord[:-iCutIndex] ;

    def stem_pass_3 (self, sWord) :
        # --- Supprime les doublons de lettres a la fin des racines
        if len(sWord) > 2 :
            if sWord[-1] == sWord[-2] :
                return sWord[:-1] ;
        return sWord ;


    # --------------------------------------------------------------------
    # * Interface
    # --------------------------------------------------------------------

    def stem (self, pLxm) :
        # --- Retourne la racine du mot fourni en argument
        #     le mot doit etre en minuscules

        if len (pLxm) > 0 :
            # --- \ before a string means a regular expression
            if pLxm[0] == '\\' :
                return pLxm ;

        pRules = [(2, 'er'),
                  (2, 'ir'),
                  (2, 'ez'),
                  (2, 'ag'),
                  (2, 'ait'),
                  (2, 'air'),
                  (2, 'ant'),
                  (2, 'ent'), 
                  (2, 'eur'), 
                  (2, 'ion'), 
                  (2, 'tion'),
                  (2, 'ement'),
                  (2, 'aient'),
                  (2, 'ation'),
                  (3, 'ilit')];

        sWord = pLxm.lower ().translate (self.pTransTable) ;
        iCutIndex = 0 ;
        self.iNbSyls = self.comp_nb_syls (sWord) ;
        sWordPass1 = self.stem_pass_1 (sWord) ;
        for pRule in pRules :
            iCutLen = self.test_suffix (pRule[0], pRule[1], sWordPass1) ;
            if iCutLen > iCutIndex :
                iCutIndex = iCutLen ;
        if iCutIndex > 0 :
            sWordPass2 = sWordPass1[:-iCutIndex] ;
        else :
            sWordPass2 = sWordPass1 ;
        if self.iNbSyls > 1 :
            return self.stem_pass_3 (sWordPass2) ;
        return sWordPass2 ;

    # --------------------------------------------------------------------
    # * Special methods
    # --------------------------------------------------------------------

    # --------------------------------------------------------------------
    # * Initialization
    # --------------------------------------------------------------------

    def make_trans_table (self) :
        # *** Build a translation tble to remove accentuated chars
        pFrom = "âàëéêèïîôûùÂÀËÉÊÈÏÎÔÛÙ" ;
        pTo   = "aaeeeeiiouuaaeeeeiiouu" ;
        self.pTransTable = string.maketrans (pFrom, pTo) ;

    def __init__ (self) :

        self.pVowels = ['a', 'e', 'i', 'o', 'u', 'y', 
                        'â', 'à', 
                        'ë', 'é', 'ê', 'è', 
                        'ï', 'î', 'ô', 'û', 'ù' ] ;
        self.pTransTable = None ;
        self.make_trans_table () ;
