# -*- coding: cp1252 -*-
# ----------------------------------------------------------------------
# Date      : 2017-09-03
# Origine   : Lise Palacios
# Objet     : TCursor object
# ----------------------------------------------------------------------
# See also  : Artificial Intelligence - A modern approach
# ----------------------------------------------------------------------

# --- Module imports
import sys    ;
import os     ;
# ------------------------------------------------------------------------
# --- My imports
# ------------------------------------------------------------------------
import LiseUtils as lu ;

from LiseUtils import dmsg, derr, atof, atoi ;
# ------------------------------------------------------------------------
# --- Processing
# ------------------------------------------------------------------------

class TCursor (object) :

    def is_meta (self, ch=None) :
        if ch == None :
            ch = self.curChar ;
        return ch == '$' ;

    def is_opar (self, ch=None) :
        if ch == None :
            ch = self.curChar ;
        return ch == '(' ;

    def is_cpar (self, ch=None) :
        if ch == None :
            ch = self.curChar ;
        return ch == ')' ;

    def is_letter (self, ch=None) :
        if ch == None :
            ch = self.curChar ;
        return ch.isalpha () ;

    def is_digit  (self, ch=None) :
        if ch == None :
            ch = self.curChar ;
        return ch.isdigit () ;

    def is_ascii (self, ch=None) :
        if ch == None :
            ch = self.curChar ;
        return ord(ch) >= 32 and ord(ch) < 127 ;

    def is_id_char (self, ch=None) :
        if ch == None :
            ch = self.curChar ;
        return self.is_letter (ch) or self.is_digit (ch) or self.curChar in self.pSpecChars ;
    
    def is_space (self, ch=None) :
        if ch == None :
            ch = self.curChar ;
        return ch.isspace () ;

    def set_cursor (self, pStr) :
            self.pStr = pStr ;
            self.maxLen = len (pStr) - 1 ;
            self.index  = -1 ;
            self.curChar = None ;


    def look_ahead (self, iVal) :
        iIdx = self.index + iVal ;
        if iIdx < self.maxLen :
            return self.pStr[iIdx] ;
        return None ;

    def is_sign (self) :
        pPlusMoins = ['+', '-'] ;
        chNext = self.look_ahead (1) ;

        return self.curChar in pPlusMoins and chNext.isdigit () ;

    def is_minus (self) :
        return self.curChar == '-' ;

    # --------------------------------------------------------------------
    # --- Interface
    # --------------------------------------------------------------------

    def getch (self) :
        try :
            self.index += 1 ;
            self.curChar = self.pStr[self.index] ;
        except IndexError :
            self.pStr = self.hFile.readline () ;
            if self.pStr :
                self.iLineNo += 1 ;
                self.index   = 0 ;
                self.curChar = self.pStr[self.index] ;
            else :
                self.curChar = None ;
        return (self.curChar) ;

    def ungetch (self) :
        self.index -= 1 ;
        self.curChar = self.pStr[self.index] ;

    # --------------------------------------------------------------------
    # --- Initialization
    # --------------------------------------------------------------------

    def __init__ (self, hFile) :
        self.hFile = hFile ;
        self.pStr  = hFile.readline () ;
        self.index   = -1 ;
        self.curChar = None ;
        self.iLineNo = 1 ;
        self.pSpecChars = ['_', '-', '*', '='] ; 
    

