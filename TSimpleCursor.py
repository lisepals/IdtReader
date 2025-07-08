# -*- coding: cp1252 -*-
# ------------------------------------------------------------------------
# Date   : 2017-11-26
# Author : Lise Palacios
# Object : A new TTextCursor class
# ------------------------------------------------------------------------

import os  ;
import sys ;
import re  ;

import LiseUtils as lu ;
# ------------------------------------------------------------------------
# --- My imports
# ------------------------------------------------------------------------

from   LiseUtils import xmsg ;

class TTextCursor (object) :
    # --- Cet classe permet de scanner un fichier texte caractere par
    # --- caractere.
    # --- Il est utilisé dans tous les analyseurs lexicaux

    # --------------------------------------------------------------------
    # * Protected
    # --------------------------------------------------------------------

    # >>> Protected initialization related methods

    def join (self, pStrList) :
        sCh = '' ;
        return sCh.join (pStrList) ;

    def init_internals (self) :
        # --- Initialise les variables privées pour la première ligne
        # --- du fichier.
        self.iLineNo = 0 ;
        self.maxLen   = len (self.pStr) ;
        if self.maxLen > 0 :
            self.index    = 0 ;
            self.curChar  = self.pStr[self.index] ;
        else :
            self.index   = None ;
            self.curChar  = None ;

    def init_cursor (self, pStrList) :
        # --- Initialise le curseur
        if isinstance (pStrList, list) :
            self.pStr = self.join (pStrList) ;
        elif isinstance (pStrList, str) :
            self.pStr = pStrList ;
        else :
            # --- Emit XMmlReader Err 101 :
            #     Cursor must be given a string or a list of strings as
            #     argument.
            sErr  = "  ! TextCursor Err 101 : %s %s" ;
            sMsg1 = "Cursor must be given a string or ";
            sMsg2 = "a list of strings as argument" ;
            lu.xerr (lu.ERFATAL, sErr, sMsg1, sMsg2) ;
        # --- Initialise Cursor
        self.init_internals () ;

    # --------------------------------------------------------------------
    # * Interface
    # --------------------------------------------------------------------

    def getch (self) :
        # --- Retourne le caractère qui est sous le curseur
        try :
            self.curChar = self.pStr[self.index] ;
            if self.curChar == '\n' :
                self.iLineNo += 1;
            self.index += 1 ;
            return self.curChar ;
        except IndexError :
            # --- We have reach the end of string
            return None ;
        except TypeError :
            # --- self.index == None
            return None ;

    def ungetch (self) :
        # --- Recule le curseur d'une position
        if self.index > 0 :
            self.index -= 1 ;
        if self.curChar == '\n' :
            self.iLineNo -= 1;

    def look_ahead (self, iVal) :
        # --- Retourne le caractere qui se trouve à iVal positions
        # --- du curseur.
        iIdx = self.index + iVal ;
        if iIdx < self.maxLen :
            return self.pStr[iIdx] ;
        return None ;

    def line (self) :
        # --- Retourne le numero de ligne
        return self.iLineNo ;

    def string (self) :
        # --- Retourne la chaine en cours d'analyse
        return self.pStr ;
		
    def get_index (self) :
        return self.index ;
		
    # --------------------------------------------------------------------
    # * Initialization
    # --------------------------------------------------------------------

    def __init__ (self, pStrList = None) :
        if pStrList :
            self.init_cursor (pStrList) ;


