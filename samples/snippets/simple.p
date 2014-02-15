Program SimpleTest;

Type
   T_UINT8 = 0..255;
   T_UINT4 = 0..15;
   T_SINT8 = -128..127;
 
Var
   u8 : T_UINT8;
   u4 : T_UINT4;
   s8 : T_SINT8;
   i  : Integer;
Begin
   u8 := 0;
   u4 := 10;
   s8 := u4;
   s8 := -u4;

   if (s8 = -10) and (s8 < 0) then
      writeln('OK')
   else
      halt(1);
End.