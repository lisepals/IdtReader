# ------------------------------------------------------------------------
# Date   : 2017-09-03
# Auteur : Lise Palacios
# Objet  : Initialization by AutoProg
# ------------------------------------------------------------------------

# --------------------------------------------------------------------
## Imports
# ------------------------------------------------------------------------
import sys    ;
import getopt ;
import os ;

# --- My imports
import Mods.TLispExceptions as tlx ;
import Mods.TLogProcessor   as tlp ;

import TextReader.TIdCursor as csr ;

import LiseUtils as lu ;
# ------------------------------------------------------------------------
#   * A TIdTextReader (see html-builder.txt)
#     This class is a finite state automaton
# ------------------------------------------------------------------------
class TIdObject (object) :

    # --------------------------------------------------------------------
    # --- Protected
    # --------------------------------------------------------------------

    # --------------------------------------------------------------------
    # --- Interface
    # --------------------------------------------------------------------
    def get_id (self) :
        return self.sId ;

    def get_text (self) :
        return self.sText ;

    def text (self) :
        return self.sText ;

    # --------------------------------------------------------------------
    # --- special methods
    # --------------------------------------------------------------------

    def __repr__ (self) :
        if len (self.sText) > 30 :
            sStrDeb = self.sText[:13] ;
            sStrFin = self.sText[-13:] ;
            sFmtText= "{0} ... {1}" ;
            sText = sFmtText.format (sStrDeb, sStrFin) ;
        else :
            sText = self.sText ;

        sFmtStr = "<TiObject : Id = {0}, text = {1}>" ;
        return sFmtStr.format (self.sId, sText) ;

    # --------------------------------------------------------------------
    # --- Initialization
    # --------------------------------------------------------------------
    def __init__ (self, sId, sText) :
        self.sId   = sId ;
        self.sText = sText ;

