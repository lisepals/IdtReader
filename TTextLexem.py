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
import TStem          as tsm ;

from LiseUtils import xmsg, xerr, dmsg ;
# ------------------------------------------------------------------------
#   * Three tightly coupled classes
# ------------------------------------------------------------------------

# ========================================================================
#   * A text lexem
# ========================================================================

class TTextLexem (object) :

    # --------------------------------------------------------------------
    # * Protected
    # --------------------------------------------------------------------
    def is_num (self) :
        pDigits = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'] ;
        for sCh in self.sLower :
            if not sCh in pDigits :
                return False ;
        return True ;

    def is_date (self) :
        if self.iLen > 10 or self.iLen < 7 :
            return False ;
        pPat = re.compile ('[0-9]*[0-9]/[0-9]{2}/20[0-9]{2}', re.I) ;
        if pPat.match (self.sLower) :
            return True ;
        pPat1 = re.compile ('[0-9]*[0-9]/[01]*[0-9]/[012][0-9]', re.I) ;
        if pPat1.match (self.sLower) :
            return True ;
        return False ;

    def is_abbrev_date (self) :
        if self.iLen > 5 :
            return False ;
        pPat = re.compile ('[0123]*[0-9]/[01]*[0-9]', re.I) ;
        if pPat.match (self.sLower) :
            return True ;
        return False ;

    def is_rf (self) :
        if self.iLen < 7 or self.iLen > 10 :
            return False ;
        pPat = re.compile ('[0-9]*[A-Z]{3}[0-9]+[A-Z]{2}', re.I) ;
        if pPat.match (self.sLower) :
            return True ;
        return False ;

    def is_hour (self) :
        if self.iLen > 5 :
            return False ;
        pPat = re.compile ('[0-9]*[0-9]+[h:][0-9]{2}', re.I) ;
        if pPat.match (self.sLower) :
            return True ;
        return False ;

    def is_appword (self) :
        pAppList = ['t', 'd', 'l', 's', 'n', 'c', 
                    'qu', 
                    'jusqu', 'presqu', 'puisqu', 'lorsqu', 'aujourd'] ;
        if self.sLower in pAppList :
            return True ;
        return False ;

    def is_special (self) :
        pSpecials = set(['0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
                         '-', '_', '/']) ;
        s0 = self.sLower[0] ;
        if s0 in pSpecials :
            return True ;
        return False ;

    def comp_stem (self) :
        # --- Compute the stem of sLower
        pStemmer = tsm.TFrenchStemmer () ;
        self.sStem = pStemmer.stem (self.sLower) ;

    # --------------------------------------------------------------------
    # * Interface
    # --------------------------------------------------------------------
    def type (self) :
        return self.sType ;

    def body (self) :
        return self.sString ;

    def lower (self) :
        return self.sLower ;

    def stem (self) :
        if self.sStem :
            return self.sStem ;
        return self.sString ;

    def set_type (self, sNewType) :
        self.sType = sNewType ;

    def set_stem (self, sStr) :
        self.sStem = sStr ;

    def set_tfd (self, fVal) :
        self.fTfd = fVal ;

    def set_tfidf (self, fIdf) :
        self.fTfiTf = self.fTfd * fIdf ;

    def an_tword (self) :
        # --- Analyze a TLexem instance and transform it into a syntagme
        if self.is_num () :
            self.sType = 'TNUM' ;
        elif self.is_date () or self.is_abbrev_date () :
            self.sType = 'TDATE' ;
        elif self.is_rf () :
            self.sType = 'TRF' ;
        elif self.is_hour () :
            self.sType = 'THOUR' ;
        elif self.is_appword () :
            self.sType = 'TAPPWORD' ;
        elif self.is_special () :
            self.sType = 'TSPECIAL' ;
        else :
            self.sType = 'TWORD' ;
            # --- We compute the stem only if we have a TWORD lexem
            self.comp_stem () ;

    def an_space (self) :
        # --- Mark new lines chars as TNL lexems
        if self.sString[0] == '\n' :
            self.sType = 'TNL' ;
        else :
            self.sType = 'TSPACE' ;

    def an_punct (self) :
        if self.sString == "'" :
            self.sType = 'TAP' ;
        else :
            self.sType = 'TPUNC' ;

    def save_as_xml (self, hBase) :
        sFmtStr  = "<{0}>\n{1}\n</{0}>\n" ;
        sTag = 'Lexem' ;
        sFmtDeb  = "<{0}>\n"
        sFmtEnd  = "</{0}>\n"
        hBase.write (sFmtDeb.format (sTag)) ;
        hBase.write (sFmtStr.format ('Post',  self.sType)) ;
        hBase.write (sFmtStr.format ('Body',  self.sString)) ;
        hBase.write (sFmtStr.format ('Lower',  self.sLower)) ;
        hBase.write (sFmtEnd.format (sTag)) ;

    # --------------------------------------------------------------------
    # * Special methods
    # --------------------------------------------------------------------
    def __repr__ (self) :
        # --- A representation of myself
        if self.sType not in ['TNL', 'TPARG', 'TPUNC'] :
            sFmt = "  + TLexem - type : %s, body : %s, lower : %s, stem : %s" ;
            return sFmt % (self.sType, self.sString, self.sLower, self.sStem ) ;
        elif self.sType == 'TPUNC' :
            sFmt1 = "  . Lexem - Type : %-10s, body : %s" ;
            return sFmt1 % (self.sType, self.sString) ;
        else :
            sFmt1 = "  . Lexem - Type : %-10s" ;
            return sFmt1 % (self.sType) ;
    
    def __len__ (self) :
        return self.iLen ;
    # --------------------------------------------------------------------
    # * Initialization
    # --------------------------------------------------------------------

    def __init__ (self, sLexType, sLexString, iLen) :
        self.sString = sLexString ;
        self.iLen    = iLen ;
        # --- A lot of further analysis will be done upon lower.
        self.sLower  = sLexString.lower () ;
        # --- The stem of the word
        self.sStem   = None ;

        if sLexType == 'TWORD' :
            self.an_tword () ;
        elif sLexType == 'PUNCT' :
            self.an_punct () ;
        elif sLexType == 'SPACE' :
            self.an_space () ;
        else :
            self.sType = sLexType ;
