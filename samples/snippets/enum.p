Program EnumTest;

Type
   T_NUMBER = (ONE, TWO, THREE, FOUR, FIVE);
Var
   num : T_NUMBER;
   
Procedure Assert(value, expected : T_NUMBER);
Begin
   If value = expected Then
      Writeln('OK')
   Else
      Halt(1);
End; { Assert }

Begin
   num := ONE;
   Assert(num, ONE);
   Assert(num, T_NUMBER(0));
End.