class TIdTextReader (object) :

    # --------------------------------------------------------------------
    # --- Protected
    # --------------------------------------------------------------------
    def open_source (self, sUrl) :
        # --- add the content of a file (as string) to self.pData
        try :
            return open (sUrl, "r", encoding="utf-8") ;
        except IOError :
            # --- Display an error message and quit ignominiously
            sMsg0 = "  ! IOErr1 - Unable to open file %s" ;
            tlp.logmsg (tlp.CRITICAL, sMsg0, sUrl) ;
            raise ;
    
    # === The INIT STATE
    def init_state (self, ch) :
        # --- Test if we have the meta char
        if self.pCursor.is_meta (ch) :
            # --- Fill ch in pKwBuffer
            self.sState = 'S_META_0' ;
            self.iMeta  = 1 ;

    # === The META_i STATES : finding $begin(id) token
    def meta_state_0 (self, ch) :
        # --- Test if we have B or b
        if ch in ['B', 'b'] :
            self.sState = 'S_META_1' ;
        else :
            self.sState = 'S_INIT' ;

    def meta_state_1 (self, ch) :
        # --- Test if we have E or e
        if ch in ['E', 'e'] :
            self.sState = 'S_META_2' ;
        else :
            self.sState = 'S_INIT' ;

    def meta_state_2 (self, ch) :
        # --- Test if we have the meta char
        if ch in ['G', 'g'] :
            self.sState = 'S_META_3' ;
        else :
            self.sState = 'S_INIT' ;

    def meta_state_3 (self, ch) :
        # --- Test if we have the meta char
        if ch in ['I', 'i'] :
            self.sState = 'S_META_4' ;
        else :
            self.sState = 'S_INIT' ;

    def meta_state_4 (self, ch) :
        # --- Test if we have the meta char
        if ch in ['N', 'n'] :
            self.sState = 'S_META_5' ;
            # --- Here 'begin' has been found
            # reset the Keyword Buffer.
        else :
            self.sState = 'S_INIT' ;

    def meta_state_5 (self, ch) :
        # --- Test if we have the meta char
        if self.pCursor.is_opar () :
            self.sState = 'S_ID' ;
        elif self.pCursor.is_space () :
            self.sState = 'S_META_5' ;
        else :
            self.sState = 'S_INIT' ;

    # === Token : $begin(id) found. Save Identifier

    def create_id (self) :
        # --- create the identifier name
        self.pIdReg = ''.join (self.pIdBuf) ;
        
    def meta_state_id (self, ch) :
        # --- Test if we have the meta char
        if self.pCursor.is_id_char () :
            self.pIdBuf.append (self.pCursor.curChar) ;
        elif self.pCursor.is_space () :
            # --- blanks are not significant in 'S_ID' state
            pass ;
        elif self.pCursor.is_cpar () :
            self.create_id () ;
            self.sState = 'S_TEXT' ;
        else :
            self.sState = 'S_INIT' ;

    # === Accumulate characters in a buffer

    def acc_state (self, ch) :
        # --- The accumulate state - Used in text mode
        if ch :
            # --- Test if we have the meta char
            if self.pCursor.is_meta () :
                # --- Fill ch in pKwBuffer
                self.pKwBuf.append (ch) ;
                self.sState = 'S_END_1' ;
            else :
                if ch == '\n' and self.pTextBuf == [] :
                    # --- Ignore NL characters in IDT while buffer is empty.
                    return ;
                if ch == '\\' :
                    ch = self.pCursor.getch () ;
                self.pTextBuf.append (self.pCursor.curChar) ;
        else :
            # --- Unexpected EOF. Can only be in S_INIT state
            self.sState = 'S_ERROR' ;
            self.sErrId = 'SYN_000' ; # Unexpected EOF

    def reset_kw_buf (self) :
        self.pKwBuf = [] ;

    def fill_text_buf (self) :
        # --- Fill the text buffer with the content of the temp. kw buffer
        self.pTextBuf.extend (self.pKwBuf) ;
        self.reset_kw_buf  () ;

    # === Finding the $end token in text

    def state_end_1 (self, ch) :
        # --- Test if we have E or e
        self.pKwBuf.append (ch) ;
        if ch in ['E', 'e'] :
            self.sState = 'S_END_2' ;
        else :
            self.fill_text_buf ()
            self.sState = 'S_TEXT' ;

    def state_end_2 (self, ch) :
        # --- Test if we have the end char
        self.pKwBuf.append (ch) ;
        if ch in ['N', 'n'] :
            self.sState = 'S_END_3' ;
        else :
            self.fill_text_buf () ;
            self.sState = 'S_TEXT' ;

    # === Creation of TIdObject instances

    def create_id_object (self) :
        # --- Cree un TIdObject instance
        # --- sId is in self.pIdReg
        # --- Create the text
        self.pTextReg = ''.join (self.pTextBuf) ;
        # --- reinit the Id buffer
        self.pTextBuf = [] ;
        self.pObjReg = TIdObject (self.pIdReg, self.pTextReg) ;
        # --- reset registers
        self.pIdReg   = None ;
        self.pTextReg = None ;
        self.reset_kw_buf () ;

    def state_end_3 (self, ch) :
        # --- Test if we have the end char
        self.pKwBuf.append (ch) ;
        if ch in ['D', 'd'] :
            self.sState = 'S_END' ;
            self.create_id_object () ;
        else :
            self.fill_text_buf () ;
            self.sState = 'S_TEXT' ;

    def init_registers (self) :
        self.pTextReg = None ;
        self.pIdReg   = None ;
        self.pObjReg  = None ;

    def init_buffers (self) :
        self.pTextBuf = [] ;
        self.pIdBuf   = [] ;
        # --- The temporary keyword buffer
        self.pKwBuf   = [] ;
 
    # --------------------------------------------------------------------
    # --- Interface
    # --------------------------------------------------------------------
    def get_obj (self) :
        self.sState = 'S_INIT' ;
        # --- Initialize the registers and buffers of the virtual machine
        self.init_registers () ;
        self.init_buffers () ;
        # --- Init loop
        ch = self.pCursor.getch () ;
        while ch != None and self.sState != 'S_END' :
            if self.sState == 'S_INIT' :
                self.init_state (ch) ;
            elif self.sState == 'S_META' :
                self.meta_state (ch) ;
            elif self.sState == 'S_TEXT' :
                self.acc_state (ch) ;
            elif self.sState == 'S_META_0' :
                self.meta_state_0 (ch) ;
            elif self.sState == 'S_META_1' :
                self.meta_state_1 (ch) ;
            elif self.sState == 'S_META_2' :
                self.meta_state_2 (ch) ;
            elif self.sState == 'S_META_3' :
                self.meta_state_3 (ch) ;
            elif self.sState == 'S_META_4' :
                self.meta_state_4 (ch) ;
            elif self.sState == 'S_META_5' :
                self.meta_state_5 (ch) ;
            elif self.sState == 'S_ID' :
                self.meta_state_id (ch) ;
            elif self.sState == 'S_END_1' :
                self.state_end_1 (ch) ;
            elif self.sState == 'S_END_2' :
                self.state_end_2 (ch) ;
            elif self.sState == 'S_END_3' :
                self.state_end_3 (ch) ;
            elif self.sState == 'S_END' :
                self.state_end (ch) ;
            else :
                # --- Display an error message and quit ignominiously
                sMsg0 = f"  ! RdErr00 - get_obj : bad state in FSA {self.sState}" ;
                tlp.logmsg (tlp.CRITICAL, sMsg0) ;
                raise tlx.LispError (sMsg0, self.sState) ;
            # --- Advance to next char
            if self.sState != 'S_END' :
                ch = self.pCursor.getch () ;
        return self.pObjReg ;

    def create_id_table (self) :
        bCont = True ;
        while bCont :
            pObj = self.get_obj () ;
            if pObj :
                self.pIdObjTable[pObj.get_id()] = pObj ;
            else :
                bCont = False ;

    def text (self, sKey) :
        try :
            return self.pIdObjTable[sKey].get_text () ;
        except KeyError :
            return "-" ;

    def write_idt (self, hFile, sKey) :
        """
        Object :
        Write an IdT to hfile
        """
        sIdtTmpl = "$Begin({0})\n{1}\n$End\n\n" ;
        hFile.write (sIdtTmpl.format (sKey,
                                      self.pIdObjTable[sKey].text ())) ;
        
    def save (self, sPath) :
        """
        Object : Save the reader to the file specified by sPath
        """
        try :
            hFile = open (sPath, "w") ;
            pListKeys = list (self.pIdObjTable.keys()) ;
            for sKey in pListKeys :
                self.write_idt (hFile, sKey) ;
            close (hFile) ;
        except IOError :
            eMsg = "Unable to open file {0}"
            raise txc.TPyLispError (101, eMsg.format (spath)) ;

    def keys (self) :
        """
        Object : Return the keys of self.pIdObjTable as a list
        """
        return list (self.pIdObjTable.keys ()) 
    # --------------------------------------------------------------------
    # --- Special methods
    # --------------------------------------------------------------------

    def __getitem__ (self, sKey) :
        try :
            return self.pIdObjTable[sKey] ;
        except KeyError :
            return "-" ;

    def __setitem__ (self, sKey, sVal) :
        """
        *** Object :
        Insert a new text Id into self.pIdObjTable
        """
        self.pIdObjTable[sKey] = TIdObject (sKey, sVal) ;
        
    def __iter__ (self) :
        # -- input :
        # --    None 
        # -- Implementation of the iter operator []
        # -- Output :
        # --    An interator upon self.list
        return self.pIdObjTable.iteritems() ;

    def iterkeys (self) :
        # -- input :
        # --    None 
        # -- Implementation of the iter operator []
        # -- Output :
        # --    An interator upon self.pIdObjTable.keys 
        return iter (self.pIdObjTable.keys()) ;


    def itervalues (self) :
        # -- input :
        # --    None 
        # -- Implementation of the iter operator []
        # -- Output :
        # --    An interator upon self.pIdObjTable.keys 
        return iter (self.pIdObjTable.values()) ;
    # --------------------------------------------------------------------
    # --- Initialization
    # --------------------------------------------------------------------

    def __init__ (self, sFileName=None) :
        # --- Create the Id Table
        self.pIdObjTable = {} ;
        if sFileName != None :
            self.sFileName = sFileName ;
            self.hInput = self.open_source (sFileName) ;
            # --- Create the cursor
            self.pCursor = csr.TCursor (self.hInput) ;
            # --- The registers of the virtual machine
            self.init_registers () ;
            # --- The buffers to accumulate chars
            self.init_buffers () ;
            # --- Create the IdTable
            self.create_id_table () ;

