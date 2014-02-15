program VariantTest;

Type
   T_UINT8  = 0..255;
   T_UINT16 = 0..65535;
   T_SINT8  = -128..127;
   T_BSET8  = set of (BIT0, BIT1, BIT2, BIT3, BIT4, BIT5, BIT6, BIT7);
   T_BYTE8  = record case integer of
		 1 : (UINT : T_UINT8);
	         2 : (SINT : T_SINT8);
	         3 : (BSET : T_BSET8);
	     end; { case }
   T_WORD16 = record
		 id : integer;
		 case integer of
		   1 : (UINT : T_UINT16);
		   2 : (SINT : T_UINT16);
		   3 : (LO,HI : T_UINT8);
		 end; { case }
   T_TEST   = record
		 case rcastt : boolean of
		   true	 : ();
		   false : ();
		 end; { case }
Var
   b : T_BYTE8;
   v : T_BYTE8;
   w : T_WORD16;
   t : T_TEST;
   
Procedure Assert(value, expected: Boolean);
Begin
   If value = expected Then
      Writeln('OK')
   Else
      Halt(1);
End; { Assert }


Procedure ArrayTest;
Var
   input, output : T_BSET8;
   bitstore	 : Array[0..1] of T_BYTE8;
   i, j, n	 : integer;
Begin

   bitstore[0].uint := 0;
   bitstore[1].uint := 0;

   for i := 0 to 1 do begin
      n := i;
      for j := 0 to 1 do begin
	 output := bitstore[n].bset * input;
      end;
   end;
   
End; { ArrayTest }


Begin
   v.bset := [BIT0, BIT1, BIT2, BIT3, BIT4, BIT5, BIT6, BIT7];

   Assert(v.sint = -1, True);
   Assert(v.uint = 255, True);

   v.bset := [BIT7];

   Assert(v.sint = -128, True);
   Assert(v.uint = 128, True);

   w.uint := 256;
   Assert(w.lo = 0, True);
   Assert(w.hi = 1, True);

   w.lo := 44;
   Assert(w.uint = 300, True);

   w.hi := 2;
   Assert(w.uint = 556, True);
  
   with w do
   begin
      uint := 256;
      lo := 44;
      Assert(uint = 300, True);

      hi := 2;
      Assert(uint = 556, True);
   end;
End.
