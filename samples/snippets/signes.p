program SignTest;

Type
   T_SINT8  = -128..127;
   T_SINT16 = integer;
Var
   s8  : T_SINT8;
   s16 : T_SINT16;

$include (assert.inc)
   
Begin
   s8 := -1;
$if XTEST
   Halt(1);
$else
   WriteLn('OK');
$endif
   s16 := s8;

   Assert(s16 = -1, True);
End.
