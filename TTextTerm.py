# -*- coding: cp1252 -*-
# ------------------------------------------------------------------------
# Date   : 2017-12-30
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
#   * A text term is an abstraction of a set of lexems sharing the same
#     stem.
# ========================================================================

class TTextTerm (object) :

    # --------------------------------------------------------------------
    # * Protected
    # --------------------------------------------------------------------

    # --------------------------------------------------------------------
    # * Interface
    # --------------------------------------------------------------------

    def comp_tfidf (self, fIdf) :
        self.fIdf = fIdf ;
        self.fTfIdf = self.fTfd * fIdf ;

    def comp_tfd (self, fNbTerms) :
        # --- Compute the frequency of term in this document
        # * Args :
        #   . fNbTerms (float) : nb of terms in document
        # * RetV :
        #   . None
        self.fTfd = float (len (self.pLexems)) / fNbTerms ;

    def tfd (self) :
        return self.fTfd () ;

    def tfidf (self) :
        return self.fTfIdf ;

    def add (self, pLxm) :
        # --- Add a lexem to this term.
        self.pLexems.append (pLxm) ;

    def save_num_data (self, hBase) :
        sFmtStr  = "<{0}>\n{1:6.3f}\n</{0}>\n" ;
        hBase.write (sFmtStr.format ('Tfd',   self.fTfd)) ;
        hBase.write (sFmtStr.format ('Idf',   self.fIdf)) ;
        hBase.write (sFmtStr.format ('TfIdf', self.fTfIdf)) ;

    def save_stem_data (self, hBase) :
        sFmtStr  = "<{0}>\n{1}\n</{0}>\n" ;
        hBase.write (sFmtStr.format ('Stem',  self.sStem)) ;

    def save_lexems (self, hBase) :
        sTag = 'LexList' ;
        sFmtDeb  = "<{0}>\n"
        sFmtEnd  = "</{0}>\n"
        hBase.write (sFmtDeb.format (sTag)) ;
        for pLxm in self.pLexems :
            pLxm.save_as_xml (hBase) ;
        hBase.write (sFmtEnd.format (sTag)) ;

    def save_as_xml (self, hBase) :
        sTag = 'Term' ;
        sFmtDeb  = "<{0}>\n"
        sFmtEnd  = "</{0}>\n"
        hBase.write (sFmtDeb.format (sTag)) ;
        # --- Save the numerical data
        self.save_num_data (hBase) ;
        # --- Save the stem data of term
        self.save_stem_data (hBase) ;
        # --- Save the lexems
        self.save_lexems (hBase) ;
        hBase.write (sFmtEnd.format (sTag)) ;

    # --------------------------------------------------------------------
    # * Special methods
    # --------------------------------------------------------------------

    def __repr__ (self) :
        # --- Representation of Terms (a set of lexems)
        pStrList = ["  * Stem = %s" % self.sStem] ;
        pStrList.append ("    + Tfd   = %6.3f" % self.fTfd) ;
        pStrList.append ("    + Idf   = %6.3f" % self.fIdf) ;
        pStrList.append ("    + TfIdf = %6.3f" % self.fTfIdf) ;
        sSep = '\n' ;
        return sSep.join (pStrList) ;

    # --------------------------------------------------------------------
    # * Initialization
    # --------------------------------------------------------------------

    def __init__ (self, pLxm) :
        self.pLexems = [pLxm] ;
        # --- Term frequency in document
        self.fTfd = 0.0 ;
        # --- Inverse document frequency of term
        self.fIdf = 0.0 ;
        # --- Global Term frequency times inverse document frequency of term
        self.fTfIdf = 0.0 ;
        # --- The stem
        self.sStem = pLxm.stem () ;
