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
import os  ;

# --- My imports
import LiseUtils     as lu ;
import TTable        as tt ;
import TRecord       as tr ;
import TLogProcessor as tlp ;

import TTextCursor   as txc ;

from LiseUtils import xmsg, xerr, dmsg ;
# ------------------------------------------------------------------------

# ========================================================================
#   * A TTextLexem Analyzer.
# ------------------------------------------------------------------------
#     This class allows to analyze a single lexem. A more comprehensive
#     analysis (involving multiples lexems) is performed by the 
#     TTextReader class
# ========================================================================

class TTextLexemAnalyzer (object) :

    # --------------------------------------------------------------------
    # * Protected
    # --------------------------------------------------------------------
    def is_sitetr (self, pLexem) :
        if len(pLexem) == 4 :
            sSite = pLexem.body().upper()[:3] ;
            return sSite in self.pSites ;
        return False ;

    def test_plural (self, pLexem) :
        sLastLetter = pLexem.body()[-1] ;
        if sLastLetter in ['s', 'x'] :
            pLexem.set_type ('TNNP') ;
        else :
            pLexem.set_type ('TNN') ;

    def is_aux (self, sTerm, pLexem) :
        if sTerm in ['est', 'sont', 'était', 'étaient', 'été'] :
            pLexem.set_type ('TAUXET') ;
            return True ;
        if sTerm in ['ont', 'avait', 'avaient', 'eu'] :
            pLexem.set_type ('TAUXAV') ;
            return True ;
        return False ;

    def is_prep (self, sTerm, pLexem) :
        if sTerm in self.pPreps :
            #lu.dmsg ("  > %-15s, %-7s, %3d", 
            #         pLexem.body(), pLexem.type(), len(pLexem)) ;
            pLexem.set_type ('TPREP') ;
            return True ;
        return False ;

    def is_conjunction (self, sTerm, pLexem) :
        if sTerm in self.pConjs :
            #lu.dmsg ("  > %-15s, %-7s, %3d", 
            #         pLexem.body(), pLexem.type(), len(pLexem)) ;
            pLexem.set_type ('TCONJ') ;
            return True ;
        return False ;
    # --------------------------------------------------------------------
    # * Interface
    # --------------------------------------------------------------------
    def analyze (self, pLexem) :
        sStr = pLexem.lower () ;
        if len(pLexem) == 1 :
            if sStr == 'a' :
                pLexem.set_type ('TAUXAV') ;
                return ;
        if len(pLexem) < 4 and len(pLexem) > 1 :
            if len(pLexem) == 2 :
                if sStr in self.pBgs :
                    pLexem.set_type ('TBG') ;
                    return ;
            if len (pLexem) == 3 :
                if sStr in self.pTgs :
                    pLexem.set_type ('TTG') ;
                    return ;
        if self.is_sitetr (pLexem) :
            pLexem.set_type ('TSITR') ;
            return ;
        if sStr in self.pDets :
            pLexem.set_type ('TDET') ;
            return ;
        if sStr in self.pPronouns :
            pLexem.set_type ('TPP') ;
            return ;
        if self.is_prep (sStr, pLexem) :
            pLexem.set_type ('TPREP') ;
            return ;
        if self.is_conjunction (sStr, pLexem) :
            pLexem.set_type ('TCONJ') ;
            return ;
        if self.is_prep (sStr, pLexem) :
            return ;
        if sStr in self.pAdverbs :
            pLexem.set_type ('TADV') ;
            return ;
        if sStr in self.pVerbs :
            pLexem.set_type ('TVERB') ;
            return ;
        if sStr in self.pAdjs :
            pLexem.set_type ('TADJ') ;
            return ;
        if self.is_aux (sStr, pLexem) :
            return ;
        return self.test_plural (pLexem) ;
        
    # --------------------------------------------------------------------
    # * Initialization
    # --------------------------------------------------------------------

    def set_from_csv_table (self, sName, iColNo) :
        # --- Loads a simple csv table and transforms it into a set
        # Args :
        #    . sPath(str) : the path (except the volume)
        #    . sName(str) : the file name.
        #    . iColNo(int): the column nulber to extract
        # RetV :
        #    . pSet(set)  : the set
        # --- Get file name
        sFileName = lu.mk_url (self.sKbaseRep, sName) ;
        # --- Open file
        hIf    = lu.open_file (sFileName, "r") ;
        # --- The lines
        pSet = set() ;
        for i, sLine in enumerate (hIf.readlines ()) :
            if i > 0 :
                pRec = sLine.split (';') ;
                try :
                    pSet.add (pRec[iColNo].strip().lower()) ;
                except IndexError :
                    sMsg1 = "Bad column number (%d) specified in set_from_csv_table" ;
                    lu.xerr (lu.ERFATAL, sMsg1, iColNo) ;
        return pSet ;

    def load_bigrams (self) :
        # --- Get file name
        sFileName = "bigrams.csv" ;
        self.pBgs = self.set_from_csv_table (sFileName, 0) ;
        tlp.ixmsg (6, 65, "+ Bigrams loaded.") ;

    def load_trigrams (self) :
        # --- Get file name
        sFileName = "trigrams.csv" ;
        self.pTgs = self.set_from_csv_table (sFileName, 0) ;
        tlp.ixmsg (6, 65, "+ Trigrams loaded.") ;

    def load_simple_table (self, sName) :
        # --- Loads a text file, one word per line and transforms it into
        #     a set.
        # Args :
        #    . sPath(str) : the path (except the volume)
        #    . sName(str) : the file name.
        # RetV :
        #    . pSet(set)  : the set
        # --- Get file name
        sPath = self.sKbaseRep ;
        sFileName = lu.mk_url (sPath, sName) ;
        # --- Open file
        hIf    = lu.open_file (sFileName, "r") ;
        # --- The lines
        pSet = set() ;
        for sLine in hIf.readlines () :
            pSet.add (sLine.strip().lower()) ;
        return pSet ;

    def load_adverbs (self) :
        # --- Loads the list of french adverbs
        sFileName = "adverbs.csv" ;
        self.pAdverbs = self.load_simple_table (sFileName) ;
        tlp.ixmsg (6, 65, "+ Adverbs loaded.") ;

    def load_verbs (self) :
        # --- Loads the list of french verbs
        sFileName = "verbs.csv" ;
        self.pVerbs = self.load_simple_table (sFileName) ;
        tlp.ixmsg (6, 65, "+ Verbs loaded.") ;

    def load_adjectives (self) :
        # --- Loads the list of french adjectives
        sFileName = "adjectifs.csv" ;
        self.pAdjs = self.load_simple_table (sFileName) ;
        tlp.ixmsg (6, 65, "+ Adjectives loaded.") ;

    def load_dets (self) :
        # --- Loads the list of french 
        sFileName = "dets.csv" ;
        self.pDets = self.load_simple_table (sFileName) ;
        tlp.ixmsg (6, 65, "+ Dets loaded.") ;

    def load_abbrevs (self) :
        pass ;

    def load_sites (self) :
        self.pSites = set (["BUG", "FES",
                            "BLA", "CHB", "CRU", "DAM", "GRA", "SLB", "TRI",
                            "FLA", "PAL", "SAL",
                            "BEL", "CAT", "GOL", "NOG", "PEN",
                            "CIV", "CHO"]) ;

    def load_preps (self) :
        self.pPreps = set (["à", "À", "avant", "après", "avec", "chez", 
                            "contre", "dans", "de", "depuis", "derrière", 
                            "devant", "durant", "en", "jusque", "par", 
                            "parmi", "pendant", "pour", "sans", "sur"]) ;

    def load_pronouns (self) :
        self.pPronouns = set (["je", "tu", "il", 
                               "nous", "vous", "ils",
                               "elle", "elles", "lequel", "laquelle"]) ;

    def load_conjunctions (self) :
        self.pConjs = set (["mais", "ou", "et", 
                            "donc", "or", "ni",
                            "car"]) ;

    def build_sets (self) :
        self.load_bigrams () ;
        self.load_trigrams () ;
        self.load_adverbs () ;
        self.load_verbs () ;
        self.load_adjectives () ;
        self.load_dets () ;
        # --- Special sets
        self.load_sites () ;
        self.load_preps () ;
        self.load_pronouns () ;
        self.load_conjunctions () ;

    def det_os (self) :
        # --- determine the current os
        sCwd = os.getcwd () ;
        # --- lu.ixmsg (6, 80, ". Current working directory : %s", sCwd) ;
        if os.name == 'posix' :
            if sCwd.find ('lise') < 0 :
                sKbaseRep = "/media/d09114/HDD_EXT/Pymods/TextReader/Ress" ;
            else :
                sKbaseRep = "/usr/local/python/TextReader/Ress" ;
        else :
            sKbaseRep = "D:/Pymods/TextReader/Ress" ;
        return sKbaseRep ;

    def __init__ (self) :
        # --- determines os and sets the attribute self.sVolume
        self.sKbaseRep = self.det_os () ;
        # --- declaration de l'ensemble des trigrammes
        self.pTgs     = None ;
        # --- Declaration de l'ensemble des bigrammes
        self.pBgs     = None ;
        # --- Declaration de l'ensemble des abbreviations
        self.pAbbrevs = None ;
        # --- Declaration de l'ensemble des verbes
        self.pVerbs   = None ;
        # --- Declaration de l'ensemble des adverbes
        self.pAdverbs = None ;
        # --- Declaration de l'ensemble des adjectifs
        self.pAdjs    = None ;
        # --- Declaration de l'ensemble des determinants, pronoms
        self.pDets    = None ;
        # --- Load files and build sets
        self.build_sets () ;

